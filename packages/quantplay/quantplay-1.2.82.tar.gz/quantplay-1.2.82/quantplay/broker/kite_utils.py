import time
import traceback

from retrying import retry
from quantplay.utils.selenium_utils import Selenium
import pyotp

class KiteUtils():
    zerodha_username = "zerodha_username"
    zerodha_password = "zerodha_password"
    zeordha_totp_unique_id = "zerodha_totp_unique_id"

    @staticmethod
    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=3)
    def get_request_token(api_key=None, user_id=None, password=None, totp=None):
    
        try:
            browser = Selenium.get_browser()

            # TODO api should be fetched from configuration

            kite_url = "https://kite.trade/connect/login?api_key={}&v=3".format(api_key)
            print("Kite Url {}".format(kite_url))
            browser.get(kite_url)
            time.sleep(5)


            user_id_element = browser.find_element("xpath", '//*[@id="container"]/div/div/div[2]/form/div[1]/input')
            password_element = browser.find_element("xpath", '//*[@id="container"]/div/div/div[2]/form/div[2]/input')

            user_id_element.send_keys(user_id)
            password_element.send_keys(password)

            login_attempt = browser.find_element("xpath", '//*[@id="container"]/div/div/div[2]/form/div[4]/button')
            login_attempt.submit()
            time.sleep(5)

            kite_pin = browser.find_element("xpath", '/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/form/div[1]/input')
            kite_pin.send_keys(pyotp.TOTP(totp).now())
            time.sleep(3)
            # login_attempt = browser.find_element("xpath", '//*[@id="container"]/div/div/div[2]/form/div[3]/button')
            # login_attempt.submit()
            # time.sleep(1)

            url = browser.current_url
            print("got kite url {}".format(url))
            request_token = url.split('token=')[1].split('&')[0]

            browser.close()

            return request_token
        except:
            print(traceback.print_exc())
            raise


