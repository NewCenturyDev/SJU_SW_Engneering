# Import External Packages
import json
import os
import pykis

# Import Internal Packages
import file_config


class CredentialManager:
    # Data Fields
    credentials_file = os.path.join(file_config.ROOT_DIR, "credential.json")
    credentails_info = None
    api = None

    def get_api(self):
        return self.api

    def load_credentials(self, account_idx, callback):
        with open(self.credentials_file, 'r') as file:
            self.credentails_info = json.load(file)
            if account_idx == 0:
                self.api = pykis.Api(
                    domain_info=pykis.DomainInfo(kind="virtual"),
                    key_info=self.credentails_info["secret_test"],
                    account_info=self.credentails_info["account_test"]
                )
            else:
                self.api = pykis.Api(
                    key_info=self.credentails_info["secret"],
                    account_info=self.credentails_info["account"]
                )
            callback()
