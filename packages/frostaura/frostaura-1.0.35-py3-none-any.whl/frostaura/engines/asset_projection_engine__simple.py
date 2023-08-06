'''This module defines projection engine components.'''
import pandas as pd
from frostaura.models.symbol_data import SymbolData
import inflect
from frostaura.engines.asset_projection_engine import IAssetProjectionEngine
from frostaura.engines.asset_valuation_engine import IAssetValuationEngine
from frostaura.models.valuation_result import ValuationResult
from frostaura.data_access.public_asset_data_access import IPublicAssetDataAccess

class SimpleAssetProjectionEngine(IAssetProjectionEngine):
    '''Calculations-related functionality using some maths under-the-hood.'''

    def __init__(self,
                 asset_valuation_engine: IAssetValuationEngine,
                 public_asset_data_access: IPublicAssetDataAccess,
                 config: dict = {}):
        self.asset_valuation_engine = asset_valuation_engine
        self.public_asset_data_access = public_asset_data_access
        self.config = config
        self.inflect_engine = inflect.engine()

    def project_monthly_asset_growth(self,
                                     n_months: int,
                                     symbol: str,
                                     principal_value: float,
                                     monthly_deposit: float = 0) -> pd.DataFrame:
        '''Determine an asset's growth at a given annual rate over a specified number of months while applying a monthly deposit.'''

        symbol_data: SymbolData = self.public_asset_data_access.get_symbol_info(symbol=symbol)
        valuation: ValuationResult = self.asset_valuation_engine.valuate(symbol_data=symbol_data)
        annual_growth_rate: float = symbol_data.annual_growth_projected
        divident_payout_frequency_in_months: int = valuation.divident_payout_frequency_in_months
        data = {
            'month': list(),
            'deposits_withdrawals': list(),
            'interest': list(),
            'total_deposits_withdrawals': list(),
            'accrued_interest': list(),
            'balance': list()
        }

        data['month'].append(0)
        data['deposits_withdrawals'].append(0)
        data['interest'].append(0)
        data['total_deposits_withdrawals'].append(0)
        data['accrued_interest'].append(0)
        data['balance'].append(principal_value)

        for i in range(1, n_months + 1):
            data['month'].append(i)
            data['deposits_withdrawals'].append(monthly_deposit)
            
            interest: float = (annual_growth_rate / 12) * data['balance'][-1]

            if divident_payout_frequency_in_months > 0 and i % divident_payout_frequency_in_months == 0:
                annual_dividend_rate: float = valuation.annual_dividend_percentage / 100
                interest += (annual_dividend_rate / 12 / divident_payout_frequency_in_months) * data['balance'][-1]

            data['interest'].append(interest)
            data['accrued_interest'].append(data['accrued_interest'][-1] + data['interest'][-1])
            data['total_deposits_withdrawals'].append(data['total_deposits_withdrawals'][-1] + monthly_deposit)
            data['balance'].append(data['interest'][-1] + data['balance'][-1] + monthly_deposit)

        response: pd.DataFrame = pd.DataFrame(data)

        return response.set_index('month')

    def project_monthly_holdings_growth(self,
                                   n_months: int,
                                   holdings_with_profits: pd.DataFrame,
                                   monthly_deposits: list) -> pd.DataFrame:
        '''Determine a comprehensive holdings growth at a given annual rates over a specified numbers of months while applying a monthly deposits.'''

        annual_growth_rates: list = list()
        principal_values: list = list()
        symbols: list = list()

        for row_index, row in holdings_with_profits.iterrows():
            try:
                symbol_data: SymbolData = self.public_asset_data_access.get_symbol_info(symbol=row['symbol'])
                symbol_valuation: ValuationResult = self.asset_valuation_engine.valuate(symbol_data=symbol_data)
                annual_growth_rate: float = symbol_data.annual_growth_projected

                if symbol_valuation.annual_dividend_percentage is not None:
                    annual_growth_rate += (symbol_valuation.annual_dividend_percentage / 100)

                annual_growth_rates.append(annual_growth_rate)
                principal_values.append(row['total_current_usd'])
                symbols.append(row['symbol'])
            except Exception:
                pass

        projections: list = list()

        for month_index in range(len(annual_growth_rates)):
            projection = self.project_monthly_asset_growth(n_months=n_months,
                                                           symbol=symbols[month_index],
                                                           principal_value=principal_values[month_index],
                                                           monthly_deposit=monthly_deposits[month_index])

            projections.append(projection)

        data = {
            'month': list(),
            'deposits_withdrawals': list(),
            'interest': list(),
            'total_deposits_withdrawals': list(),
            'accrued_interest': list(),
            'balance': list()
        }

        for month_index in range(1, n_months + 1):
            data['month'].append(month_index)
            data['deposits_withdrawals'].append(sum([p.loc[month_index]['deposits_withdrawals'] for p in projections]))

            previous_row_balances: float = sum([p.loc[month_index - 1]['balance'] for p in projections])
            current_row_balances: float = sum([p.loc[month_index]['balance'] for p in projections])
            current_deposits: float = sum([p.loc[month_index]['deposits_withdrawals'] for p in projections])
            interest = 1 - previous_row_balances / (current_row_balances - current_deposits)

            data['interest'].append(interest)
            data['total_deposits_withdrawals'].append(sum([p.loc[month_index]['total_deposits_withdrawals'] for p in projections]))
            data['accrued_interest'].append(sum([p.loc[month_index]['accrued_interest'] for p in projections]))
            data['balance'].append(sum([p.loc[month_index]['balance'] for p in projections]))

        return pd.DataFrame(data)

    def project_wealth_growth(self,
                              holdings_with_profits: pd.DataFrame,
                              monthly_deposits: list,
                              n_months: int = 12 * 50, # 50 Years
                              min_amount: float = 1,
                              max_amount: float = 100 * 1000 * 10 * 1000 * 10, # Ten Billion
                              factorials_of: int = 10) -> pd.DataFrame:
        '''Determine wealth growth at a given annual rates over a specified numbers of months while applying a monthly deposits.'''

        factorials_of: int = 10
        holdings_growth: pd.DataFrame = self.project_monthly_holdings_growth(n_months=n_months,
                                                                             holdings_with_profits=holdings_with_profits,
                                                                             monthly_deposits=monthly_deposits)
        current_amount_to_project_calculation: float = min_amount
        data = {
            'Target Balance (USD)': list(),
            'Target Balance Eng (USD)': list(),
            'ETA (Months)': list(),
            'ETA (Years)': list()
        }
        current_balance: float = holdings_with_profits['total_current_usd'].sum()

        while current_amount_to_project_calculation <= max_amount:
            projections: int = holdings_growth.loc[holdings_growth['balance'] > current_amount_to_project_calculation]

            if current_balance > current_amount_to_project_calculation:
                current_amount_to_project_calculation *= factorials_of
                continue

            if projections.shape[0] <= 0:
                break

            data['Target Balance (USD)'].append(projections.iloc[0]["balance"])
            data['Target Balance Eng (USD)'].append(self.inflect_engine.number_to_words(projections.iloc[0]["balance"]))
            data['ETA (Months)'].append(projections.index[0])
            data['ETA (Years)'].append(projections.index[0] / 12)
            
            current_amount_to_project_calculation *= factorials_of

        return pd.DataFrame(data)