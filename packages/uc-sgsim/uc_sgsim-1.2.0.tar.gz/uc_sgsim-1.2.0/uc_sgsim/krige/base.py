import numpy as np
from uc_sgsim.cov_model.base import CovModel


class Kriging:
    def __init__(self, model: CovModel):
        self.__model = model
        self.__bandwidth_step = model.bandwidth_step
        self.__bandwidth = model.bandwidth
        self.__k_range = model.k_range
        self.__sill = model.sill

    @property
    def model(self) -> CovModel:
        return self.__model

    @property
    def bandwidth_step(self) -> int:
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
