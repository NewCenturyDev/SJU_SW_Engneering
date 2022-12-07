import requests
import logging

from src.common.singleton import MetaSingleton
from src.login.credential_manager import CredentialManager


class StockBalanceServ(metaclass=MetaSingleton):
    _api = None
    _credentail_manager = None

    def __init__(self, api):
        self._api = api
        self._credentail_manager = CredentialManager()

    def fetch_cash_balance(self):
        try:
            return self._api.get_kr_buyable_cash()
        except Exception as err:
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            logger.error(str(err), exc_info=True)
            raise err

    def fetch_stock_balance(self):
        # 증권사에서는 제공하지만 pykis library에 없는 API 직접 호출
        key_info = self._credentail_manager.get_key_info()
        account_info = self._credentail_manager.get_account_info()
        tr_id = "TTTC8434R"
        if self._credentail_manager.get_account_idx() == 0:
            tr_id = "VTTC8434R"
        try:
            stock_balance = requests.get(
                url=self._api.domain.get_url("/uapi/domestic-stock/v1/trading/inquire-balance"),
                headers={
                    "content-type": "application/json; charset=utf-8",
                    "authorization": self._api.token.value,
                    "appkey": key_info["appkey"],
                    "appsecret": key_info["appsecret"],
                    "tr_id": tr_id
                }, params={
                    "CANO": account_info["account_code"],
                    "ACNT_PRDT_CD": account_info["product_code"],
                    "AFHR_FLPR_YN": "N",
                    "OFL_YN": "",
                    "INQR_DVSN": "02",
                    "UNPR_DVSN": "01",
                    "FUND_STTL_ICLD_YN": "N",
                    "FNCG_AMT_AUTO_RDPT_YN": "N",
                    "PRCS_DVSN": "01",
                    "CTX_AREA_FK100": "",
                    "CTX_AREA_NK100": ""
                }
            )
            balance_rows = []
            for output in stock_balance.json()["output1"]:
                balance_rows.append(
                    (output["pdno"], output["prdt_name"], output["hldg_qty"], output["prpr"], output["pchs_avg_pric"],
                     output["pchs_amt"], output["evlu_amt"], output["evlu_pfls_amt"],)
                )
            return balance_rows
        except Exception as err:
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            logger.error(str(err), exc_info=True)
            return []

    def fetch_stock_detail(self, new_stock):
        # 증권사에서는 제공하지만 pykis library에 없는 API 직접 호출
        key_info = self._credentail_manager.get_key_info()
        try:
            basic_detail_res = requests.get(
                url="https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/search-info",
                headers={
                    "content-type": "application/json; charset=utf-8",
                    "authorization": self._api.token.value,
                    "appkey": key_info["appkey"],
                    "appsecret": key_info["appsecret"],
                    "tr_id": "CTPF1604R",
                    "custtype": "P"
                }, params={
                    "PDNO": new_stock.get_code(),
                    "PRDT_TYPE_CD": "300"  # 300 국내주식 / 512 미국 나스닥 / 513 미국 뉴욕 / 529 미국 아멕스
                }
            )
            new_stock.set_name(basic_detail_res.json()["output"]["prdt_abrv_name"])
            advance_detail_raw_res = requests.get(
                url=self._api.domain.get_url("/uapi/domestic-stock/v1/quotations/inquire-price"),
                headers={
                    "content-type": "application/json; charset=utf-8",
                    "authorization": self._api.token.value,
                    "appkey": key_info["appkey"],
                    "appsecret": key_info["appsecret"],
                    "tr_id": "FHKST01010100"
                }, params={
                    "FID_COND_MRKT_DIV_CODE": "J",
                    "FID_INPUT_ISCD": new_stock.get_code()
                }
            )
            advance_detail_res = advance_detail_raw_res.json()["output"]
            new_stock.set_advance_details(
                advance_detail_res["rprs_mrkt_kor_name"],
                advance_detail_res["bstp_kor_isnm"],
                advance_detail_res["stck_prpr"],
                advance_detail_res["acml_vol"],
                advance_detail_res["aspr_unit"]
            )
            return new_stock
        except Exception as err:
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            logger.error(str(err), exc_info=True)
