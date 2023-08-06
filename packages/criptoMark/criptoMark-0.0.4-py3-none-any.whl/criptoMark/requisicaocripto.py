
import requests
from datetime import datetime


def fear_and_greed(self,limite,formato,date_format):
   """Parametros:
      ----------
                  Limite      :  parametro de limite de retorno
                  formato     :  formato da resposta (`cvs` ou `json`)
                  date_format :  formato da data (`world`)

      Retorno:
      ----------
                 Retorna um dicionario da solicitação, no formato desejado 
                 

                  Response
                  {
                     "name": "Fear and Greed Index",
                     "data": [
                        {
                           "value": "40",
                           "value_classification": "Fear",
                           "timestamp": "1551157200",
                           "time_until_update": "68499"
                        },
                        {
                           "value": "47",
                           "value_classification": "Neutral",
                           "timestamp": "1551070800"
                        }
                     ],
                     "metadata": {
                        "error": null
                     }
                  }

                  """
     
 
   url= 'https://api.alternative.me/fng/?'
   parametros={
        'limit':limite,
        'format':formato,
        'date_format':date_format
    }
   response=requests.get(url=url,params=parametros)
    
   return dict(response.json())



def get_supported_future_markets():
   """Parametros:
      ----------
                  `Sem parametros`

                  

      Retorno:
      --------
                 [
                  {
                  "symbol": "string",
                  "exchange": "string",
                  "symbol_on_exchange": "string",
                  "base_asset": "string",
                  "quote_asset": "string",
                  "is_perpetual": true,
                  "margined": "STABLE",
                  "expire_at": 0,
                  "oi_lq_vol_denominated_in": "BASE_ASSET",
                  "has_long_short_ratio_data": true,
                  "has_ohlcv_data": true,
                  "has_buy_sell_data": true
                  }
                ]


   """
   url='https://api.coinalyze.net/v1/future-markets'
   headers={'api_key':'3412bd99-6be7-4b4f-8092-c441e37718ad'}
   response=requests.get(url=url,headers=headers)
   response=response.json()
   return response



def get_supported_exchanges():
   """Parametros:
      ---------
                  Sem parametros

      Retorno:
      --------
                  Retorna uma lista com simbolos das exchanges

                  [
                     {
                     "name": "string",
                     "code": "string"
                     }
                  ]


   """
   url='https://api.coinalyze.net/v1/exchanges'
   headers={'api_key':'3412bd99-6be7-4b4f-8092-c441e37718ad'}
   response=requests.get(url=url,headers=headers)
   response=response.json()
   return response


def getlong_short_ratio(symbols,interval,fron,to):
   """Parametros:
      ----------
                  symbols     :  simbolo da moeda
                  interval    :  intervalo >  `"1min" "5min" "15min" "30min" "1hour" "2hour" "4hour" "6hour" "12hour" "daily"`
                  fron/from   :  tempo em segundos do inicio da amostra > `From (inclusive), UNIX timestamp in seconds`
                  to          :  tempo em segundos do fim da amostra    > `From (inclusive), UNIX timestamp in seconds`

                  Exemplo     :  
                                                      #ano/mes/dia
                                 start_time = datetime(2023,5,11,23,0) 
                                                      #ano/mes/dia
                                 end_time = datetime(2023,5,12,1,0)

                                 fron = int(start_time.timestamp())
                                 to = int(end_time.timestamp())
                                 response = long_short(symbols='BTCUSDT_PERP.A',interval='5min',fron=fron,to=to)

      Retorno:
      -------
                  Retorna uma lista com a resposta da solicitação

                 [
                  {
                     "symbol": "string",
                     "history": [
                        {
                        "t": 0,  => The beginning of the interval, UNIX timestamp in seconds
                        "r": 0,  => Ratio
                        "l": 0,  => Long%
                        "s": 0   => Short%
                        }
                     ]
                  }
                ]


   """

   url='https://api.coinalyze.net/v1/long-short-ratio-history'
   headers={'api_key':'3412bd99-6be7-4b4f-8092-c441e37718ad'}
   
   parametros={
      
      'symbols'   :  symbols,
      'interval'  :  interval,
      'from'      :  fron,
      'to'        :  to
   }
   response=requests.get(url=url,headers=headers,params=parametros)
   response=response.json()
   return (response)


def get_current_open_interest(symbols:str,convert_to_usd:str):
    
    """Parametros:
      ---------
                  symbols: simbolo da moeda: `BTCUSDT_PERP.A`
                  convert_to_usd: se true retorna o valor em dolar (string)


      Retorno:
      --------
                  Retorna uma lista com o valor de open interest

                  [
                     {
                        "symbol": "string",
                        "value": 0,
                        "update": 0
                     }
                  ]


   """
    url='https://api.coinalyze.net/v1/open-interest'
    headers={'api_key':'3412bd99-6be7-4b4f-8092-c441e37718ad'}
   
    parametros={
      
      'symbols'         :  symbols,
      'convert_to_usd'  :  convert_to_usd
      
   }
    response=requests.get(url=url,headers=headers,params=parametros)
    response=response.json()
    return (response)


def get_current_funding_rate(symbols):
   """Parametros:
   --------------
                  symbols: simbolo `BTCUSD_PERP.0`

   Retorno:
   -------
                  Retorna 
                     [ 
                        {
                           symbol   :  string
                           value    :  number <double> Current funding rate ( % )
                           update	:  integer <int64>UNIX timestamp in milliseconds
                        }
                     ]

   """
   url='https://api.coinalyze.net/v1/funding-rate'
   headers={'api_key':'3412bd99-6be7-4b4f-8092-c441e37718ad'}
   
   parametros={
      
      'symbols'         :  symbols,
      
      
   }
   response=requests.get(url=url,headers=headers,params=parametros)
   response=response.json()
   return (response)
   

