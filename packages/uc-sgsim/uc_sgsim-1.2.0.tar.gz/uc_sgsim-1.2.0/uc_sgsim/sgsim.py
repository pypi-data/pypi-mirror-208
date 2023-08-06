import time
import sys
from pathlib import Path
from ctypes import CDLL, POINTER, c_double, c_int
from multiprocessing import Pool

import numpy as np
from uc_sgsim.exception import VariogramDoesNotCompute
from uc_sgsim.krige import SimpleKrige
from uc_sgsim.random_field import RandomField
from uc_sgsim.plot.plot import Visualize
from uc_sgsim.cov_model.base import CovModel
from uc_sgsim.utils import CovModelStructure, SgsimStructure

BASE_DIR = Path(__file__).resolve().parent


class UCSgsim(RandomField):
    def __init__(
        self,
        x: int,
        model: CovModel,
        realization_number: int,
        krige_method='SimpleKrige',
    ):
        super().__init__(x, model, realization_number)
        self.krige_method = krige_method

    def compute(self, randomseed=0, parallel=False) -> np.array:
        self.randomseed = randomseed
        if parallel is False:
            self.n_process = 1

        if self.krige_method == 'SimpleKrige':
            self.krige = SimpleKrige(self.model)

        counts = 0

        start_time = time.time()
        np.random.seed(self.randomseed)
        while counts < self.realization_number // self.n_process:
            unsampled = np.linspace(0, self.x_size - 1, self.x_size)

            y_value = np.random.normal(0, 1, 2).reshape(2, 1)
            x_grid = np.array([0, self.x_size - 1]).reshape(2, 1)
            z = np.zeros(self.x_size)
            z[0], z[-1] = y_value[0], y_value[1]
            unsampled = np.delete(unsampled, [0, -1])
            neigh = 0

            L = np.hstack([x_grid, y_value])

            randompath = np.random.choice(
                unsampled,
                len(unsampled),
                replace=False,
            )

            for i in range(len(unsampled)):
                z[int(randompath[i])] = self.krige.simulation(
                    L,
                    randompath[i],
                    neighbor=neigh,
                )
                temp = np.hstack([randompath[i], z[int(randompath[i])]])
                L = np.vstack([L, temp])

                if neigh < 8:
                    neigh += 1

            self.randomseed += 1

            z_gap = abs(z.max() - z.min())

            if 2 < z_gap <= 6.5:
                self.random_field[counts, :] = z
                counts = counts + 1
                print('Progress = %.2f' % (counts / self.realization_number * 100) + '%', end='\r')

        print('Progress = %.2f' % 100 + '%\n', end='\r')
        end_time = time.time()
        print('Time = %f' % (end_time - start_time), 's\n')

        return self.random_field

    def compute_async(self, n_process: int, randomseed: int) -> np.array:
        pool = Pool(processes=n_process)
        self.n_process = n_process
        self.realization_number = self.realization_number * n_process
        self.random_field = np.empty([self.realization_number, self.x_size])

        rand_list = []
        parallel = []
        for i in range(n_process):
            s = randomseed + int(i)
            rand_list.append(int(s))
            parallel.append(True)

        z = pool.starmap(self.compute, zip(rand_list, parallel))
        pool.close()
        # use pool.join() to measure the coverage of sub process
        pool.join()

        for i in range(n_process):
            for j in range(int(self.realization_number / n_process)):
                start = int(i * self.realization_number / n_process)
                self.random_field[j + start, :] = z[i][j, :]

        return self.random_field

    def variogram_compute(self, n_process=1) -> None:
        pool = Pool(processes=n_process)
        model_len = self.x_size
        x = np.linspace(0, self.x_size - 1, model_len).reshape(model_len, 1)

        L = []
        for i in range(self.realization_number):
            L.append(
                np.hstack([x, self.random_field[i, :].reshape(model_len, 1)]),
            )

        self.variogram = pool.starmap(self.model.variogram, zip(L))
        pool.close()
        # use pool.join() to measure the coverage of sub process
        pool.join()
        self.variogram = np.array(self.variogram)

    def mean_plot(self, n, mean=0, std=1) -> None:
        m_plot = Visualize(self.model, self.random_field)
        m_plot.mean_plot(n, mean, std)

    def variance_plot(self, mean=0, std=1) -> None:
        s_plot = Visualize(self.model, self.random_field)
        s_plot.variance_plot(mean, std)

    def cdf_plot(self, x_location: int) -> None:
        c_plot = Visualize(self.model, self.random_field)
        c_plot.cdf_plot(x_location)

    def hist_plot(self, x_location: int) -> None:
        h_plot = Visualize(self.model, self.random_field)
        h_plot.hist_plot(x_location)

    def vario_plot(self) -> None:
        if type(self.variogram) == int:
            raise VariogramDoesNotCompute()
        v_plot = Visualize(self.model, self.random_field)
        v_plot.variogram_plot(self.variogram)


class UCSgsimDLL(UCSgsim):
    def __init__(
        self,
        x: int,
        model: CovModel,
        realization_number: int,
        krige_method='SimpleKrige',
    ):
        super().__init__(x, model, realization_number)
        self.krige_method = krige_method

    def lib_read(self) -> CDLL:
        if sys.platform.startswith('linux'):
            lib = CDLL(str(BASE_DIR) + r'/c_core/uc_sgsim.so')
        elif sys.platform.startswith('win32'):
            lib = CDLL(str(BASE_DIR) + r'/c_core/uc_sgsim.dll', winmode=0)
        return lib

    def cpdll(self, randomseed: int) -> np.array:
        lib = self.lib_read()
        mlen = int(self.x_size)
        realization_number = int(self.realization_number // self.n_process)
        random_field = np.empty([realization_number, self.x_size])

        sgsim_init = lib.sgsim_init
        sgsim_init.argtypes = (
            POINTER(SgsimStructure),
            c_int,
            c_int,
            c_int,
            c_int,
        )
        sgsim_s = SgsimStructure()
        sgsim_init(sgsim_s, mlen, realization_number, randomseed, 0)
        sgsim_s.array = (c_double * (mlen * realization_number))()

        cov_init = lib.cov_model_init
        cov_s = CovModelStructure()
        cov_init.argtypes = (
            POINTER(CovModelStructure),
            c_int,
            c_int,
            c_double,
            c_double,
        )
        cov_init(cov_s, 1, 35, 17.32, 1)

        sgsim = lib.sgsim_run
        sgsim.argtypes = (POINTER(SgsimStructure), POINTER(CovModelStructure), c_int)
        sgsim(sgsim_s, cov_s, 0)

        # array = as_array(sgsim_s.array, shape=(realization_number * mlen, 1))
        for i in range(realization_number):
            random_field[i, :] = sgsim_s.array[i * mlen : (i + 1) * mlen]
        return random_field

    def compute(self, n_process: int, randomseed: int) -> np.array:
        pool = Pool(processes=n_process)
        self.n_process = n_process

        if n_process > 1:
            self.realization_number = self.realization_number * n_process

        self.random_field = np.empty([self.realization_number, self.x_size])

        rand_list = []
        for i in range(n_process):
            s = randomseed + int(i)
            rand_list.append(int(s))

        z = pool.starmap(self.cpdll, zip(rand_list))
        print(len(z))
        pool.close()
        # use pool.join() to measure the coverage of sub process
        pool.join()

        for i in range(n_process):
            for j in range(int(self.realization_number / n_process)):
                start = int(i * self.realization_number / n_process)
                self.random_field[j + start, :] = z[i][j, :]

        return self.random_field

    def variogram_cpdll(self, cpu_number: int) -> np.array:
        lib = self.lib_read()
        vario = lib.variogram
        vario.argtypes = (
            POINTER(c_double),
            POINTER(c_double),
            c_int,
            c_int,
            c_int,
        )
        vario.restype = None

        mlen = int(self.x_size)
        realization_number = int(self.realization_number // self.n_process)

        vario_size = len(self.bandwidth)

        vario_array = (c_double * (vario_size))()
        random_field_array = (c_double * (mlen))()

        variogram = np.empty([realization_number, vario_size])

        for i in range(realization_number):
            random_field_array[:] = self.random_field[i + cpu_number * realization_number, :]
            vario(random_field_array, vario_array, mlen, vario_size, 1)
            variogram[i, :] = list(vario_array)

        return variogram

    def variogram_compute(self, n_process=1) -> np.array:
        pool = Pool(processes=n_process)
        self.n_process = n_process

        if n_process < 1:
            self.realization_number = self.realization_number * n_process

        self.variogram = np.empty([self.realization_number, len(self.bandwidth)])
        cpu_number = []
        for i in range(self.n_process):
            cpu_number.append(i)

        z = pool.starmap(self.variogram_cpdll, zip(cpu_number))
        pool.close()
        # use pool.join() to measure the coverage of sub process
        pool.join()

        for i in range(n_process):
            for j in range(int(self.realization_number / n_process)):
                self.variogram[(j + int(i * self.realization_number / n_process)), :] = z[i][j, :]
        return self.variogram
