# Import External Packages
import json
import os
import pykis

# Import Internal Packages
import file_config


# Import Internal Packages
from src.common.singleton import MetaSingleton


class CredentialManager(metaclass=MetaSingleton):
    # Data Fields
    _account_idx = None
    _credentials_file = os.path.join(file_config.ROOT_DIR, "credential.json")
    _credentails_info = None
    _key_info = None
    _account_info = None
    _api = None

    def get_api(self):
        return self._api

    def load_credentials(self, account_idx, callback):
        self._account_idx = account_idx
        file = open(self._credentials_file, 'r')
        self._credentails_info = json.load(file)
        if account_idx == 0:
            self._key_info = self._credentails_info["secret_test"]
            self._account_info = self._credentails_info["account_test"]
            self._api = pykis.Api(
                domain_info=pykis.DomainInfo(kind="virtual"),
                key_info=self._credentails_info["secret_test"],
                account_info=self._credentails_info["account_test"]
            )
        else:
            self._key_info = self._credentails_info["secret"]
            self._account_info = self._credentails_info["account"]
            self._api = pykis.Api(
                key_info=self._credentails_info["secret"],
                account_info=self._credentails_info["account"]
            )
        file.close()
        callback()
            
    def get_account_idx(self):
        # 0 == 모의투자, 1 == 실전투자
        return self._account_idx

    def get_key_info(self):
        if self._account_idx == 0:
            return self._credentails_info["secret_test"]
        else:
            return self._credentails_info["secret"]

    def get_account_info(self):
        if self._account_idx == 0:
            return self._credentails_info["account_test"]
        else:
            return self._credentails_info["account"]
