import numpy as np
from uc_sgsim.cov_model.base import CovModel


class Gaussian(CovModel):
    model_name = 'Gaussian'

    def model(self, h: float) -> float:
        return self.sill * (1 - np.exp(-3 * h**2 / self.k_range**2))


class Spherical(CovModel):
    model_name = 'Spherical'

    def model(self, h: float) -> float:
        if h <= self.k_range:
            return self.sill * (1.5 * h / self.k_range - 0.5 * (h / self.k_range) ** 3.0)
        else:
            return self.sill
