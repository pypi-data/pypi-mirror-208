import datetime
import logging
import requests
import time
from requests import utils


class UsedTime:
    stamp = int(time.time() * 1000)
    now = datetime.datetime.now().date()
    today = now.__str__()
    weekstrat = (now - datetime.timedelta(days=now.weekday())).__str__()
    weekend = (now + datetime.timedelta(days=6 - now.weekday())).__str__()
    yymm = time.strftime('%Y-%m', time.localtime())
    yymm01 = time.strftime('%Y-%m-01', time.localtime())
    todaybeformonth = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400 * 30))
    tomorrow = time.strftime('%Y-%m-%d', time.localtime(time.time() + 86400))
    yesterday = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))


class YunXiao:

    def __init__(self, phone: str, password: str):
        """
        :param phone: 用户手机号
        :param password: 用户密码
        """
        self.user = phone
        self.pwd = password


class AppOAuth(YunXiao):
    def __init__(self, phone: str, password: str):
        """
        获取一个配置好鉴权的 Request Session
        :param phone:
        :param password:
        """
        super().__init__(phone, password)

        self.__token__ = self.__read_token__()

        while self.__check_token__() != 200:
            logging.warning("Token 失效，准备刷新")
            self.__renew_token__()
            time.sleep(2)
        else:
            logging.info("Token 有效")

        self.session = requests.session()
        self.session.headers.update({"x3-authentication": self.__token__})

    @staticmethod
    def __read_token__():
        """
        读取存储的 token
        """
        # logging.info("正在读取配置文件")
        try:
            with open("token.tmp", "r") as f:
                token = f.read()
        except Exception as e:
            print(e)
            token = "Need a new token"
        return token

    def __renew_token__(self):
        """
        刷新 token.tmp 配置中存储的 token
        """
        token = requests.post(
            url="https://yunxiao.xiaogj.com/api/cs-crm/teacher/loginByPhonePwd",
            json={
                "_t_": UsedTime.stamp,
                "password": self.pwd,
                "phone": self.user,
                "userType": 1
            }
        ).json()["data"]["token"]

        token = requests.get(
            url="https://yunxiao.xiaogj.com/api/cs-crm/teacher/businessLogin",
            headers={"x3-authentication": token},
            params={"_t_": UsedTime.stamp}
        ).json()["data"]["token"]

        self.__token__ = token
        with open(f"token.tmp", "w") as f:
            f.write(token)
        logging.info("成功刷新 TOKEN")

    def __check_token__(self):
        """
        测试 token 是否有效.
        """
        url = f"https://yunxiao.xiaogj.com/api/cs-crm/teacher/hasPassword?_t_={UsedTime.stamp}"
        headers = {"content-type": "application/json;charset=UTF-8", "x3-authentication": self.__token__}
        res = requests.get(url, headers=headers)
        code = res.json()["code"]
        return code


class WebOAuth(YunXiao):

    def __init__(self, phone: str, password: str):
        """
        获取一个配置好鉴权的 Request Session
        :param phone:
        :param password:
        """
        super().__init__(phone, password)
        self.user = phone
        self.pwd = password

        while self.__check_cookie() != 200:
            logging.warning("Cookie 失效，准备刷新")
            self.__renew_cookie__()
            time.sleep(2)
        else:
            logging.info("Cookie 有效")

        self.__cookie__ = self.__read_cookie__()
        self.session = requests.session()
        self.session.headers.update({"cookie": self.__cookie__})

    @staticmethod
    def __read_cookie__():
        """
        读取存储的 cookie
        """
        # logging.info("正在读取配置文件")
        try:
            with open("cookie.tmp", "r") as f:
                cookie = f.read()
        except Exception as e:
            print(e)
            cookie = "Need a new cookie"
        return cookie

    def __renew_cookie__(self):
        """
        刷新 cookie.tmp 配置中存储的 cookie
        """
        # logging.debug("开始刷新 Cookie")
        res = requests.post(
            url="https://yunxiao.xiaogj.com/api/ua/login/password",
            params={
                "productCode": 1,
                "terminalType": 2,
                "userType": 1,
                "channel": "undefined"
            },
            json={
                "_t_": UsedTime.stamp,
                "clientId": "x3_prd",
                "password": self.pwd,
                "username": self.user,
                "redirectUri": "https://yunxiao.xiaogj.com/web/teacher/#/home/0",
                "errUri": "https://yunxiao.xiaogj.com/web/simple/#/login-error"
            },
            allow_redirects=False
        )
        res1 = requests.Session().get(
            url=res.json()["data"],
            cookies=res.cookies,
            allow_redirects=False
        )

        cookie1 = "UASESSIONID=" + requests.utils.dict_from_cookiejar(res.cookies)["UASESSIONID"]
        cookie2 = "SCSESSIONID=" + requests.utils.dict_from_cookiejar(res1.cookies)["SCSESSIONID"]
        headers = {"cookie": cookie1 + "; " + cookie2}

        res2 = requests.Session().get(
            url=res1.headers["location"],
            headers=headers,
            allow_redirects=False
        )

        res3 = requests.Session().get(
            url=res2.headers["location"],
            headers=headers,
            allow_redirects=False
        )

        cookie3 = "SCSESSIONID=" + requests.utils.dict_from_cookiejar(res3.cookies)["SCSESSIONID"]

        cookie = cookie1 + "; " + cookie3

        with open(f"cookie.tmp", "w") as f:
            f.write(cookie)
        logging.info("成功刷新 Cookie")

    def __check_cookie(self):
        """
        测试 cookie 是否有效.
        """
        cookie = self.__read_cookie__()
        code = requests.get(
            url=f"https://yunxiao.xiaogj.com/api/cs-pc-crm/teacher/businessLogin?_t_={UsedTime.stamp}",
            headers={"cookie": cookie}
        ).json()["code"]
        return code
