'''This module defines Easy Equities data access components.'''
from datetime import datetime
from logging import debug, info
import json
import pandas as pd
from easy_equities_client.clients import EasyEquitiesClient
from easy_equities_client.accounts.types import Account
from frostaura.data_access.resources_data_access import IResourcesDataAccess
from frostaura.data_access.personal_asset_data_access import IPersonalAssetDataAccess

class EasyEquitiesPersonalAssetDataAccess(IPersonalAssetDataAccess):
    '''EasyEquities-related functionality.'''

    def __init__(self, resource_data_access: IResourcesDataAccess, username: str, password: str, config: dict = {}):
        self.resource_data_access = resource_data_access
        self.client = EasyEquitiesClient()
        self.username = username
        self.password = password
        self.config = config

    def __get_accounts__(self) -> list:
        info(f'Signing into EasyEquities as "{self.username}".')
        self.client.login(username=self.username, password=self.password)
        
        return self.client.accounts.list()

    def __get_account_by_name__(self, account_name: str) -> Account:
        accounts: list = self.__get_accounts__()
        
        debug(f'Filtering accounts list by name "{account_name}".')
        return [a for a in accounts if a.name == account_name][0]

    def __get_account_holdings__(self, account_name: str) -> list:
        account: Account = self.__get_account_by_name__(account_name=account_name)
        
        info(f'Getting account holdings for account "{account.name}" ({account.id}).')
        return self.client.accounts.holdings(account.id, include_shares=True)

    def __get_account_valuation__(self, account_name: str) -> list:
        account: Account = self.__get_account_by_name__(account_name=account_name)
        
        info(f'Getting account valuation for account "{account.name}" ({account.id}).')
        return self.client.accounts.valuations(account.id)

    def __get_excluded_assets__(self) -> list:
        with self.resource_data_access.get_resource(path='easy_equities_us_exclusions.json') as file:
            excluded_symbols: list = json.load(file)
            
            return excluded_symbols

    def get_supported_assets(self) -> pd.DataFrame:
        '''Get all supported asset names and symbols.'''

        info('Fetching EasyEquities supported symbols from a static source.')

        excluded_symbols: list = self.__get_excluded_assets__()

        with self.resource_data_access.get_resource(path='easy_equities_us_stocks.json') as file:
            company_names_symbols: list = json.load(file)
            data: dict = {
                'name': [c[0] for c in company_names_symbols if c[1] not in excluded_symbols],
                'symbol': [c[1] for c in company_names_symbols if c[1] not in excluded_symbols],
            }

            return pd.DataFrame(data)

    def get_personal_transactions(self) -> pd.DataFrame:
        '''Get all personal transactions made on an EasyEquities account.'''

        data: list = [
            ['Tesla Inc.', 'TSLA', 0.0688, datetime(2022, 7, 28, 0, 0)],
            ['3D Systems Corporation', 'DDD', 8.8925, datetime(2022, 8, 5, 0, 0)],
            ['3D Systems Corporation', 'DDD', 5.2957, datetime(2022, 8, 18, 0, 0)],
            ['SPDR S&P 500 ETF', 'SPY', 0.0829, datetime(2022, 8, 22, 0, 0)],
            ['3D Systems Corporation', 'DDD', 2.317, datetime(2022, 8, 22, 0, 0)],
            ['Tesla Inc.', 'TSLA', 0.0884, datetime(2022, 8, 29, 0, 0)],
            ['SPDR S&P 500 ETF', 'SPY', 0.0547, datetime(2022, 8, 29, 0, 0)],
            ['SPDR S&P 500 ETF', 'SPY', 0.4347, datetime(2022, 12, 19, 0, 0)]
        ]

        return pd.DataFrame(data, columns =['name', 'symbol', 'shares', 'date']).set_index('date')
