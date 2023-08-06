'''This module defines public asset data access components.'''
import pandas as pd
from frostaura.models.symbol_data import SymbolData

class IPublicAssetDataAccess:
    '''Component to perform functions related to public assets.'''

    def get_symbol_history(self, symbol: str) -> pd.DataFrame:
        '''Get historical price movements for a given symbol.'''

        raise NotImplementedError()

    def get_symbol_info(self, symbol: str) -> SymbolData:
        '''Get the data for a specific symbol.'''

        raise NotImplementedError()

    def augment_symbols_info(self, symbols: pd.DataFrame) -> pd.DataFrame:
        '''Add info to a daraframe containing symbols.'''

        raise NotImplementedError()
