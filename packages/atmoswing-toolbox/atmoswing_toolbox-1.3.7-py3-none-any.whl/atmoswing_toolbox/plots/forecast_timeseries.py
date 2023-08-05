import math
import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


class ForecastTimeSeriesPlot:
    """Base class to create a time serie of forecast"""

    def __init__(self, output_path=''):
        self.fig = None
        self.ax = None
        self.output_path = output_path
        self.output_name = 'plot'
        self.dates = None
        self.obs_values = None
        self.analogs_values = None
        self.start = 0
        self.end = 0
        self.ref_periods = np.array([])
        self.ref_precip = np.array([])
        self.max_val = 0
        self._show_legend = True
        self._show_dots = False

    def show(self):
        plt.ion()
        self._make_figure()
        plt.show()

    def print(self):
        if not self.output_path:
            raise Exception('Output path not provided')
        plt.ioff()
        self._make_figure()
        self._print()

    def _make_figure(self):
        plt.rcParams.update({'font.size': 15})
        self.fig = plt.figure(figsize=(18, 4.5))
        self.ax = self.fig.add_subplot(111)
        self.build()

    def _print(self):
        self.fig.savefig(os.path.join(self.output_path, self.output_name + '.pdf'))
        self.fig.savefig(os.path.join(self.output_path, self.output_name + '.png'),
                         dpi=300)
        plt.close(self.fig)

    def set_output_name(self, name):
        self.output_name = name

    def limit_period(self, start, end):
        # Using datetime: ex: datetime.date(1987, 7, 4)
        self.start = start
        self.end = end

    def set_reference_levels(self, ref_periods, ref_precip):
        self.ref_periods = ref_periods
        self.ref_precip = ref_precip

    def hide_legend(self):
        self._show_legend = False

    def show_all_dots(self):
        self._show_dots = True

    def set_data(self, dates, obs_values, analogs_values):
        self.dates = dates
        self.obs_values = obs_values
        self.analogs_values = analogs_values

    def set_max_val(self, value):
        self.max_val = value

    def build(self):
        # Split data if we focus on a period
        if self.start and self.end:
            start_array = np.searchsorted(self.dates, self.start.toordinal() - 678576)
            end_array = np.searchsorted(self.dates, self.end.toordinal() - 678575)
            self.analogs_values = self.analogs_values[start_array:end_array, :]
            self.dates = self.dates[start_array:end_array]
            self.obs_values = self.obs_values[start_array:end_array]

        # Convert time for plotting
        plot_dates = self.dates + 678575 + 1

        # Extract quantiles
        q030 = np.nanmean(np.percentile(self.analogs_values, 30, axis=2), axis=0)
        q060 = np.nanmean(np.percentile(self.analogs_values, 60, axis=2), axis=0)
        q090_all = np.percentile(self.analogs_values, 90, axis=2)
        q090 = np.nanmean(q090_all, axis=0)
        q100 = np.nanmean(np.percentile(self.analogs_values, 100, axis=2), axis=0)

        # Plot the reference values
        plot_obs = self.obs_values
        plot_obs[np.isnan(q100)] = np.nan
        self.ax.plot(plot_dates, plot_obs, '-', linewidth=2, color='r',
                     label="observations")

        # Plot areas and lines
        self.ax.fill_between(plot_dates, q030, q060, facecolor=[0.6, 0.6, 0.6],
                             edgecolor='None')
        self.ax.fill_between(plot_dates, q060, q090, facecolor=[0.6, 0.6, 0.6],
                             edgecolor='None')
        self.ax.plot(plot_dates, q030, '--', linewidth=1, color='k',
                     label=r"mean quantile 30\%")
        self.ax.plot(plot_dates, q060, '-', linewidth=1, color='k',
                     label=r"mean quantile 60\%")
        self.ax.plot(plot_dates, q090_all[0], ':', linewidth=1, color='k',
                     label=r"single quantile 90\%")
        self.ax.plot(plot_dates, q090_all[1], ':', linewidth=1, color='k')
        self.ax.plot(plot_dates, q090_all[2], ':', linewidth=1, color='k')
        self.ax.plot(plot_dates, q090_all[3], ':', linewidth=1, color='k')
        self.ax.plot(plot_dates, q090, '--', linewidth=1, color='k',
                     label=r"mean quantile 90\%")
        self.ax.plot(plot_dates, q100, 'x', markersize=3, color='0.5',
                     label="mean maximum")

        # Gray nan areas
        for idx, val in enumerate(q100):
            if math.isnan(val):
                self.ax.axvspan(plot_dates[max(idx - 1, 0)],
                                plot_dates[min(idx + 1, plot_dates.size - 1)],
                                facecolor=[0.9, 0.9, 0.9], edgecolor='None')

        # Plot the dots
        if self._show_dots:
            for i in range(self.analogs_values.shape[0]):
                self.ax.plot(plot_dates, self.analogs_values[:, i], 'ko')

        # Format the ticks
        if self.start and self.end:
            days = mdates.DayLocator()
            some_days = mdates.DayLocator(interval=5)
            days_fmt = mdates.DateFormatter('%d.%m.%Y')
            self.ax.xaxis.set_major_locator(some_days)
            self.ax.xaxis.set_minor_locator(days)
            self.ax.xaxis.set_major_formatter(days_fmt)
        else:
            self.ax.xaxis.set_major_locator(mdates.MonthLocator())
            self.ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=15))
            self.ax.xaxis.set_major_formatter(ticker.NullFormatter())
            self.ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))

            for tick in self.ax.xaxis.get_minor_ticks():
                tick.tick1line.set_markersize(0)
                tick.tick2line.set_markersize(0)
                tick.label1.set_horizontalalignment('center')

            i_mid = len(plot_dates) // 2
            date = plot_dates[i_mid]
            if np.isnan(date):
                date = plot_dates[0]
            if np.isnan(date):
                date = plot_dates[-1]
            y = mdates.num2date(date).year
            self.ax.set_xlabel(str(y))

        # Draw grid and set axis label
        self.ax.grid(True)
        plt.ylabel('Precipitation (mm/d)')

        # Draw line return periods P10
        if self.ref_periods.size == 0 and self.ref_precip.size == 0:
            p10_index = np.searchsorted(self.ref_periods, 10)
            plt.axhline(y=self.ref_precip[p10_index], linewidth=2, color='r',
                        label="return period of 10 years")

        # Set correct limits
        plt.ylim(bottom=0)
        if self.max_val > 0:
            plt.ylim(top=self.max_val)

        if self.start and self.end:
            self.ax.set_xlim(self.start, self.end)
        else:
            plt.xlim(plot_dates[0], plot_dates[-1])

        # Legends
        if self._show_legend:
            handles, labels = self.ax.get_legend_handles_labels()
            self.ax.legend(handles, labels, loc='upper left')

        self.fig.tight_layout()
