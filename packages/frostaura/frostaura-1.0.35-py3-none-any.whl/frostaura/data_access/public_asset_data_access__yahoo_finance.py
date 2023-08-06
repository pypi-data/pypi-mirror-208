'''This module defines Yahoo Finance data access components.'''
from frostaura.models.symbol_data import SymbolData
import yfinance as yf
import pandas as pd
import time
import requests
import json
from joblib import Parallel, delayed
from logging import info, warning
from frostaura.data_access.public_asset_data_access import IPublicAssetDataAccess

class YahooFinanceDataAccess(IPublicAssetDataAccess):
    '''Yahoo Finance public asset-related functionality.'''

    def __init__(self, config: dict = {}):
        self.config = config

    def __get_value__(self, root: dict, path: str, default: object = None) -> object:
        segments: list = path.split('.')
        context: dict = root

        for segment in segments:
            if not segment in context:
                return default

            context = context[segment]
        
        return context

    def __get_symbol_quote__(self, symbol: str, current_attempt: int=1, max_retry_count: int=3) -> dict:
        try:
            base_url: str = f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=assetProfile,defaultKeyStatistics,financialData,earningsTrend,price,summaryDetail'
            http_response = requests.get(base_url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
            })
            data = json.loads(http_response.text)
            symbol_quote = data['quoteSummary']['result'][0]
            response: dict = {
                'symbol': symbol,
                'eps': self.__get_value__(root=symbol_quote, path='defaultKeyStatistics.trailingEps.raw'),
                'long_description': self.__get_value__(root=symbol_quote, path='assetProfile.longBusinessSummary'),
                'company_name': self.__get_value__(root=symbol_quote, path='price.longName'),
                'market_cap': self.__get_value__(root=symbol_quote, path='price.marketCap.raw'),
                'current_price': self.__get_value__(root=symbol_quote, path='financialData.currentPrice.raw'),
                'total_cash': self.__get_value__(root=symbol_quote, path='financialData.totalCash.raw'),
                'total_debt': self.__get_value__(root=symbol_quote, path='financialData.totalDebt.raw'),
                'total_revenue': self.__get_value__(root=symbol_quote, path='financialData.totalRevenue.raw'),
                'pe_ratio': self.__get_value__(root=symbol_quote, path='summaryDetail.trailingPE.raw'),
                'ex_dividend_date': self.__get_value__(root=symbol_quote, path='summaryDetail.exDividendDate.raw'),
                'dividend_yield': self.__get_value__(root=symbol_quote, path='summaryDetail.dividendYield.raw'),
                'growth_rate': None
            }

            five_year_growth_periods: list = [t for t in self.__get_value__(root=data['quoteSummary']['result'][0], path='earningsTrend.trend', default=[]) if t['period'] == '+5y']

            if len(five_year_growth_periods) > 0:
                response['growth_rate'] = self.__get_value__(root=five_year_growth_periods[0], path='growth.raw')

            return response
        except Exception as ex:
            if current_attempt <= max_retry_count:
                print(f'Symbol "{symbol}" failed: "{ex}". Retrying {current_attempt}/{max_retry_count}.')
                time.sleep(current_attempt)

                return self.__get_symbol_quote__(symbol=symbol, current_attempt=current_attempt+1)

            return {}

    def __get_symbol_quotes_async__(self, symbols: list) -> list:
        parrallelizer: Parallel = Parallel(n_jobs=len(symbols), prefer='threads')
        results: list = parrallelizer([delayed(self.__get_symbol_quote__)(s) for s in symbols])

        return results

    def get_symbol_history(self, symbol: str) -> pd.DataFrame:
        '''Get historical price movements for a given symbol.'''

        info(f'Fetching historical price movements for symbol "{symbol}".')

        ticker = yf.Ticker(symbol)
        value = ticker.history(period='max')

        return value

    def get_symbol_info(self, symbol: str) -> SymbolData:
        '''Get the data for a specific symbol.'''
        quote: dict = self.__get_symbol_quote__(symbol=symbol)

        return SymbolData(symbol=quote['symbol'],
                          company_name=quote['company_name'],
                          current_price=quote['current_price'],
                          eps=quote['eps'],
                          annual_growth_projected=quote['growth_rate'])

    def augment_symbols_info(self, symbols: pd.DataFrame) -> pd.DataFrame:
        '''Add info to a daraframe containing symbols.'''

        __symbols__: pd.DataFrame = symbols.copy()
        __symbols__['quote'] = __symbols__['symbol'].apply(self.get_symbol_info)

        return __symbols__.sort_values('symbol').loc[__symbols__['quote'] != None]
