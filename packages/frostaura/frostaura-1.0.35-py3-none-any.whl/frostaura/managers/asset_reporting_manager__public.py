'''This module defines public manager components.'''
import pandas as pd
from frostaura.data_access.notifications_data_access import INotificationsDataAccess
from frostaura.engines.visualization_engine import IVisualizationEngine
from frostaura.managers.asset_reporting_manager import IAssetReportingManager
from frostaura.data_access.personal_asset_data_access import IPersonalAssetDataAccess
from frostaura.engines.asset_valuation_engine import IAssetValuationEngine
from frostaura.data_access.public_asset_data_access import IPublicAssetDataAccess
from frostaura.models.visualization_types import VisualizationType
from frostaura.models.valuation_result import ValuationResult

class PublicAssetReportingManager(IAssetReportingManager):
    '''Component to perform functions related to public asset reporting.'''

    def __init__(self,
                 personal_asset_data_access: IPersonalAssetDataAccess,
                 asset_valuation_engine: IAssetValuationEngine,
                 visualization_engine: IVisualizationEngine,
                 public_notification_data_access: INotificationsDataAccess,
                 public_asset_data_access: IPublicAssetDataAccess,
                 config: dict = {}):
        self.personal_asset_data_access = personal_asset_data_access
        self.asset_valuation_engine = asset_valuation_engine
        self.visualization_engine = visualization_engine
        self.public_notification_data_access = public_notification_data_access
        self.public_asset_data_access = public_asset_data_access
        self.config = config

    def __send_individual_asset_performance_reports__(self, symbol_data: list):
        currency_format: str = '${x:,.0f}'
        green: str = '#11E5AD'
        red: str = '#e55111'
        top: int = 15
        top_x_symbol_data = symbol_data.copy()
        top_x_symbol_data = [s for s in top_x_symbol_data if s['valuation'] is not None and not s['valuation'].is_overvalued]

        if len(top_x_symbol_data) <= 0:
            self.public_notification_data_access.send_text(text='No undervalued stocks to report currently.')
            return

        for data in top_x_symbol_data:
            valuation: ValuationResult = data['valuation']

            if valuation.is_overvalued:
                valuation.absolute_current_v_valuation_delta = -valuation.absolute_current_v_valuation_delta

        top_x_symbol_data = sorted(top_x_symbol_data,
                             key=lambda i: i['valuation'].absolute_current_v_valuation_delta,
                             reverse=True)[:top]

        text: str = f'Top <i>{top}</i> EasyEquities <strong>Value</strong> Assets <i>(better viewed horizontally)</i>'
        self.public_notification_data_access.send_text(text=text)
        assets_table: dict = {
            'Symbol': [],
            'Close': [],
            'Intrinsic': [],
            '%': [],
            'Dividend': []
        }

        for data in top_x_symbol_data:
            valuation: ValuationResult = data['valuation']
            symbol: str = valuation.symbol
            company: str = valuation.company_name

            assets_table['Symbol'].append(symbol)
            assets_table['Close'].append(currency_format.format(x=valuation.current_price))
            assets_table['Intrinsic'].append(currency_format.format(x=valuation.fair_price))
            assets_table['%'].append(f'{round(valuation.absolute_current_v_valuation_delta * 100, 2)}%')

            if valuation.divident_payout_frequency_in_months > 0:
                assets_table['Dividend'].append(f'{round(valuation.annual_dividend_percentage, 2)}%')
            else:
                assets_table['Dividend'].append(currency_format.format(x=0))

        self.public_notification_data_access.send_dataframe(pd.DataFrame(assets_table))

        for data in top_x_symbol_data:
            valuation: ValuationResult = data['valuation']
            symbol: str = valuation.symbol
            company: str = valuation.company_name
            history: pd.DataFrame = self.public_asset_data_access.get_symbol_history(symbol=symbol)

            fig, ax = self.visualization_engine.get_figure(x='Date',
                                                           y='Close',
                                                           data=history,
                                                           graph_type=VisualizationType.LINE,
                                                           title=f'{company} ({symbol})',
                                                           subtitle=None if (valuation.annual_dividend_percentage is None or valuation.divident_payout_frequency_in_months == 0) else f'Dividend: {round(valuation.annual_dividend_percentage, 2)}% Annually ({valuation.divident_payout_frequency_in_months} Month Frequency)',
                                                           legend=True,
                                                           line_label=f'Current Value: {currency_format.format(x=valuation.current_price)}',
                                                           y_tick_format_str=currency_format)

            # Draw valuation line
            ax.axhline(y=valuation.fair_price,
                       linestyle='-',
                       color=red if valuation.is_overvalued else green,
                       label=f'Intrinsic Value: {currency_format.format(x=valuation.fair_price)} (Δ{round(valuation.absolute_current_v_valuation_delta*100, 2)}%)')

            fig.legends = [fig.legend()]

            self.public_notification_data_access.send_figure(figure=fig)

    def send_reports(self):
        '''Generate and send asset reports.'''

        all_symbols: list = self.personal_asset_data_access.get_supported_assets()
        symbols_with_info: pd.DataFrame = self.public_asset_data_access.augment_symbols_info(symbols=all_symbols)
        symbol_data: list = [{ 'history': None, 'valuation': self.asset_valuation_engine.valuate(symbol_data=v) } for v in list(symbols_with_info.quote.values)]
        symbol_data = [sd for sd in symbol_data if sd['valuation'] is not None]

        self.__send_individual_asset_performance_reports__(symbol_data=symbol_data)
