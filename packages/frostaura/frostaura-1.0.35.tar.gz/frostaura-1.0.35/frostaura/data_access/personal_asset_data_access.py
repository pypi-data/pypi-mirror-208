'''This module defines personal asset data access components.'''
import pandas as pd

class IPersonalAssetDataAccess:
    '''Component to perform functions related to personal / owned assets.'''

    def get_supported_assets(self) -> pd.DataFrame:
        '''Get all supported asset names and symbols.'''

        raise NotImplementedError()

    def get_personal_transactions(self) -> pd.DataFrame:
        '''Get all personal transactions made on an EasyEquities account.'''

        raise NotImplementedError()
