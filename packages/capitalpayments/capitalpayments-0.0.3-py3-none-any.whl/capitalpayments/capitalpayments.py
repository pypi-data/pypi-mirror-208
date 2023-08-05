from url_manager import url_manager
import requests

class CapitalPayments:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
    def getLogin(self):
        response = requests.get(
            url_manager['login'], 
            headers = {'Content-Type': 'application/json'},
            auth = (self.api_key, self.api_secret)
        )
        return response.json()
    def getAccount(self):
        response = requests.get(
            url_manager['get_account'], 
            headers = {'Content-Type': 'application/json'},
            auth = (self.api_key, self.api_secret)
        )
        return response.json()
    def getBalance(self):
        response = requests.get(
            url_manager['get_balance'], 
            headers = {'Content-Type': 'application/json'},
            auth = (self.api_key, self.api_secret)
        )
        return response.json()
    def getEnvironment(self):
        response = requests.get(
            url_manager['get_environment'], 
            headers = {'Content-Type': 'application/json'},
            auth = (self.api_key, self.api_secret)
        )
        return response.json()
    def getMainWallet(self):
        response = requests.get(
            url_manager['get_main_wallet'], 
            headers = {'Content-Type': 'application/json'},
            auth = (self.api_key, self.api_secret)
        )
        return response.json()
    def getWallets(self):
        response = requests.get(
            url_manager['get_wallets'], 
            headers = {'Content-Type': 'application/json'},
            auth = (self.api_key, self.api_secret)
        )
        return response.json()
    def createInvoice(self,data):
        response = requests.post(
            url_manager['create_invoice'], 
            headers = {'Content-Type': 'application/json'},
            auth = (self.api_key, self.api_secret),
            json = data
        )
        return response.json()
    def cancelInvoice(self,data):
        if data.get('invoice_id'):
            response = requests.post(
                url_manager['cancel_invoice'], 
                headers = {'Content-Type': 'application/json'},
                auth = (self.api_key, self.api_secret),
                json = data
            )
            return response.json()
        else: 
            raise TypeError("Not invoice id")
    def getInvoiceStatus(self,data):
        if data.get('invoice_id'):
            response = requests.post(
                url_manager['get_invoice_status'], 
                headers = {'Content-Type': 'application/json'},
                auth = (self.api_key, self.api_secret),
                json = data
            )
            return response.json()
        else: 
            raise TypeError("Not invoice id")
    def createPayout(self,data):
        if data.get('amount'):
            if data.get('address'):
                response = requests.post(
                    url_manager['create_payout'], 
                    headers = {'Content-Type': 'application/json'},
                    auth = (self.api_key, self.api_secret),
                    json = data
                )
                return response.json()
            else: 
                raise TypeError("Not address")
        else: 
            raise TypeError("Not ammount")
    def cancelPayout(self,data):
        if data.get('payout_id'):
            response = requests.post(
                url_manager['cancel_payout'], 
                headers = {'Content-Type': 'application/json'},
                auth = (self.api_key, self.api_secret),
                json = data
            )
            return response.json()
        else: 
            raise TypeError("Not payout id")
    def getPayoutStatus(self,data):
        if data.get('payout_id'):
            response = requests.post(
                url_manager['get_payout_status'], 
                headers = {'Content-Type': 'application/json'},
                auth = (self.api_key, self.api_secret),
                json = data
            )
            return response.json()
        else: 
            raise TypeError("Not payout id")