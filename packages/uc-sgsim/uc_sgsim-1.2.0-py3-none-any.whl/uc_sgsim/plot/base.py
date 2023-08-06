import numpy as np

from uc_sgsim.cov_model.base import CovModel


class PlotBase:
    def __init__(self, model: CovModel, random_field: np.array, figsize=(10, 8)):
        self.__model = model
        self.__random_field = random_field
        self.__figsize = figsize
        self.__model_name = model.model_name
        self.__bandwidth_step = model.bandwidth_step
        self.__bandwidth = model.bandwidth
        self.__k_range = model.k_range
        self.__sill = model.sill
        self.__size = len(random_field)
        self.__realization_number = len(random_field[:, 0])

    @property
    def model(self) -> CovModel:
        return self.__model

    @property
    def random_field(self) -> np.array:
        return self.__random_field

    @property
    def figsize(self) -> tuple:
        return self.__figsize

    @property
    def model_name(self) -> str:
        return self.__model_name

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

    @property
    def size(self) -> int:
        return self.__size

    @property
    def realization_number(self) -> int:
        return self.__realization_number
