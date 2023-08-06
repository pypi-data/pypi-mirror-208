'''This module defines the interface for the notifications data access components.'''
import matplotlib.pyplot as plt
import pandas as pd

class INotificationsDataAccess:
    '''Component to perform resource related actions.'''

    def send_figure(self, figure: plt.Figure):
        '''Send a Matplotlib figure as an image.'''

        raise NotImplementedError()

    def send_text(self, text: str) -> object:
        '''Send a text notification.'''

        raise NotImplementedError()

    def send_dataframe(self, dataframe: pd.DataFrame):
        '''Send a Pndas dataframe table.'''

        raise NotImplementedError()
