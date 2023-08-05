import os

import matplotlib.pyplot as plt
import pandas as pd

from atmoswing_toolbox.parsers.optimized_parameters import ParametersArray


class MonteCarloPlot:
    """Plotting the results of the Monte Carlo analysis"""

    def __init__(self, file, output_path=''):
        self.fig = None
        self.results = ParametersArray(file)
        self.results.load()
        self.other_results = []
        self.other_results_score = []
        self.other_results_markers = []
        self.other_results_colors = []
        self.output_path = output_path
        self._do_print = False
        self._step = 0
        self._ptor = 0

    def show(self):
        plt.ion()
        self._loop_structure()

    def print(self):
        if not self.output_path:
            raise Exception('Output path not provided')
        self._do_print = True
        plt.ioff()
        self._loop_structure()

    def add_param(self, file, marker='+', period='valid', color=''):
        other_result = ParametersArray(file)
        other_result.load()

        # Make some checks
        if len(other_result.get_anbs(0)) != 1:
            raise Exception(f'The parameters file should contain exactly 1 set '
                            f'(the file has {other_result.get_anbs(0)}).')
        if len(self.results.struct) != len(other_result.struct):
            raise Exception(f'The number of steps is different between files '
                            f'({len(self.results.struct)} vs '
                            f'{len(other_result.struct)}).')
        for i_step, step in enumerate(self.results.struct):
            if step != other_result.struct[i_step]:
                raise Exception(f'The number of predictors is different between files '
                                f'({step} vs {other_result.struct[i_step]}).')
        # Store data
        if (period == 'valid') or (period == 'validation'):
            self.other_results_score.append(other_result.get_valid_score())
            if color == '':
                color = 'blue'
        elif (period == 'calib') or (period == 'calibration'):
            self.other_results_score.append(other_result.get_calib_score())
            if color == '':
                color = 'red'
        else:
            raise Exception(f'The provided period {period} is not recognized.')

        self.other_results.append(other_result)
        self.other_results_markers.append(marker)
        self.other_results_colors.append(color)

    def _loop_structure(self):
        for i_step, step in enumerate(self.results.struct):
            title = f'Level {i_step + 1}'
            self.make_plot('anb', xlabel='Number of analogues', title=title)
            self._print_or_show(title, 'Number of analogues')
            for self._ptor in range(0, step):
                title = f'Level {i_step + 1} - ' \
                        f'{self.results.get_variable(i_step, self._ptor)}' \
                        f'{self.results.get_level(i_step, self._ptor)} ' \
                        f'{self.results.get_time(i_step, self._ptor)}h'
                self.make_plot('xmin', xlabel='Minimum longitude [°]', title=title)
                self._print_or_show(title, 'Minimum longitude [°]')
                self.make_plot('xmax', xlabel='Maximum longitude [°]', title=title)
                self._print_or_show(title, 'Maximum longitude [°]')
                self.make_plot('ymin', xlabel='Minimum latitude [°]', title=title)
                self._print_or_show(title, 'Minimum latitude [°]')
                self.make_plot('ymax', xlabel='Maximum latitude [°]', title=title)
                self._print_or_show(title, 'Maximum latitude [°]')

    def make_plot(self, var, xlabel, title):
        self.fig = plt.figure(figsize=(5, 4))
        score = self.results.get_calib_scores()

        # Get MC values and plot
        values = None
        if var == 'anb':
            values = self.results.get_anbs(self._step)
        elif var == 'xmin':
            values = self.results.get_xmins(self._step, self._ptor)
        elif var == 'xmax':
            values = self.results.get_xmaxs(self._step, self._ptor)
        elif var == 'ymin':
            values = self.results.get_ymins(self._step, self._ptor)
        elif var == 'ymax':
            values = self.results.get_ymaxs(self._step, self._ptor)
        plt.scatter(values, score, c='', edgecolors=(0.2, 0.2, 0.2, 0.7),
                    linewidths=0.5, s=30)

        # Other values (ex. from calibration or GAs)
        for idx, res in enumerate(self.other_results):
            other_value = None
            if var == 'anb':
                other_value = res.get_anbs(self._step)
            elif var == 'xmin':
                other_value = res.get_xmins(self._step, self._ptor)
            elif var == 'xmax':
                other_value = res.get_xmaxs(self._step, self._ptor)
            elif var == 'ymin':
                other_value = res.get_ymins(self._step, self._ptor)
            elif var == 'ymax':
                other_value = res.get_ymaxs(self._step, self._ptor)
            other_score = self.other_results_score[idx]
            score = score.append(pd.Series(other_score))
            marker = self.other_results_markers[idx]
            color = self.other_results_colors[idx]
            plt.plot(other_value, other_score, marker=marker, color=color)

        # Formatting
        xmargin = 0.02 * (values.max() - values.min())
        if xmargin == 0:
            xmargin = 0.1
        plt.xlim(values.min() - xmargin, values.max() + xmargin)
        if self.results.score == 'CRPSS':
            plt.ylim(score.quantile(.75), 1.03 * score.max())
        elif self.results.score == 'CRPS':
            plt.ylim(0.97 * score.min(), score.quantile(.25))
        else:
            plt.ylim(0.97 * score.min(), score.quantile(.25))
        plt.xlabel(xlabel)
        plt.ylabel(self.results.score)
        plt.title(title)
        self.fig.tight_layout()

    def _print_or_show(self, title, xlabel):
        if self._do_print:
            filename = title + '_' + xlabel
            filename = filename.lower()
            filename = filename.replace('-', '')
            filename = filename.replace(' [°]', '')
            filename = filename.replace('  ', ' ')
            filename = filename.replace(' ', '_')
            filename = filename.replace('/', '_')
            filename = filename.replace('minimum', 'min')
            filename = filename.replace('maximum', 'max')
            filename = filename.replace('longitude', 'lon')
            filename = filename.replace('latitude', 'lat')
            filename = filename.replace('number_of', 'nb')
            self.fig.savefig(os.path.join(self.output_path, filename + '.pdf'))
            self.fig.savefig(os.path.join(self.output_path, filename + '.png'), dpi=300)
            plt.close(self.fig)
        else:
            plt.show()
