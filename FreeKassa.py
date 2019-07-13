import requests
import hashlib

class FK:
    API_URL = 'https://www.fkwallet.ru/api_v1.php'

    token = '1'
    merchant_id = 139031
    secret_word = '02cc7188'
    wallet_id = '1'

    def generate_hash(self, amount, type, order_id=None):
        md5 = hashlib.md5()
        string = ''
        if type == 'get':
            string_args = f'{self.merchant_id}:{amount}:{self.secret_word}:{order_id}'
            print(string_args)
            md5.update(string_args.encode()) 
            string = md5.hexdigest()
        
        return string


    def generate_link(self, amount, id, other_params = None):
        print(amount, id)
        hash = self.generate_hash(amount, "get", id)
        url = f'http://www.free-kassa.ru/merchant/cash.php?m={self.merchant_id}&oa={amount}&o={id}&s={hash}'
        if other_params:
            url = url + '&' + other_params
            
        return url



