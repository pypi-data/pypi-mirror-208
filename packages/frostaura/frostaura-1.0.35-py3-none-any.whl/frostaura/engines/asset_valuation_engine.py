'''This module defines valuation engine components.'''
from frostaura.models.symbol_data import SymbolData
from frostaura.models.valuation_result import ValuationResult

class IAssetValuationEngine:
    '''Component to perform functions related to asset valuation.'''

    def valuate(self, symbol_data: SymbolData) -> ValuationResult:
        '''Valuate a given asset.'''

        raise NotImplementedError()
