'''This module defines calculations engine components.'''
from logging import debug
import pandas as pd
from frostaura.data_access.public_asset_data_access import IPublicAssetDataAccess
from frostaura.engines.asset_calculations_engine import IAssetCalculationsEngine
from frostaura.models import ProfitCalculationResult

class SimpleAssetCalculationsEngine(IAssetCalculationsEngine):
    '''Calculations-related functionality using some maths under-the-hood.'''

    def __init__(self, public_asset_data_access: IPublicAssetDataAccess, config: dict = {}):
        self.public_asset_data_access = public_asset_data_access
        self.config = config

    def __calculate_holdings_ratios__(self, holdings: pd.DataFrame) -> pd.DataFrame:
        '''Determine the ratios that each asset makes up of the overall portfolio adding up to 1.'''

        def determine_usd(row: dict) -> float:
            history: pd.DataFrame = self.public_asset_data_access.get_symbol_history(symbol=row['symbol'])

            return row['shares'] * history.loc[row.name].Close

        holdings_with_usd: pd.DataFrame = holdings.copy()
        holdings_with_usd['usd'] = holdings.apply(determine_usd, axis=1)
        grouped_holdings: pd.DataFrame = holdings_with_usd.groupby(['name', 'symbol'], as_index=False).sum()
        holding_names: list = grouped_holdings['name'].value_counts().index.values
        holding_symbols: list = grouped_holdings['symbol'].value_counts().index.values
        data: dict = {
            'name': holding_names,
            'symbol': holding_symbols,
            'ratio': list()
        }

        for row_index, row in grouped_holdings.iterrows():
            data['ratio'].append(row['usd'] / grouped_holdings['usd'].sum())

        return pd.DataFrame(data)

    def calculate_holdings_profits(self, holdings: pd.DataFrame) -> pd.DataFrame:
        '''Determine individual asset profit ratio & profit USD and interpolate them into a copy of the given holdings.'''

        holding_names: list = holdings['name'].value_counts().index.values
        holding_symbols: list = holdings['symbol'].value_counts().index.values
        data: dict = {
            'name': holding_names,
            'symbol': holding_symbols,
            'total_purchased_usd': list(),
            'total_purchased_shares': list(),
            'total_current_usd': list(),
            'total_profit_ratio': list(),
            'total_profit_usd': list()
        }

        for holding_symbol in holding_symbols:
            debug(f'Calculating profit for asset "{holding_symbol}".')

            transactions_by_date_asc: pd.DataFrame = holdings \
                                                        .loc[holdings['symbol'] == holding_symbol] \
                                                        .sort_index(ascending=True)
            history: pd.DataFrame = self.public_asset_data_access.get_symbol_history(symbol=holding_symbol)
            total_purchased_usd: float = 0
            total_purchased_shares: float = 0

            for transaction_date, row in transactions_by_date_asc.iterrows():
                transaction_value: float = row['shares']
                transaction_close: float = history.loc[transaction_date]['Close']

                debug(f'[{holding_symbol}] Processing transaction value ${transaction_value} on {transaction_date}.')

                total_purchased_usd += transaction_close * transaction_value
                total_purchased_shares += transaction_value

            total_current_usd: float = history.iloc[-1]['Close'] * total_purchased_shares

            if total_current_usd > 1:
                data['total_purchased_usd'].append(total_purchased_usd)
                data['total_purchased_shares'].append(total_purchased_shares)
                data['total_current_usd'].append(total_current_usd)
                data['total_profit_ratio'].append((1 - min(total_purchased_usd, total_current_usd) / max(total_purchased_usd, total_current_usd)) * 100)
                data['total_profit_usd'].append(total_current_usd - total_purchased_usd)
            else:
                data['total_purchased_usd'].append(0)
                data['total_purchased_shares'].append(0)
                data['total_current_usd'].append(0)
                data['total_profit_ratio'].append(0)
                data['total_profit_usd'].append(0)

        ratios: pd.DataFrame = self.__calculate_holdings_ratios__(holdings=holdings)

        return pd.DataFrame(data).set_index('symbol').join(other=ratios.drop(columns=['name']).set_index('symbol')).reset_index()

    def calculate_holdings_profit(self, holdings: pd.DataFrame) -> ProfitCalculationResult:
        '''Determine the holdings profit percentage & profit USD, given the holdings.'''

        debug('Calculating overall holdings profits.')

        holdings_profits: pd.DataFrame = self.calculate_holdings_profits(holdings=holdings)
        total_purchased_usd: float = holdings_profits['total_purchased_usd'].sum()
        total_current_usd: float = holdings_profits['total_current_usd'].sum()
        total_profit_ratio: float = (1 - min(total_purchased_usd, total_current_usd) / max(total_purchased_usd, total_current_usd)) * 100
        total_profit_usd: float = total_current_usd - total_purchased_usd

        return ProfitCalculationResult(percentage=total_profit_ratio, value=total_profit_usd)
