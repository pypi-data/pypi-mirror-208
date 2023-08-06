import pandas as pd
import codecs
import pickle
import numpy as np
import time
from retrying import retry
from quantplay.utils.constant import Constants, timeit
from quantplay.exception.exceptions import InvalidArgumentException
from quantplay.broker.generics.broker import Broker
from quantplay.config.qplay_config import QplayConfig
from kiteconnect import KiteConnect
import traceback
from quantplay.broker.kite_utils import KiteUtils
import math
from quantplay.utils.number_utils import NumberUtils
import random
from kiteconnect import KiteTicker
from quantplay.exception.exceptions import InvalidArgumentException
from quantplay.utils.pickle_utils import PickleUtils


class Zerodha(Broker):
    stoploss = 'stoploss'
    zerodha_api_key = "zerodha_api_key"
    zerodha_api_secret = "zerodha_api_secret"
    zerodha_wrapper = "zerodha_wrapper"

    @timeit(MetricName="Zerodha:__init__")
    def __init__(self, wrapper=None, user_id=None, api_key=None, api_secret=None, password=None, totp=None):
        try:
            if wrapper:
                self.set_wrapper(wrapper)
            else:
                self.generate_token(user_id, api_key, api_secret, password, totp)
        except Exception as e:
            raise e

        try:
            self.wrapper.orders()
        except Exception as e:
            raise InvalidArgumentException("Zerodha client generation failed due to invalid arguments")

        Constants.logger.info(self.wrapper.profile())

        self.initialize_symbol_data()
        super(Zerodha, self).__init__()

    def set_wrapper(self, serialized_wrapper):
        self.wrapper = pickle.loads(codecs.decode(serialized_wrapper.encode(), "base64"))

    def initialize_symbol_data(self):
        try:
            self.symbol_data = PickleUtils.load_data("zerodha_instruments")
            Constants.logger.info("[LOADING_INSTRUMENTS] loading data from cache")
        except Exception as e:
            instruments = self.wrapper.instruments()
            self.symbol_data = {}
            for instrument in instruments:
                exchange = instrument['exchange']
                tradingsymbol = instrument['tradingsymbol']
                self.symbol_data["{}:{}".format(exchange, tradingsymbol)] = instrument

            PickleUtils.save_data(self.symbol_data, "zerodha_instruments")
            Constants.logger.info("[LOADING_INSTRUMENTS] loading data from server")

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

    def on_ticks(self, kws, ticks):
        """Callback on live ticks"""
        # logger.info("[TEST_TICK] {}".format(ticks))
        pass

    def on_order_update(self, kws, data):
        """Callback on order update"""
        Constants.logger.info("[UPDATE_RECEIVED] {}".format(data))
        self.order_updates.put(data)

    def on_connect(self, kws, response):
        """Callback on successfull connect"""
        kws.subscribe([256265])
        kws.set_mode(kws.MODE_FULL, [256265])

    def stream_order_data(self):
        kite_ticker = KiteTicker(self.wrapper.api_key, self.wrapper.access_token)
        kite_ticker.on_order_update = self.on_order_update
        kite_ticker.on_ticks = self.on_ticks
        kite_ticker.on_connect = self.on_connect

        kite_ticker.connect(threaded=True)

    @retry(wait_exponential_multiplier=3000, wait_exponential_max=10000, stop_max_attempt_number=3)
    @timeit(MetricName="Zerodha:get_ltps")
    def get_ltps(self, trading_symbols):
        response = self.wrapper.ltp(trading_symbols)
        return response

    @retry(wait_exponential_multiplier=3000, wait_exponential_max=10000, stop_max_attempt_number=3)
    def get_ltp(self, exchange=None, tradingsymbol=None):
        try:
            key = "{}:".format(exchange) + tradingsymbol
            response = self.wrapper.ltp([key])

            if key not in response:
                raise InvalidArgumentException("Symbol {} not listed on exchange".format(tradingsymbol))

            response = response[key]['last_price']
            return response
        except Exception as e:
            exception_message = "GetLtp call failed for [{}] with error [{}]".format(tradingsymbol, str(e))
            Constants.logger.error("{}".format(exception_message))

    @retry(wait_exponential_multiplier=3000, wait_exponential_max=10000, stop_max_attempt_number=3)
    def get_orders(self, status=None):
        orders = self.wrapper.orders()
        if status:
            orders = [a for a in orders if a['status'] == status]
        return orders

    def exit_all_trigger_orders(self, tag="ALL", symbol_contains=None):
        stoploss_orders = self.get_orders("TRIGGER PENDING")

        if len(stoploss_orders) == 0:
            Constants.logger.info("All stoploss orders have been already closed")
            return

        stoploss_orders = pd.DataFrame(stoploss_orders)
        if tag != "ALL":
            stoploss_orders = stoploss_orders[stoploss_orders.tag == tag]

        if symbol_contains is not None:
            stoploss_orders = stoploss_orders[stoploss_orders['tradingsymbol'].str.contains(symbol_contains)]

        if len(stoploss_orders) == 0:
            Constants.logger.info("All stoploss orders have been already closed")
            return

        orders_to_close = list(stoploss_orders.order_id.unique())

        stoploss_orders = stoploss_orders.to_dict('records')
        for stoploss_order in stoploss_orders:
            exchange = stoploss_order['exchange']
            tradingsymbol = stoploss_order['tradingsymbol']

            if exchange == "NFO":
                stoploss_order['order_type'] = "MARKET"
                stoploss_order['price'] = 0
            else:
                ltp = self.get_ltp(exchange, tradingsymbol)
                stoploss_order['order_type'] = "LIMIT"
                stoploss_order['price'] = self.round_to_tick(ltp)

            self.modify_order(stoploss_order)
            time.sleep(.1)

        self.modify_orders_till_complete(orders_to_close)
        Constants.logger.info("All order have been closed successfully")

    @retry(wait_exponential_multiplier=3000, wait_exponential_max=10000, stop_max_attempt_number=3)
    def modify_order(self, data):
        try:
            Constants.logger.info("Modifying order [{}] new price [{}]".format(data['order_id'], data['price']))
            response = self.wrapper.modify_order(order_id=data['order_id'],
                                                 variety=data['variety'],
                                                 price=data['price'],
                                                 trigger_price=data['trigger_price'],
                                                 order_type=data['order_type'])
            return response
        except Exception as e:
            exception_message = "OrderModificationFailed for {} failed with exception {}".format(data['order_id'], e)
            Constants.logger.error("{}".format(exception_message))

    def modify_price(self, order_id, price, trigger_price=None, order_type=None):
        data = {}

        data['order_id'] = order_id
        data['price'] = price
        data['order_type'] = order_type
        data['variety'] = 'regular'
        data['trigger_price'] = trigger_price

        self.modify_order(data)

    def cancel_order(self, order_id, variety='regular'):
        self.wrapper.cancel_order(order_id=order_id, variety=variety)

    def get_ltp_by_order(self, order):
        exchange = order['exchange']
        tradingsymbol = order['tradingsymbol']

        return self.get_ltp(exchange, tradingsymbol)

    def modify_orders_till_complete(self, orders_placed, sleep_time=10):
        modification_count = {}
        while 1:
            time.sleep(sleep_time)
            orders = pd.DataFrame(self.get_orders())

            orders = orders[orders.order_id.isin(orders_placed)]
            orders = orders[~orders.status.isin(["REJECTED", "CANCELLED", "COMPLETE"])]

            if len(orders) == 0:
                Constants.logger.info("ALL orders have been completed")
                break

            orders = orders.to_dict('records')
            for order in orders:
                order_id = order['order_id']

                ltp = self.get_ltp(order['exchange'], order['tradingsymbol'])
                order['price'] = ltp
                self.modify_order(order)

                if order_id not in modification_count:
                    modification_count[order_id] = 1
                else:
                    modification_count[order_id] += 1

                time.sleep(.1)

                if modification_count[order_id] > 5:
                    order['order_type'] = "MARKET"
                    order['price'] = 0
                    Constants.logger.info("Placing MARKET order [{}]".format(order))
                    self.modify_order(order)

    @retry(wait_exponential_multiplier=3000, wait_exponential_max=10000, stop_max_attempt_number=3)
    def get_positions(self):
        return self.wrapper.positions()

    def positions_pnl(self):
        positions = pd.DataFrame(self.get_positions()['net'])
        print("Total PnL {}".format(positions.pnl.astype(float).sum()))

    def add_params(self, orders):
        df = pd.DataFrame(orders)
        df.loc[:, 'price'] = df.apply(lambda x: self.get_ltp(x['exchange'],
                                                             x['tradingsymbol']),
                                      axis=1)

        df.loc[:, 'disclosedquantity'] = np.where(df.exchange == "NSE", df.quantity / 10 + 1, df.quantity)
        df.loc[:, 'disclosedquantity'] = df.disclosedquantity.astype(int)

        return df.to_dict('records')

    # @retry(wait_exponential_multiplier=3000, wait_exponential_max=10000, stop_max_attempt_number=3)
    def place_order(self, tradingsymbol=None, exchange=None, quantity=None, order_type=None, transaction_type=None,
                    tag=None, product=None, price=None, trigger_price=None):
        try:
            order_id = self.wrapper.place_order(variety='regular',
                                                tradingsymbol=tradingsymbol,
                                                exchange=exchange,
                                                transaction_type=transaction_type,
                                                quantity=int(abs(quantity)),
                                                order_type=order_type,
                                                disclosed_quantity=None,
                                                price=price,
                                                trigger_price=trigger_price,
                                                product=product,
                                                tag=tag)
            return order_id
        except Exception as e:
            exception_message = "Order placement failed with error [{}]".format(str(e))
            print(exception_message)

    def square_off_all(self, dry_run=True, strike=None, sleep_time=0.1):
        positions = self.get_positions()['net']
        if len(positions) == 0:
            print("Positions are already squared off")
            return

        positions = pd.DataFrame(positions)
        if strike:
            positions = positions[positions.tradingsymbol.str.contains(strike)]

        positions.loc[:, 'net_quantity'] = positions.buy_quantity - positions.sell_quantity
        positions = positions[positions.net_quantity != 0]
        positions = positions[positions.exchange == "NFO"]
        positions.loc[:, 'transaction_type'] = np.where(positions.quantity < 0,
                                                        "BUY",
                                                        "SELL")
        positions.loc[:, 'lot_size'] = positions.apply(lambda x: self.get_lot_size(x.exchange, x.tradingsymbol), axis=1)
        positions.loc[:, 'price'] = positions.apply(lambda x: self.get_ltp(x['exchange'], x['tradingsymbol']), axis=1)

        positions = positions.to_dict('records')
        orders_to_close = []
        for position in positions:
            quantity = abs(position['net_quantity'])
            exchange = position['exchange']
            tradingsymbol = position['tradingsymbol']
            transaction_type = position['transaction_type']

            quantity_in_lots = int(quantity / self.get_lot_size(exchange, tradingsymbol))

            split_into = int(math.ceil(quantity_in_lots / 25))
            split_array = NumberUtils.split(abs(quantity_in_lots), abs(split_into))

            for q in split_array:
                orders_to_close.append(
                    {
                        'symbol': tradingsymbol,
                        'exchange': exchange,
                        'transaction_type': transaction_type,
                        'quantity_in_lots': q,
                        'product': position['product'],
                        'price': position['price']
                    })

        random.shuffle(orders_to_close)
        orders_to_close = sorted(orders_to_close, key=lambda d: d['transaction_type'])
        orders_placed = []
        for order in orders_to_close:
            quantity = int(order['quantity_in_lots'] * self.get_lot_size(order['exchange'], order['symbol']))
            print(order['symbol'], order['exchange'], order['transaction_type'], quantity, order['product'],
                  order['price'])
            if dry_run == False:
                order_id = self.place_order(tradingsymbol=order['symbol'],
                                            exchange=order['exchange'],
                                            quantity=quantity,
                                            order_type="LIMIT",
                                            transaction_type=order['transaction_type'],
                                            tag="killall",
                                            product=order['product'],
                                            price=order['price'])
                orders_placed.append(order_id)
                time.sleep(sleep_time)
        if dry_run == False:
            self.modify_orders_till_complete(orders_placed)

        return orders_to_close

    def configure(self):
        quantplay_config = QplayConfig.get_config()

        print("Enter Zerodha API key:")
        api_key = input()

        print("Enter Zerodha API Secret:")
        api_secret = input()

        quantplay_config['DEFAULT'][Zerodha.zerodha_api_key] = api_key
        quantplay_config['DEFAULT'][Zerodha.zerodha_api_secret] = api_secret

        with open('{}/config'.format(QplayConfig.config_path), 'w') as configfile:
            quantplay_config.write(configfile)

    def validate_config(self, quantplay_config):
        if quantplay_config is None:
            return False
        if Zerodha.zerodha_api_key not in quantplay_config['DEFAULT']:
            return False
        if Zerodha.zerodha_api_secret not in quantplay_config["DEFAULT"]:
            return False

        return True

    def generate_token(self, user_id, api_key, api_secret, password, totp):
        kite = KiteConnect(api_key=api_key)

        try:
            request_token = KiteUtils.get_request_token(api_key=api_key,
                                                        user_id=user_id,
                                                        password=password,
                                                        totp=totp)
        except Exception as e:
            traceback.print_exc()
            print("Need token input " + kite.login_url())
            raise e
            # request_token = input()

        print("request token {} api_secret {}".format(request_token, api_secret))

        data = kite.generate_session(request_token, api_secret=api_secret)
        kite.set_access_token(data["access_token"])

        QplayConfig.save_config("zerodha_wrapper", codecs.encode(pickle.dumps(kite), "base64").decode())
        self.kite = kite
        self.wrapper = kite
        return kite

    def profile(self):
        user_profile = self.wrapper.profile()

        response = {
            'user_id': user_profile['user_id'],
            'full_name': user_profile['user_name'],
            'segments': user_profile['exchanges'],
            'email': user_profile['email']
        }

        return response

    def positions(self):
        positions = pd.DataFrame(self.wrapper.positions()['net'])

        if len(positions) == 0:
            return pd.DataFrame(columns=self.positions_column_list)

        positions.loc[:, 'exchange_symbol'] = positions.exchange + ":" + positions.tradingsymbol
        symbols = positions.exchange_symbol.unique().tolist()
        symbol_ltps = self.get_ltps(symbols)

        positions.loc[:, 'ltp'] = positions.exchange_symbol.apply(lambda x: symbol_ltps[x]['last_price'])
        positions.loc[:, 'pnl'] = positions.sell_value - positions.buy_value
        positions.loc[:, 'pnl'] += (positions.quantity) * positions.ltp

        positions.loc[:, 'option_type'] = np.where("PE" == positions.tradingsymbol.str[-2:], "PE", "CE")
        positions.loc[:, 'option_type'] = np.where(positions.exchange != "NFO", None, positions.option_type)
        return positions[self.positions_column_list]

    def orders(self, tag=None):
        orders = pd.DataFrame(self.wrapper.orders())

        positions = self.positions()
        if len(orders) == 0:
            return pd.DataFrame(columns=self.orders_column_list)

        orders = pd.merge(orders, positions[['tradingsymbol', 'ltp']],
                          how="left",
                          left_on=['tradingsymbol'],
                          right_on=['tradingsymbol'])

        orders.rename(
            columns={
                'placed_by': 'user_id'
            }, inplace=True)

        orders = orders[self.orders_column_list]

        orders.loc[:, 'pnl'] = orders.ltp * orders.filled_quantity - orders.average_price * orders.filled_quantity
        orders.loc[:, 'pnl'] = np.where(orders.transaction_type == "SELL", -orders.pnl, orders.pnl)

        if tag:
            orders = orders[orders.tag == tag]

        return orders

    def account_summary(self):
        margins = self.wrapper.margins()
        response = {
            'margin_used': float(margins['equity']['utilised']['debits']),
            'margin_available': float(margins['equity']['available']['live_balance']),
            'pnl': float(self.positions().pnl.sum())
        }
        return response
