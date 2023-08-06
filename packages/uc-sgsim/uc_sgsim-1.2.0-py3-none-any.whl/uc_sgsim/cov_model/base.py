import numpy as np
from scipy.spatial.distance import pdist, squareform


class CovModel:
    def __init__(
        self,
        bandwidth_len: float,
        bandwidth_step: float,
        k_range: float,
        sill=1,
    ):
        self.__bandwidth_len = bandwidth_len
        self.__bandwidth_step = bandwidth_step
        self.__bandwidth = np.arange(0, bandwidth_len, bandwidth_step)
        self.__k_range = k_range
        self.__sill = sill

    @property
    def bandwidth_len(self) -> float:
        return self.__bandwidth_len

    @property
    def bandwidth_step(self) -> float:
        return self.__bandwidth_step

    @property
    def bandwidth(self) -> np.array:
        return self.__bandwidth

    @property
    def k_range(self) -> float:
        return self.__k_range

    @property
    def sill(self) -> float:
        return self.__sill

    def cov_compute(self, x: np.array) -> np.array:
        cov = np.empty(len(x))
        for i in range(len(x)):
            cov[i] = self.__sill - self.model(x[i])

        return cov

    def var_compute(self, x: np.array) -> np.array:
        var = np.empty(len(x))
        for i in range(len(x)):
            var[i] = self.model(x[i])

        return var

    def variogram(self, x: np.array) -> np.array:
        dist = squareform(pdist(x[:, :1]))
        variogram = []

        for h in self.__bandwidth:
            z = []
            for i in range(len(dist[:, 0])):
                for j in range(i + 1, len(dist[:, 0])):
                    if (dist[i, j] >= h - self.__bandwidth_step) and (
                        dist[i, j] <= h + self.__bandwidth_step
                    ):
                        z.append(np.power(x[i, 1] - x[j, 1], 2))
            if np.sum(z) >= 1e-7:
                variogram.append(np.sum(z) / (2 * len(z)))

        return np.array(variogram)
