import hashlib
import requests
import json
import time
import pandas as pd

from quantplay.utils.constant import Constants, timeit, OrderType
from quantplay.config.qplay_config import QplayConfig
import getpass
from quantplay.broker.generics.broker import Broker
import traceback
from quantplay.exception.exceptions import InvalidArgumentException
import numpy as np
import pyotp
import math
from quantplay.utils.number_utils import NumberUtils
import random
import websocket
import _thread as thread
import copy
import threading
from quantplay.utils.pickle_utils import PickleUtils


class Motilal(Broker):
    user_id = "motilal_user_id"
    api_key = "motilal_api_key"
    password = "motilal_password"
    auth_token = "motilal_auth_token"
    two_factor_authentication = "motilal_2FA"
    secret_key = "motilal_secret_key"

    headers = {
        "Accept": "application/json",
        "User-Agent": "MOSL/V.1.1.0",
        "SourceId": "WEB",
        "MacAddress": "00:50:56:BD:F4:0B",
        "ClientLocalIp": "192.168.165.165",
        "ClientPublicIp": "106.193.137.95",
        "osname": "Ubuntu",
        "osversion": "10.0.19041",
        "devicemodel": "AHV",
        "manufacturer": "DELL",
        "productname": "Your Product Name",
        "productversion": "Your Product Version",
        "installedappid": "AppID",
        "browsername": "Chrome",
        "browserversion": "105.0"
    }

    @timeit(MetricName="Motilal:__init__")
    def __init__(self, is_uat=False, headers=None, load_instruments=True, user_id=None, password=None, api_key=None,
                 two_fa=None, totp=None):
        super(Motilal, self).__init__()

        self.instrument_data_by_exchange = {}

        uat = ""
        if is_uat:
            uat = "uat"

        self.url = "https://{}openapi.motilaloswal.com/rest/login/v3/authdirectapi".format(uat)
        self.otp_url = "https://{}openapi.motilaloswal.com/rest/login/v3/resendotp".format(uat)
        self.verify_otp_url = "https://{}openapi.motilaloswal.com/rest/login/v3/verifyotp".format(uat)
        self.ltp_utl = "https://{}openapi.motilaloswal.com/rest/report/v1/getltpdata".format(uat)
        self.place_order_url = "https://{}openapi.motilaloswal.com/rest/trans/v1/placeorder".format(uat)
        self.get_profile_url = "https://{}openapi.motilaloswal.com/rest/login/v1/getprofile".format(uat)
        self.margin_summary_url = "https://{}openapi.motilaloswal.com/rest/report/v1/getreportmarginsummary".format(uat)
        self.modify_order_url = "https://{}openapi.motilaloswal.com/rest/trans/v2/modifyorder".format(uat)
        self.order_book_url = "https://{}openapi.motilaloswal.com/rest/book/v1/getorderbook".format(uat)
        self.cancel_order_url = "https://{}openapi.motilaloswal.com/rest/trans/v1/cancelorder".format(uat)
        self.positions_url = "https://{}openapi.motilaloswal.com/rest/book/v1/getposition".format(uat)

        try:
            if headers:
                self.headers = headers
            else:
                self.generate_token(user_id, password, api_key, two_fa, totp)
        except Exception as e:
            raise e

        try:
            self.get_orders()
        except Exception as e:
            raise InvalidArgumentException("Motilal client generation failed due to invalid arguments")

        if load_instruments:
            self.load_instrument()

        self.order_type_sl = "STOPLOSS"
        self.nfo_exchange = "NSEFO"
        self.exchange_code_map = {
            "NFO": "NSEFO",
            "CDS": "NSECD"
        }

    def update_headers(self):
        Constants.logger.info("Updating headers")
        quantplay_config = QplayConfig.get_config()

        auth_token = quantplay_config['DEFAULT'][Motilal.auth_token]
        api_key = quantplay_config['DEFAULT'][Motilal.api_key]
        user_id = quantplay_config['DEFAULT'][Motilal.user_id]

        self.headers['vendorinfo'] = user_id
        self.headers['Authorization'] = auth_token
        self.headers['ApiKey'] = api_key

        self.user_id = user_id

    @timeit(MetricName="Motilal:initialize_expiry_fields")
    def initialize_expiry_fields(self):
        self.instrument_data.loc[:, 'tradingsymbol'] = self.instrument_data.scripshortname
        self.instrument_data.loc[:, 'expiry'] = pd.to_datetime(self.instrument_data.expirydate + 315513000,
                                                                  unit='s')

        self.instrument_data.loc[:, "expiry_year"] = self.instrument_data["expiry"].dt.strftime("%y").astype(str)
        self.instrument_data.loc[:, "month"] = self.instrument_data["expiry"].dt.strftime("%b").str.upper()

        self.instrument_data.loc[:, "month_number"] = self.instrument_data["expiry"].dt.strftime("%m").astype(
            float).astype(str)
        self.instrument_data.loc[:, 'month_number'] = np.where(self.instrument_data.month_number == 'nan',
                                                                  np.nan,
                                                                  self.instrument_data.month_number.str.split(
                                                                      ".").str[0]
                                                                  )

        self.instrument_data.loc[:, "week_option_prefix"] = np.where(
            self.instrument_data.month_number.astype(float) >= 10,
            self.instrument_data.month.str[0] + self.instrument_data["expiry"].dt.strftime("%d").astype(str),
            self.instrument_data.month_number + self.instrument_data["expiry"].dt.strftime("%d").astype(str),
        )

        self.instrument_data.loc[:, "next_expiry"] = self.instrument_data.expiry + pd.DateOffset(days=7)

    @timeit(MetricName="Motilal:add_quantplay_fut_tradingsymbol")
    def add_quantplay_fut_tradingsymbol(self):
        seg_condition = [
            ((self.instrument_data["instrumentname"].str.contains("FUT")) & (
                        self.instrument_data.instrumentname != "OPTFUT"))
        ]

        tradingsymbol = [
            self.instrument_data.tradingsymbol + self.instrument_data.expiry_year + self.instrument_data.month + "FUT"
        ]

        self.instrument_data.loc[:, "tradingsymbol"] = np.select(
            seg_condition, tradingsymbol, default=self.instrument_data.tradingsymbol
        )

    @timeit(MetricName="Motilal:add_quantplay_opt_tradingsymbol")
    def add_quantplay_opt_tradingsymbol(self):
        seg_condition = (self.instrument_data["strikeprice"] > 0)
        weekly_option_condition = (
                (self.instrument_data.expiry.dt.month == self.instrument_data.next_expiry.dt.month) & (
            self.instrument_data.exchangename.isin(["NFO", "NSEFO", "NSECD"])))
        month_option_condition = (
                (self.instrument_data.expiry.dt.month != self.instrument_data.next_expiry.dt.month) | (
                    self.instrument_data.exchangename == "MCX"))

        self.instrument_data.loc[:, "tradingsymbol"] = np.where(
            seg_condition,
            self.instrument_data.tradingsymbol + self.instrument_data.expiry_year,
            self.instrument_data.tradingsymbol
        )

        self.instrument_data.loc[:, "tradingsymbol"] = np.where(
            seg_condition & weekly_option_condition,
            self.instrument_data.tradingsymbol + self.instrument_data.week_option_prefix,
            self.instrument_data.tradingsymbol
        )

        self.instrument_data.loc[:, "tradingsymbol"] = np.where(
            seg_condition & month_option_condition,
            self.instrument_data.tradingsymbol + self.instrument_data.month,
            self.instrument_data.tradingsymbol
        )

        self.instrument_data.loc[:, "tradingsymbol"] = np.where(
            seg_condition,
            self.instrument_data.tradingsymbol +
            self.instrument_data.strikeprice.astype(float).astype(str).str.split(".").str[0],
            self.instrument_data.tradingsymbol
        )

        self.instrument_data.loc[:, 'after_point'] = (self.instrument_data.strikeprice * 100).astype(int)
        self.instrument_data.loc[:, 'after_point'] = (self.instrument_data.after_point % 100).astype(str).apply(
            lambda x: x.rstrip('0'))
        self.instrument_data.loc[:, 'tradingsymbol'] = np.where(self.instrument_data.after_point.str.len() > 0,
                                                                   self.instrument_data.tradingsymbol + "." + self.instrument_data.after_point,
                                                                   self.instrument_data.tradingsymbol)

        self.instrument_data.loc[:, "tradingsymbol"] = np.where(
            seg_condition,
            self.instrument_data.tradingsymbol + self.instrument_data.optiontype,
            self.instrument_data.tradingsymbol
        )

    @timeit(MetricName="Motilal:load_file_by_url")
    def load_file_by_url(self, exchange):
        data_url = "https://openapi.motilaloswal.com/getscripmastercsv?name={}".format(exchange)
        df = pd.read_csv(data_url)
        self.instrument_data_by_exchange[exchange] = df

    @timeit(MetricName="Motilal:load_instrument")
    def load_instrument(self):
        try:
            self.symbol_data = PickleUtils.load_data("motilal_instruments")
            Constants.logger.info("[LOADING_INSTRUMENTS] loading data from cache")
        except Exception as e:
            Constants.logger.info("[LOADING_INSTRUMENTS] loading data from server")
            exchanges = ["NSEFO", "MCX", "NSECD", "NSE"]
            threads = []
            for exchange in exchanges:
                th = threading.Thread(target=self.load_file_by_url, args=(exchange,))
                th.start()
                threads.append(th)
            for thread in threads:
                thread.join()

            instrument_file_FO = self.instrument_data_by_exchange["NSEFO"]
            instrument_file_MCX = self.instrument_data_by_exchange["MCX"]
            instrument_file_CDS = self.instrument_data_by_exchange["NSECD"]
            instrument_file_CDS = instrument_file_CDS[instrument_file_CDS.instrumentname.isin(["OPTCUR", "FUTCUR"])]
            instrument_file_EQ = self.instrument_data_by_exchange["NSE"]
            instrument_file_EQ = instrument_file_EQ[instrument_file_EQ['scripname'].str.contains(" EQ")]
            instrument_file_EQ.loc[:, 'expiry'] = 0

            self.instrument_data = pd.concat([instrument_file_CDS, instrument_file_MCX, instrument_file_FO,
                                              instrument_file_EQ])

            self.initialize_expiry_fields()
            self.add_quantplay_opt_tradingsymbol()
            self.add_quantplay_fut_tradingsymbol()

            self.initialize_symbol_data()


        self.quantplay_symbol_map = {}
        for a in self.symbol_data:
            self.quantplay_symbol_map[self.symbol_data[a]['tradingsymbol']] = self.symbol_data[a]['scripname']

    @timeit(MetricName="Motilal:initialize_symbol_data")
    def initialize_symbol_data(self):
        instruments = self.instrument_data
        instruments = instruments.to_dict('records')
        self.symbol_data = {}
        for instrument_data in instruments:
            exchange = instrument_data['exchangename']
            tradingsymbol = instrument_data['scripname']

            instrument_data['lot_size'] = instrument_data['marketlot']
            self.symbol_data["{}:{}".format(exchange, tradingsymbol)] = instrument_data

        PickleUtils.save_data(self.symbol_data, "motilal_instruments")



    def get_symbol(self, symbol):
        if symbol not in self.quantplay_symbol_map:
            return symbol
        return self.quantplay_symbol_map[symbol]

    def get_order_type(self, order_type):
        if order_type == OrderType.sl:
            return "STOPLOSS"
        return order_type

    def get_exchange(self, exchange):
        if exchange in self.exchange_code_map:
            return self.exchange_code_map[exchange]

        return exchange

    def get_product(self, product):
        return "NORMAL"

    def place_order_quantity(self, quantity, tradingsymbol, exchange):
        lot_size = self.get_lot_size(exchange, tradingsymbol)
        quantity_in_lots = int(quantity / lot_size)

        return quantity_in_lots

    def generate_token(self, user_id, password, api_key, two_fa, totp):
        current_totp = pyotp.TOTP(totp).now()
        Constants.logger.info("TOTP is {}".format(current_totp))
        # initializing string
        str = "{}{}".format(password, api_key)
        result = hashlib.sha256(str.encode())

        data = {
            "userid": user_id,
            "password": result.hexdigest(),
            "2FA": two_fa,
            "totp": current_totp
        }

        self.headers['ApiKey'] = api_key
        self.headers['vendorinfo'] = user_id
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))

        resp_json = response.json()
        Constants.logger.info("login response {}".format(resp_json))
        self.headers['Authorization'] = resp_json['AuthToken']
        self.user_id = user_id

    def send_otp(self):
        response = requests.post(self.otp_url, headers=self.headers).json()
        Constants.logger.info(response)
        return response

    def verify_otp(self, otp):
        data = {
            "otp": otp
        }
        response = requests.post(self.verify_otp_url, headers=self.headers, data=json.dumps(data)).json()
        Constants.logger.info(response)
        return response

    def get_ltp(self, exchange=None, tradingsymbol=None):
        tradingsymbol = self.get_symbol(tradingsymbol)
        data = {
            "userid": self.user_id,
            "exchange": exchange,
            "scripcode": self.symbol_data["{}:{}".format(exchange, tradingsymbol)]['scripcode']
        }

        response = requests.post(self.ltp_utl, headers=self.headers, data=json.dumps(data))
        Constants.logger.info("[GET_LTP_RESPONSE] response {}".format(response.json()))
        return response.json()["data"]["ltp"] / 100.0

    def get_orders(self, order_status=None, order_type=None):
        response = (requests.post(self.order_book_url, headers=self.headers)).json()
        if response["status"] == "ERROR":
            Constants.logger.info("Error while fetching order book [{}]".format(response["message"]))
            raise Exception(response["message"])
        orders = response["data"]

        if order_status:
            orders = [a for a in orders if a['orderstatus'] == order_status]

        if order_type:
            orders = [a for a in orders if a['ordertype'] == order_type]

        return orders

    def get_positions(self):
        response = (requests.post(self.positions_url, headers=self.headers)).json()
        if response["status"] == "ERROR":
            Constants.logger.info("Error while fetching order book [{}]".format(response["message"]))
            raise Exception(response["message"])

        positions = response["data"]

        return positions

    def square_off_all(self, dry_run=True, strike=None, sleep_time=0.1, tag=None):
        positions = self.get_positions()
        if positions == None:
            print("Positions are already squared off")
            return

        positions = pd.DataFrame(positions)
        if strike:
            positions = positions[positions.symbol.str.contains(strike)]

        positions.loc[:, 'net_quantity'] = positions.buyquantity - positions.sellquantity
        positions = positions[['exchange', 'symbol', 'net_quantity']].sort_values("net_quantity")

        positions = positions.to_dict('records')
        orders_to_close = []
        for position in positions:
            exchange = position['exchange']
            symbol = position['symbol']
            quantity = position['net_quantity']

            transaction_type = "SELL"
            if quantity == 0 or exchange != "NSEFO":
                continue
            elif quantity < 0:
                transaction_type = "BUY"

            quantity = abs(quantity)
            quantity_in_lots = int(quantity / self.get_lot_size(exchange, symbol))

            split_into = int(math.ceil(quantity_in_lots / 25))
            split_array = NumberUtils.split(abs(quantity_in_lots), abs(split_into))

            for q in split_array:
                orders_to_close.append(
                    {
                        'symbol': symbol,
                        'exchange': exchange,
                        'transaction_type': transaction_type,
                        'quantity_in_lots': q
                    })

        random.shuffle(orders_to_close)
        orders_to_close = sorted(orders_to_close, key=lambda d: d['transaction_type'])
        for order in orders_to_close:
            print(order['symbol'], order['exchange'], order['transaction_type'], order['quantity_in_lots'])
            if dry_run == False:
                self.place_order(tradingsymbol=order['symbol'],
                                 exchange=order['exchange'],
                                 quantity=order['quantity_in_lots'],
                                 order_type="MARKET",
                                 transaction_type=order['transaction_type'],
                                 tag="square-off",
                                 product="NORMAL",
                                 price=0)
                time.sleep(sleep_time)

    def modify_price(self, order_id, price, trigger_price=None, order_type=None):
        orders = pd.DataFrame(self.get_orders())
        orders = orders.to_dict('records')
        order_found = False

        for order in orders:
            if order['uniqueorderid'] == order_id:
                order_found = True
                break

        if order_found == False:
            Constants.logger.error("[ORDER_NOT_FOUND] invalid modify request for {}".format(order_id))
            return

        order['price'] = price
        if trigger_price != None:
            order['triggerprice'] = trigger_price

        if order["ordertype"] == "Stop Loss":
            order["ordertype"] = "STOPLOSS"

        self.modify_order(order)

    def modify_orders_till_complete(self, orders_placed):
        modification_count = {}
        while 1:
            time.sleep(10)
            orders = pd.DataFrame(self.get_orders())
            orders = orders[orders.uniqueorderid.isin(orders_placed)]

            orders = orders[~orders.orderstatus.isin(["Error", "Traded", "Cancel", "Rejected"])]

            if len(orders) == 0:
                Constants.logger.info("ALL orders have be completed")
                break

            orders = orders.to_dict('records')
            for order in orders:
                order_id = order['uniqueorderid']

                ltp = self.get_ltp(order['exchange'], order['symbol'])
                order['price'] = ltp
                self.modify_order(order)

                if order_id not in modification_count:
                    modification_count[order_id] = 1
                else:
                    modification_count[order_id] += 1

                time.sleep(.1)

                if modification_count[order_id] > 5:
                    order['ordertype'] = "MARKET"
                    order['price'] = 0
                    Constants.logger.info("Placing MARKET order [{}]".format(order))
                    self.modify_order(order)

    def exit_all_trigger_orders(self, tag="ALL",
                                symbol_contains=None):

        stoploss_orders = self.get_orders(order_status="Confirm", order_type="Stop Loss")

        if len(stoploss_orders) == 0:
            print("All stoploss orders have been already closed")
            return

        stoploss_orders = pd.DataFrame(stoploss_orders)
        if tag != "ALL":
            stoploss_orders = stoploss_orders[stoploss_orders.tag == tag]

        if symbol_contains is not None:
            stoploss_orders = stoploss_orders[stoploss_orders['symbol'].str.contains(symbol_contains)]

        if len(stoploss_orders) == 0:
            print("All stoploss orders have been already closed")
            return

        orders_to_close = list(stoploss_orders.uniqueorderid.unique())

        stoploss_orders = stoploss_orders.to_dict('records')
        for stoploss_order in stoploss_orders:
            exchange = stoploss_order['exchange']
            tradingsymbol = stoploss_order['symbol']

            if exchange == "NFO":
                stoploss_order['ordertype'] = "MARKET"
                stoploss_order['price'] = 0
            else:
                ltp = self.get_ltp(exchange, tradingsymbol)
                stoploss_order['ordertype'] = "LIMIT"
                stoploss_order['price'] = self.round_to_tick(ltp)

            self.modify_order(stoploss_order)
            time.sleep(.1)

        self.modify_orders_till_complete(orders_to_close)
        print("All order have been closed successfully")

    def modify_order(self, order):
        data = {
            "uniqueorderid": order['uniqueorderid'],
            "newordertype": order['ordertype'].upper(),
            "neworderduration": order['orderduration'].upper(),
            "newquantityinlot": int(order['totalqtyremaining'] / order['lotsize']),
            # "newdisclosedquantity": 0,
            "newprice": order['price'],
            "newtriggerprice": order['triggerprice'],
            "qtytradedtoday": order['qtytradedtoday'],
            "lastmodifiedtime": order['lastmodifiedtime']
        }

        if 'exchange' in order and order['exchange'] == "MCX":
            data['newquantityinlot'] = int(order['totalqtyremaining'])

        try:
            Constants.logger.info("[MODIFYING_ORDER] order [{}]".format(data))
            response = requests.post(self.modify_order_url, headers=self.headers, data=json.dumps(data)).json()
            Constants.logger.info("[MODIFY_ORDER_RESPONSE] {}".format(response))
        except Exception as e:
            exception_message = "[ORDER_MODIFICATION_FAILED] for {} failed with exception {}".format(
                order['uniqueorderid'],
                e)
            Constants.logger.error("{}".format(exception_message))

    def cancel_order(self, unique_order_id):
        data = {
            "uniqueorderid": unique_order_id
        }

        try:
            Constants.logger.info("Cancelling order [{}]".format(unique_order_id))
            response = requests.post(self.cancel_order_url, headers=self.headers, data=json.dumps(data)).json()
            Constants.logger.info("Cancel order response [{}]".format(response))
        except Exception as e:
            exception_message = "[ORDER_CANCELLATION_FAILED] unique_order_id {} exception {}".format(unique_order_id,
                                                                                                     e)
            Constants.logger.error(exception_message)

    def get_profile(self):
        response = requests.post(self.get_profile_url, headers=self.headers,
                                 data=json.dumps({'Clientcode': self.headers['vendorinfo']})).json()
        if response['status'] == "ERROR":
            raise Exception(response['message'])

        return response['data']

    def margin_summary(self):
        response = requests.post(self.margin_summary_url, headers=self.headers,
                                 data=json.dumps({'Clientcode': self.headers['vendorinfo']})).json()
        if response['status'] == "ERROR":
            raise Exception(response['message'])

        return response['data']

    def place_order(self, tradingsymbol=None, exchange=None, quantity=None, order_type=None, transaction_type=None,
                    tag=None, product=None, price=None, trigger_price=None):
        data = {
            "exchange": exchange,
            "symboltoken": self.symbol_data["{}:{}".format(exchange, tradingsymbol)]['scripcode'],
            "buyorsell": transaction_type,
            "ordertype": order_type,
            "producttype": product,
            "orderduration": "DAY",
            "price": price,
            "triggerprice": trigger_price,
            "quantityinlot": quantity,
            "disclosedquantity": 0,
            "amoorder": "N",
            "algoid": "",
            "tag": tag
        }
        try:
            Constants.logger.info("[PLACING_ORDER] {}".format(json.dumps(data)))
            response = requests.post(self.place_order_url, headers=self.headers, data=json.dumps(data)).json()
            Constants.logger.info("[PLACE_ORDER_RESPONSE] {} input {}".format(response, json.dumps(data)))
            if response['status'] == "ERROR":
                raise Exception(response['message'])
            return response['uniqueorderid']
        except Exception as e:
            exception_message = "Order placement failed with error [{}]".format(str(e))
            print(exception_message)

    def on_message(self, ws, order):
        try:
            order = json.loads(order)
            print(order)

            order['placed_by'] = self.user_id
            order['tag'] = self.user_id
            order['order_id'] = order['orderid']
            order['exchange_order_id'] = order['order_id']
            order['transaction_type'] = order['transactiontype']
            order['quantity'] = int(order['quantity'])
            order['order_type'] = order['ordertype']

            if order['exchange'] == "NFO":
                order["tradingsymbol"] = self.symbol_map[order["tradingsymbol"]]

            if order['order_type'] == "STOPLOSS_LIMIT":
                order['order_type'] = "SL"

            if 'triggerprice' in order and order['triggerprice'] != 0:
                order['trigger_price'] = float(order['triggerprice'])
            else:
                order['trigger_price'] = None

            if order["status"] == "trigger pending":
                order["status"] = "TRIGGER PENDING"
            elif order["status"] == "cancelled":
                order["status"] = "CANCELLED"
            elif order["status"] == "open":
                order["status"] = "OPEN"
            elif order["status"] == "complete":
                order["status"] = "COMPLETE"

            # self.order_updates.put(order)
            print("Final order {}".format(order))
        except Exception as e:
            Constants.logger.error("[ORDER_UPDATE_PROCESSING_FAILED] {}".format(e))
        print(json.dumps(order))

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        def run(*args):
            for i in range(300000):
                time.sleep(1)
                print({
                    "actiontype": "TradeSubscribe",
                    "clientid": self.headers['vendorinfo']
                })
                ws.send(json.dumps({
                    "actiontype": "TradeSubscribe",
                    "clientid": self.headers['vendorinfo']
                }))
            time.sleep(1)
            ws.close()
            print("thread terminating...")

        thread.start_new_thread(run, ())

    def stream_order_data(self):
        api_key = self.headers['ApiKey']
        auth_token = self.headers['Authorization']
        client_id = self.headers['vendorinfo']

        root_url = "wss://openapi.motilaloswal.com/ws"
        ws_url = "{}?clientid={}&authtoken={}&apikey={}".format(root_url, client_id, auth_token, api_key)

        websocket.enableTrace(False)
        print(ws_url)
        ws = websocket.WebSocketApp(ws_url,
                                    on_message=self.on_message,
                                    on_error=self.on_error)
        ws.on_open = self.on_open
        ws.run_forever()

    def account_summary(self):
        response = {
            'margin_used': 0
        }

        margin_summary = self.margin_summary()
        for margin_particular in margin_summary:
            if margin_particular['srno'] == 103:
                response['margin_available'] = margin_particular['amount']
            if margin_particular['srno'] in [301, 321, 340, 360]:
                response['margin_used'] += margin_particular['amount']

        response['pnl'] = self.positions().pnl.sum()
        return response

    def profile(self):
        api_response = requests.post(self.get_profile_url, headers=self.headers,
                                     data=json.dumps({'Clientcode': self.headers['vendorinfo']})).json()
        if api_response['status'] == "ERROR":
            raise Exception(api_response['message'])

        api_response = api_response['data']
        response = {
            'user_id': api_response['clientcode'],
            'full_name': api_response['name'],
            'segments': api_response['exchanges']
        }

        return response

    def positions(self):
        response = (requests.post(self.positions_url, headers=self.headers)).json()
        if response["status"] == "ERROR":
            Constants.logger.info("Error while fetching order book [{}]".format(response["message"]))
            raise Exception(response["message"])

        positions = response["data"]

        if positions is None or len(positions) == 0:
            return pd.DataFrame(columns=self.positions_column_list)

        positions = pd.DataFrame(positions)
        positions.loc[:, 'tradingsymbol'] = positions.symbol

        positions.loc[:, 'ltp'] = positions.LTP
        positions.loc[:, 'pnl'] = positions.sellamount - positions.buyamount
        positions.loc[:, 'pnl'] += (positions.buyquantity - positions.sellquantity)*positions.ltp
        positions.loc[:, 'quantity'] = positions.buyquantity - positions.sellquantity
        positions.rename(
            columns={
                "productname": "product",
                "sellquantity": "sell_quantity",
                "buyquantity": "buy_quantity",
                "optiontype": "option_type"
            }, inplace=True)
        return positions[self.positions_column_list]

    def orders(self, tag=None):
        response = (requests.post(self.order_book_url, headers=self.headers)).json()
        if response["status"] == "ERROR":
            Constants.logger.info("Error while fetching order book [{}]".format(response["message"]))
            raise Exception(response["message"])
        orders = response["data"]
        orders = pd.DataFrame(orders)

        positions = self.positions()
        if len(positions) == 0 or len(orders) == 0:
            return pd.DataFrame(columns=self.orders_column_list)

        orders.loc[:, 'tradingsymbol'] = orders.symbol
        orders = pd.merge(orders, positions[['tradingsymbol', 'ltp']],
                          how="left",
                          left_on=['tradingsymbol'],
                          right_on=['tradingsymbol'])

        orders.rename(
            columns={
                'clientid': 'user_id',
                "LTP": 'ltp',
                'buyorsell': 'transaction_type',
                "averageprice": "average_price",
                "orderid" : "order_id",
                "orderstatus" : "status",
                "entrydatetime" : "order_timestamp",
                "orderqty" : "quantity",
                "totalqtytraded" : "filled_quantity",
                "totalqtyremaining" : "pending_quantity"
            }, inplace=True)
        orders.loc[:, 'product'] = orders.ordercategory

        orders = orders[self.orders_column_list]
        orders.loc[:, 'pnl'] = orders.ltp * orders.filled_quantity - orders.average_price * orders.filled_quantity
        orders.loc[:, 'pnl'] = np.where(orders.transaction_type == "SELL", -orders.pnl, orders.pnl)

        if tag:
            orders = orders[orders.tag == tag]

        return orders

