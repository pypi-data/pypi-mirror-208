'''This module defines visualization engine components.'''
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from frostaura.engines.visualization_engine import IVisualizationEngine
from frostaura.models.visualization_types import VisualizationType

class FrostAuraVisualizationEngine(IVisualizationEngine):
    '''Component to perform functions related to visualization that is themed for FrostAura.'''

    def get_figure(self,
                   data: pd.DataFrame,
                   x: str,
                   y: str,
                   graph_type: VisualizationType,
                   title: str=None,
                   subtitle: str=None,
                   legend: bool=False,
                   line_label: str=None,
                   x_tick_format_str: str=None,
                   y_tick_format_str: str=None) -> list:
        '''Generate a visualization for the given parameters and return a matplotlib figure.'''

        fa_light: str = '#007bff'
        fa_dark: str = '#00379b'
        fa_gray: str = '#707070'
        fa_white: str = 'white'

        line_width: float = 1
        grid_line_width: float = 0.5
        outer_background_color: str = fa_white
        inner_background_color: str = fa_white
        labels_color: str = fa_gray
        grid_frame_color: str = fa_white
        should_show_grid: bool = True
        grid_color: str = fa_light
        title_legend_color: str = fa_dark
        x_y_colors: str = fa_light

        sns.set(font_scale=0.75, rc={
            'axes.facecolor': inner_background_color,
            'figure.facecolor': outer_background_color,
            'axes.labelcolor': labels_color,
            'axes.edgecolor': grid_frame_color,
            'axes.grid': should_show_grid,
            'grid.color': grid_color,
            'grid.linestyle': '--',
            'text.color': title_legend_color,
            'xtick.color': x_y_colors,
            'ytick.color': x_y_colors,
            'lines.linewidth': line_width,
            'grid.linewidth': grid_line_width
        })
        figsize = (4,4) if graph_type == VisualizationType.PIE else (8, 4)
        fig, axs = plt.subplots(1, dpi=600, figsize=figsize)

        if line_label is not None and y_tick_format_str is not None:
            if not type(line_label) == str:
                line_label = y_tick_format_str.format(x=line_label)

        if graph_type == VisualizationType.LINE:
            sns.lineplot(x=x, y=y, data=data, ci=False, color=fa_dark, ax=axs, label=line_label)
        elif graph_type == VisualizationType.BAR:
            raise NotImplementedError('Bar plots have outstanding styling issues and is not yet supported.')
            #sns.barplot(x=x, y=y, data=data, ci=False, color=fa_dark, ax=axs, label=line_label)
        elif graph_type == VisualizationType.PIE:
            labels: list = data[x].values
            values: list = data[y].values

            plt.pie(x=values, labels=labels)
        else:
            raise NotImplementedError(f'The figure type "{graph_type}" is not supported.')

        if title is not None:
            mid = (fig.subplotpars.right + fig.subplotpars.left)/2
            fig.suptitle(title, x=mid)

        if subtitle is not None:
            axs.set_title(subtitle)

        if y_tick_format_str is not None:
            tick = mtick.StrMethodFormatter(y_tick_format_str)
            axs.yaxis.set_major_formatter(tick)

        if x_tick_format_str is not None:
            tick = mtick.StrMethodFormatter(x_tick_format_str)
            axs.xaxis.set_major_formatter(tick)

        current_legend = axs.get_legend()

        if current_legend is not None:
            current_legend.remove()

        if legend:
            fig.legend(numpoints=1)

        return fig, axs
