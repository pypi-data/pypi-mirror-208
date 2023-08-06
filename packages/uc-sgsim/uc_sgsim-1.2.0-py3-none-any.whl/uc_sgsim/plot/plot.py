import time

import matplotlib.pyplot as plt
import numpy as np
from uc_sgsim.plot.base import PlotBase
from uc_sgsim.cov_model.base import CovModel


class Visualize(PlotBase):
    xlabel = 'Distance(-)'

    def __init__(self, model: CovModel, random_field: np.array):
        super().__init__(model, random_field)

    def mean_plot(self, n, mean=0, std=1) -> None:
        realization_number = len(self.random_field[:, 0])

        if n == 'ALL':
            for i in range(realization_number):
                plt.figure(77879, figsize=self.figsize)
                plt.plot(self.random_field[i, :] * std + mean)
                plt.title('Realizations: ' + self.model_name, fontsize=20)
                plt.xlabel(self.xlabel, fontsize=20)
                plt.axhline(y=mean, color='r', linestyle='--', zorder=1)
                plt.ylabel('S', fontsize=20)

        else:
            for item in n:
                plt.figure(77879, figsize=self.figsize)
                plt.plot(self.random_field[:, item] * std + mean)
                plt.title('Realizations: ' + self.model_name, fontsize=20)
                plt.xlabel(self.xlabel, fontsize=20)
                plt.axhline(y=mean, color='r', linestyle='--', zorder=1)
                plt.ylabel('Y', fontsize=20)

    def variance_plot(self, mean=0, std=1) -> None:
        zmean = np.zeros(len(self.random_field[0, :]))

        for i in range(len(self.random_field[0, :])):
            zmean[i] = np.mean(self.random_field[:, i] * std + mean)

        plt.figure(5212, figsize=self.figsize)
        plt.plot(
            zmean,
            '-s',
            color='k',
            markeredgecolor='k',
            markerfacecolor='y',
        )
        plt.xlabel(self.xlabel, fontsize=20)
        plt.ylabel('Mean', fontsize=20)
        plt.axhline(y=mean, color='r', linestyle='--', zorder=1)
        plt.xticks(fontsize=17), plt.yticks(fontsize=17)

        zvar = np.zeros(len(self.random_field[0, :]))

        for i in range(len(self.random_field[0, :])):
            zvar[i] = np.var(self.random_field[:, i] * std)

        plt.figure(52712, figsize=self.figsize)
        plt.plot(
            zvar,
            '-o',
            color='k',
            markeredgecolor='k',
            markerfacecolor='r',
        )
        plt.xlabel(self.xlabel, fontsize=20)
        plt.ylabel('Variance', fontsize=20)
        plt.axhline(y=std**2, color='b', linestyle='--', zorder=1)
        plt.xticks(fontsize=17), plt.yticks(fontsize=17)

    def cdf_plot(self, x_location: int) -> None:

        X = self.random_field[:, x_location]

        mu = np.mean(X)
        sigma = np.std(X)
        n_bins = 50

        _, ax = plt.subplots(figsize=(8, 4))

        _, bins, _ = ax.hist(
            X,
            n_bins,
            density=True,
            histtype='step',
            cumulative=True,
            label='Empirical',
        )

        y = (1 / (np.sqrt(2 * np.pi) * sigma)) * np.exp(
            -0.5 * (1 / sigma * (bins - mu)) ** 2,
        )
        y = y.cumsum()
        y /= y[-1]

        ax.plot(bins, y, 'k--', linewidth=1.5, label='Theoretical')

        ax.grid(True)
        ax.legend(loc='right')
        ax.set_title('Cumulative step histograms, x = ' + str(x_location))
        ax.set_xlabel('Random Variable (mm)')
        ax.set_ylabel('Occurrence')

    def hist_plot(self, x_location: int) -> None:

        X = self.random_field[:, x_location]

        mu = np.mean(X)
        sigma = np.std(X)

        num_bins = 50
        plt.figure(num=1151)
        _, bins, _ = plt.hist(
            X,
            num_bins,
            density=1,
            color='blue',
            alpha=0.5,
            edgecolor='k',
        )

        y = (1 / (np.sqrt(2 * np.pi) * sigma)) * np.exp(
            -0.5 * (1 / sigma * (bins - mu)) ** 2,
        )

        plt.plot(bins, y, '--', color='black')

        plt.xlabel('X-Axis')
        plt.ylabel('Y-Axis')

        plt.title('Histogram, x = ' + str(x_location))

    def variogram_plot(self, variogram: np.array) -> None:
        start_time = time.time()
        for i in range(self.realization_number):
            plt.figure(123456, figsize=(10, 6))
            plt.plot(variogram[i, :], alpha=0.1)
            plt.title('Model: ' + self.model_name, fontsize=20)
            plt.xlabel('Lag(m)', fontsize=20)
            plt.ylabel('Variogram', fontsize=20)
            plt.xticks(fontsize=17), plt.yticks(fontsize=17)
            print('Progress = %.2f' % (i / self.realization_number * 100) + '%', end='\r')

        plt.plot(
            self.model.var_compute(self.bandwidth),
            'o',
            markeredgecolor='k',
            markerfacecolor='w',
        )

        Vario_mean = np.zeros(len(self.bandwidth))
        for i in range(len(self.bandwidth)):
            Vario_mean[i] = np.mean(variogram[:, i])

        plt.plot(Vario_mean, '--', color='blue')

        print('Progress = %.2f' % 100 + '%\n', end='\r')

        end_time = time.time()

        print('Time = ', end_time - start_time, 's')
