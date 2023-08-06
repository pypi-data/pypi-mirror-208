'''This module defines visualization engine components.'''
import pandas as pd
import matplotlib.pyplot as plt
from frostaura.models.visualization_types import VisualizationType

class IVisualizationEngine:
    '''Component to perform functions related to visualization.'''

    def get_figure(self,
                   data: pd.DataFrame,
                   x: str,
                   y: str,
                   graph_type: VisualizationType,
                   title: str,
                   subtitle: str,
                   legend: bool,
                   line_label: str,
                   x_tick_format_str: str,
                   y_tick_format_str: str) -> list:
        '''Generate a visualization for the given parameters and return a matplotlib figure.'''

        raise NotImplementedError()
