'''This module defines private manager components.'''
from cProfile import label
from datetime import datetime
import pandas as pd
from frostaura.data_access.notifications_data_access import INotificationsDataAccess
from frostaura.engines.visualization_engine import IVisualizationEngine
from frostaura.managers.asset_reporting_manager import IAssetReportingManager
from frostaura.data_access.personal_asset_data_access import IPersonalAssetDataAccess
from frostaura.engines.asset_calculations_engine import IAssetCalculationsEngine
from frostaura.engines.asset_projection_engine import IAssetProjectionEngine
from frostaura.models.profit_calculation_result import ProfitCalculationResult
from frostaura.engines.asset_valuation_engine import IAssetValuationEngine
from frostaura.data_access.public_asset_data_access import IPublicAssetDataAccess
from frostaura.models.symbol_data import SymbolData
from frostaura.models.visualization_types import VisualizationType
from frostaura.models.valuation_result import ValuationResult

class PersonalAssetReportingManager(IAssetReportingManager):
    '''Component to perform functions related to personal asset reporting.'''

    def __init__(self,
                 personal_asset_data_access: IPersonalAssetDataAccess,
                 asset_calculation_engine: IAssetCalculationsEngine,
                 asset_valuation_engine: IAssetValuationEngine,
                 asset_projection_engine: IAssetProjectionEngine,
                 visualization_engine: IVisualizationEngine,
                 personal_notification_data_access: INotificationsDataAccess,
                 public_asset_data_access: IPublicAssetDataAccess,
                 config: dict = {}):
        self.personal_asset_data_access = personal_asset_data_access
        self.asset_calculation_engine = asset_calculation_engine
        self.asset_valuation_engine = asset_valuation_engine
        self.asset_projection_engine = asset_projection_engine
        self.visualization_engine = visualization_engine
        self.personal_notification_data_access = personal_notification_data_access
        self.public_asset_data_access = public_asset_data_access
        self.config = config

    def __send_holdings_pie_chart__(self, holdings_with_profits: pd.DataFrame,):
        pie_fig, pie_ax = self.visualization_engine.get_figure(x='symbol',
                                                               y='ratio',
                                                               data=holdings_with_profits,
                                                               graph_type=VisualizationType.PIE,
                                                               title='Portfolio Assets')

        self.personal_notification_data_access.send_figure(figure=pie_fig)

    def __send_holdings_growth_projections__(self,
                                             holdings_with_profits: pd.DataFrame,
                                             n_months: int,
                                             monthly_deposits: list):
        holdings_growth = self.asset_projection_engine.project_monthly_holdings_growth(n_months=n_months,
                                                                                       holdings_with_profits=holdings_with_profits,
                                                                                       monthly_deposits=monthly_deposits)

        currency_format: str = '${x:,.0f}'
        fig, ax = self.visualization_engine.get_figure(x='month',
                                                       y='balance',
                                                       data=holdings_growth,
                                                       graph_type=VisualizationType.LINE,
                                                       title=f'Holdings Growth Projection | {int(n_months/12)} Years',
                                                       legend=True,
                                                       line_label=f'Balance | {currency_format.format(x=holdings_growth.iloc[-1]["balance"])}',
                                                       y_tick_format_str=currency_format)

        for i, r in holdings_growth.iterrows():
            # Draw a line for every 5 year.
            if r['month'] % (12 * 5) == 0:
                year: int = int(r['month'] / 12)
                ax.axvline(x=r['month'], linestyle='--', color='#11E5AD', label=f'Year {year} | {currency_format.format(x=r["balance"])}')

        fig.legends = [fig.legend()]
        percentage_increase_to_projected_time: float = round((holdings_growth.iloc[-1]['balance'] - holdings_growth.iloc[0]['balance']) / holdings_growth.iloc[0]['balance'] * 100, 2)

        self.personal_notification_data_access.send_text(f'<strong>Holdings Growth Projection ({int(n_months/12)} Years) |</strong> {percentage_increase_to_projected_time}%')
        self.personal_notification_data_access.send_figure(figure=fig)

    def __send_holdings_report__(self, holdings: list):
        overall_holdings_profit: ProfitCalculationResult = self.asset_calculation_engine.calculate_holdings_profit(holdings)

        self.personal_notification_data_access.send_text(f'<strong>Overall Holdings Profits:</strong> ${round(overall_holdings_profit.value, 2)} ({round(overall_holdings_profit.percentage if overall_holdings_profit.value > 0 else -overall_holdings_profit.percentage)}%)')

    def __send_wealth_projections_report__(self,
                                         holdings_with_profits: pd.DataFrame,
                                         monthly_deposits: float):
        wealth_projection = self.asset_projection_engine.project_wealth_growth(holdings_with_profits=holdings_with_profits,
                                                                               monthly_deposits=monthly_deposits)

        wealth_projection['Target Balance (USD)'] = wealth_projection['Target Balance (USD)'].apply(lambda v: int(v))
        wealth_projection['ETA (Years)'] = wealth_projection['ETA (Years)'].apply(lambda v: int(v))
        currency_format: str = '${x:,.0f}'
        fig, ax = self.visualization_engine.get_figure(x='ETA (Years)',
                                                       y='Target Balance (USD)',
                                                       data=wealth_projection,
                                                       graph_type=VisualizationType.LINE,
                                                       title='Wealth Projection | 30 Years',
                                                       legend=True,
                                                       line_label=wealth_projection.iloc[-1]['Target Balance (USD)'],
                                                       y_tick_format_str=currency_format)

        for i, r in wealth_projection.iterrows():
            ax.axhline(y=r['Target Balance (USD)'], linestyle='-', color='#11E5AD', label=currency_format.format(x=r['Target Balance (USD)']))

        fig.legends = [fig.legend()]

        self.personal_notification_data_access.send_text(text=f'<strong>Wealth Projection |</strong> 30 Years')
        self.personal_notification_data_access.send_figure(figure=fig)
        self.personal_notification_data_access.send_dataframe(dataframe=wealth_projection[['Target Balance (USD)', 'ETA (Months)', 'ETA (Years)']]
                                                                .rename(columns={
                                                                    'Target Balance (USD)': 'USD',
                                                                    'ETA (Months)': 'Months',
                                                                    'ETA (Years)': 'Years'
                                                                }))

    def __send_individual_asset_performance_reports__(self,
                                                      holdings: list,
                                                      holdings_with_profits: pd.DataFrame):
        currency_format: str = '${x:,.0f}'
        green: str = '#11E5AD'
        red: str = '#e55111'

        for row_index, row in holdings_with_profits.iterrows():
            symbol: str = row['symbol']
            company: str = row['name']
            current_total: float = currency_format.format(x=row['total_current_usd'])
            profit_percentage: float = round(row['total_profit_ratio'], 2)
            profit_absolute: float = row['total_profit_usd']
            transactions_for_symbol: list = holdings.loc[holdings['symbol'] == symbol]
            first_transaction_date: datetime = transactions_for_symbol.iloc[0].name
            history: pd.DataFrame = self.public_asset_data_access.get_symbol_history(symbol=symbol)
            history = history[first_transaction_date:].reset_index()

            if profit_absolute < 0:
                profit_percentage = -profit_percentage

            profit_absolute = currency_format.format(x=profit_absolute)

            message: str = f'<strong>{company} ({symbol})</strong> holdings currently amount to {current_total}. A {profit_absolute} ({profit_percentage}%) profit.'

            self.personal_notification_data_access.send_text(text=message)

            symbol_data: SymbolData = self.public_asset_data_access.get_symbol_info(symbol=symbol)
            symbol_valuation: ValuationResult = self.asset_valuation_engine.valuate(symbol_data=symbol_data)

            if symbol_valuation is None:
                return

            fig, ax = self.visualization_engine.get_figure(x='Date',
                                                           y='Close',
                                                           data=history,
                                                           graph_type=VisualizationType.LINE,
                                                           title=f'{company} ({symbol})',
                                                           subtitle=None if (symbol_valuation.annual_dividend_percentage is None or symbol_valuation.divident_payout_frequency_in_months == 0) else f'Dividend: {round(symbol_valuation.annual_dividend_percentage, 2)}% Annually ({symbol_valuation.divident_payout_frequency_in_months} Month Frequency)',
                                                           legend=True,
                                                           line_label=f'Current Value: {currency_format.format(x=history.iloc[-1]["Close"])} (Δ{round(profit_percentage, 2)}%)',
                                                           y_tick_format_str=currency_format)

            # Draw valuation line
            ax.axhline(y=symbol_valuation.fair_price,
                       linestyle='-',
                       color=red if symbol_valuation.is_overvalued else green,
                       label=f'Intrinsic Value: {currency_format.format(x=symbol_valuation.fair_price)} (Δ{round(symbol_valuation.absolute_current_v_valuation_delta*100, 2)}%)')

            for trow_index, trow in transactions_for_symbol.iterrows():
                transaction_date: datetime = trow.name
                price_at_transaction_date: float = history.loc[history['Date'] == transaction_date]['Close'].values[0]

                ax.plot(transaction_date,
                        price_at_transaction_date,
                        'ro',
                        color=red if price_at_transaction_date > symbol_valuation.current_price else green)

            fig.legends = [fig.legend()]

            self.personal_notification_data_access.send_figure(figure=fig)

    def send_reports(self):
        '''Generate and send asset reports.'''

        holdings: list = self.personal_asset_data_access.get_personal_transactions()
        holdings_with_profits: pd.DataFrame = self.asset_calculation_engine.calculate_holdings_profits(holdings=holdings)
        n_months_to_project: int = 12 * 5 # 5 Years
        usd_zar_exchange_rate: float = 16.17
        monthly_zar_deposit: float = 2000
        monthly_deposits: float = [(monthly_zar_deposit / usd_zar_exchange_rate / len(holdings_with_profits)) for h in holdings_with_profits]

        self.__send_holdings_report__(holdings=holdings)
        self.__send_holdings_pie_chart__(holdings_with_profits=holdings_with_profits)
        self.__send_holdings_growth_projections__(n_months=n_months_to_project,
                                                  monthly_deposits=monthly_deposits,
                                                  holdings_with_profits=holdings_with_profits)
        self.__send_individual_asset_performance_reports__(holdings=holdings,
                                                           holdings_with_profits=holdings_with_profits)
        self.__send_wealth_projections_report__(holdings_with_profits=holdings_with_profits,
                                                monthly_deposits=monthly_deposits)
