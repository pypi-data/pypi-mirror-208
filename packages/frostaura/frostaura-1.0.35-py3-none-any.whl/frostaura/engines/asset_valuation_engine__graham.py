'''This module defines valuation engine components.'''
from frostaura.data_access import IPublicAssetDataAccess
from frostaura.data_access import IResourcesDataAccess
from frostaura.models.valuation_result import ValuationResult
from frostaura.models.symbol_data import SymbolData
from frostaura.engines.asset_valuation_engine import IAssetValuationEngine

class GrahamValuationEngine(IAssetValuationEngine):
    '''Valuation-related functionality using the discounted free cash flow method.'''
    margin_of_safety: float = 0.5

    def __init__(self, html_data_access: IResourcesDataAccess, public_asset_data_access: IPublicAssetDataAccess, config: dict = {}):
        self.html_data_access = html_data_access
        self.public_asset_data_access = public_asset_data_access
        self.config = config

    def __determine_intrinsic_value__(self,
                                      eps: float,
                                      pe_base_non_growth_company: float,
                                      annual_growth_projected: float,
                                      average_yield_of_aaa_corporate_bonds: float,
                                      current_yield_of_aaa_corporate_bonds: float) -> float:
        value: float = eps * (pe_base_non_growth_company + 2 * annual_growth_projected) * average_yield_of_aaa_corporate_bonds / current_yield_of_aaa_corporate_bonds

        return value

    def valuate(self, symbol_data: SymbolData) -> ValuationResult:
        '''Valuate a given asset.'''
        try:
            valuation: float = self.__determine_intrinsic_value__(eps=symbol_data.eps,
                                                                pe_base_non_growth_company=symbol_data.pe_base_non_growth_company,
                                                                annual_growth_projected=symbol_data.annual_growth_projected*100,
                                                                average_yield_of_aaa_corporate_bonds=symbol_data.average_yield_of_aaa_corporate_bonds,
                                                                current_yield_of_aaa_corporate_bonds=symbol_data.current_yield_of_aaa_corporate_bonds)

            return ValuationResult(
                symbol=symbol_data.symbol,
                company_name=symbol_data.company_name,
                current_price=symbol_data.current_price,
                valuation_price=valuation,
                valuation_method='benjamin_graham_valuation',
                margin_of_safety=self.margin_of_safety
            )
        except Exception:
            return None
