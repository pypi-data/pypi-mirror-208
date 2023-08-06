'''This module defines projection engine components.'''
import pandas as pd

class IAssetProjectionEngine:
    '''Component to perform functions related to asset projections.'''

    def project_monthly_asset_growth(self,
                                     n_months: int,
                                     symbol: str,
                                     principal_value: float,
                                     monthly_deposit: float) -> pd.DataFrame:
        '''Determine an asset's growth at a given annual rate over a specified number of months while applying a monthly deposit.'''

        raise NotImplementedError()

    def project_monthly_holdings_growth(self,
                                        n_months: int,
                                        holdings_with_profits: pd.DataFrame,
                                        monthly_deposits: list) -> pd.DataFrame:
        '''Determine a comprehensive holdings growth at a given annual rates over a specified numbers of months while applying a monthly deposits.'''

        raise NotImplementedError()

    def project_wealth_growth(self,
                              holdings_with_profits: pd.DataFrame,
                              monthly_deposits: list,
                              n_months: int,
                              min_amount: float,
                              max_amount: float,
                              factorials_of: int) -> pd.DataFrame:
        '''Determine wealth growth at a given annual rates over a specified numbers of months while applying a monthly deposits.'''

        raise NotImplementedError()
