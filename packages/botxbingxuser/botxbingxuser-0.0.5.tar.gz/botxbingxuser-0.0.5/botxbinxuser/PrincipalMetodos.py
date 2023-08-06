

import urllib.parse
import hashlib
import hmac
import requests
import time
import json
from datetime import datetime

api_url         = "https://open-api.bingx.com"

API_key         = 'yourAPI_Key'
Secrect_Key     = 'yourSecrect_Key'

infoGet         = 'GET'
infoPost        = 'POST'
infoDelete      ='DELETE'

url_balance          =     '/openApi/swap/v2/user/balance'
url_new_order        =     '/openApi/swap/v2/trade/order'
url_cancel_order     =     '/openApi/swap/v2/trade/order'
url_getopenorder     =     '/openApi/swap/v2/trade/openOrders'
url_getIdopenorder   =     '/openApi/swap/v2/trade/order'
url_getpositions     =     '/openApi/swap/v2/user/positions'
url_cancelall_order  =     '/openApi/swap/v2/trade/allOpenOrders'
url_getKlines        =     '/openApi/swap/v2/quote/klines'
url_closeorder       =     '/openApi/swap/v2/trade/closeAllPositions'


class Client:
        def __init__(self,API_key,Secrect_Key):
            self.API_key = API_key
            self.Secrect_Key = Secrect_Key


        
        


        def getbalance(self):


            time_stamp=int(time.time() * 10 ** 3) 
            data = {
                        'recvWindow':   15000,
                        "timestamp": time_stamp
                    }
            
            return self.xbingx_request(url_balance, data, self.API_key, self.Secrect_Key,infoGet) 



        def neworder(self,type,side,symbol,**params):

            time_stamp=int(time.time() * 10 ** 3) 
            
            """exemplos de new order:
            #preco =float(envio['price'])*0.98
            #resposta = neworder(type = "LIMIT",side="BUY",quantity=0.001,price=preco,symbol="BTC-USDT")
            #resposta=neworder(type=envio['type'],price=envio['price'],quantity=envio['quantity'],side=envio['side'],symbol=envio['symbol'])
            #print(resposta)"""
            
            """LIMIT	quantity, price
            MARKET	quantity
            TRIGGER_LIMIT	quantity, stopPrice, price
            STOP_MARKET, TAKE_PROFIT_MARKET, TRIGGER_MARKET	quantity, stopPrice"""
            
            """De acordo com a opção escolhida, o neworder() recebe parametros adicionais"""
            
            data = {
                    'recvWindow':   15000,
                    'timestamp' :   time_stamp,
                    'symbol'    :   symbol,
                    'type'      :   type,
                    'side'      :   side,
                    **params  
                    
                    }
            return self.xbingx_request(url_new_order, data,self.API_key, self.Secrect_Key,infoPost) 
            
        

        def getopenorder(self):
            
            time_stamp=int(time.time() * 10 ** 3) 

        
            
            data = {
                            
                            "timestamp": time_stamp,
                            'recvWindow':   15000,
                            
                        }
                
            return self.xbingx_request(url_getopenorder, data,self.API_key, self.Secrect_Key,infoGet) 



        def Closeordens(self,**params):
            time_stamp=int(time.time() * 10 ** 3) 

            data={
                        'recvWindow':   15000,
                        'timestamp' :   time_stamp,
                        **params
                    
                    }
            
            return self.xbingx_request(url_closeorder, data, self.API_key, self.Secrect_Key,infoPost)



        def cancelarorder(self,id,symbol):
            
            time_stamp=int(time.time() * 10 ** 3) 


            data={
                        'recvWindow':   15000,
                        'timestamp' :   time_stamp,
                        'symbol'    :   symbol,
                        'orderId'   :   id
                    
                    }
        
            return self.xbingx_request(url_cancel_order, data,self.API_key, self.Secrect_Key,infoDelete) 



        def cancelallordens(self,symbol):

            time_stamp=int(time.time() * 10 ** 3) 


            data={
                        'recvWindow':   15000,
                        'timestamp' :   time_stamp,
                        'symbol'    :   symbol
                        
                    
                    }
            
            return self.xbingx_request(url_cancelall_order, data, self.API_key, self.Secrect_Key,infoDelete) 



        def getpositions(self,symbol):
            
            time_stamp=int(time.time() * 10 ** 3) 
            
            data={
                    "timestamp": time_stamp,
                    'recvWindow':   15000,
                    'symbol':symbol
                }
            return self.xbingx_request(url_getpositions, data,self.API_key, self.Secrect_Key,infoGet) 
            

        def xbingx_request(self,uri_path, data, api_key, api_sec,info):

        
            req=''
            headers = {}
            headers['X-BX-APIKEY'] = api_key
            signature = self.get_xbingx_signature(data, api_sec)
        
            params={
                    **data, 
                    "signature": signature
                    }
            
            if info=="GET":
                req = requests.get((api_url + uri_path), params=params, headers=headers)
                return req.json()

            elif info=='DELETE':
                req = requests.delete((api_url + uri_path), headers=headers, params=params)
                return req.json()


            elif info=='POST':

                req = requests.post((api_url + uri_path), headers=headers, data=params)
                return req.json()
               

        def get_xbingx_signature(self,data, secret):
            postdata = urllib.parse.urlencode(data)
            message = postdata.encode()
            byte_key = bytes(secret, 'UTF-8')
            mac = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
            return mac




