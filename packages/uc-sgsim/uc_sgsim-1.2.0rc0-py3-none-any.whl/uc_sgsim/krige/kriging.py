import numpy as np
from scipy.spatial.distance import pdist, squareform
from uc_sgsim.cov_model.base import CovModel
from uc_sgsim.krige.base import Kriging


class SimpleKrige(Kriging):
    def __init__(self, model: CovModel):
        super().__init__(model)

    def prediction(self, sample: np.array, unsampled: np.array) -> tuple[float, float]:
        n_sampled = len(sample)
        dist_diff = abs(sample[:, 0] - unsampled)
        dist_diff = dist_diff.reshape(len(dist_diff), 1)

        L = np.hstack([sample, dist_diff])
        meanvalue = 0

        cov_dist = np.matrix(self.model.cov_compute(L[:, 2])).T
        cov_data = squareform(pdist(L[:, :1])).flatten()
        cov_data = np.array(self.model.cov_compute(cov_data))
        cov_data = cov_data.reshape(n_sampled, n_sampled)

        weights = np.linalg.inv(cov_data) * cov_dist
        residuals = L[:, 1] - meanvalue
        estimation = np.dot(weights.T, residuals) + meanvalue
        krige_var = float(1 - np.dot(weights.T, cov_dist))

        if krige_var < 0:
            krige_var = 0

        krige_std = np.sqrt(krige_var)

        return estimation, krige_std

    def simulation(self, x: int, unsampled: int, **kwargs) -> float:
        neighbor = kwargs.get('neighbor')
        if neighbor:
            dist = abs(x[:, 0] - unsampled)
            dist = dist.reshape(len(dist), 1)
            has_neighbor = self.find_neighbor(dist, neighbor)
            if has_neighbor:
                return has_neighbor
            x = np.hstack([x, dist])
            x = np.array(sorted(x, key=lambda itr: itr[2])[:neighbor])

        estimation, krige_std = self.prediction(x, unsampled)

        random_fix = np.random.normal(0, krige_std, 1)
        return estimation + random_fix

    def find_neighbor(self, dist: list, neighbor: int) -> float:
        if neighbor == 0:
            return np.random.normal(0, 1, 1)
        close_point = 0

        criteria = self.k_range * 1.732 if self.model.model_name == 'Gaussian' else self.k_range

        for item in dist:
            if item <= criteria:
                close_point += 1

        if close_point == 0:
            return np.random.normal(0, 1, 1)
