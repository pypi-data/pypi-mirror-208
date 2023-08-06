import requests
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


