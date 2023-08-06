import numpy as np
from uc_sgsim.exception import VariogramDoesNotCompute
from uc_sgsim.utils import save_as_multiple_file, save_as_one_file
from uc_sgsim.cov_model.base import CovModel


class RandomField:
    def __init__(self, x: int, model: CovModel, realization_number: int):
        self.__model = model
        self.__realization_number = realization_number
        self.__bandwidth_step = model.bandwidth_step
        self.__bandwidth = model.bandwidth
        self.__create_grid(x)

    def __create_grid(self, x: int, y: int = 0) -> None:
        self.__x = range(x)
        self.__y = range(y)
        self.__x_size = len(self.__x)
        self.__y_size = len(self.__y)
        self.random_field = np.empty([self.__realization_number, self.__x_size])
        self.variogram = 0

    @property
    def x(self) -> int:
        return self.__x

    @property
    def x_size(self) -> int:
        return self.__x_size

    @property
    def y(self) -> int:
        return self.__y

    @property
    def y_size(self) -> int:
        return self.__y_size

    @property
    def model(self) -> CovModel:
        return self.__model

    @property
    def realization_number(self) -> int:
        return self.__realization_number

    @realization_number.setter
    def realization_number(self, val: int):
        self.__realization_number = val

    @property
    def bandwidth(self) -> np.array:
        return self.__bandwidth

    @property
    def bandwidth_step(self) -> int:
        return self.__bandwidth_step

    def save_random_field(self, path: str, file_type='csv', save_single=False) -> None:
        digit = int(np.log10(self.realization_number))
        number_head = ''
        for i in range(digit):
            number_head += '0'
        num_val = 1
        if save_single is False:
            for i in range(self.realization_number):
                if i // num_val == 10:
                    num_val *= 10
                    number_head = number_head[:-1]
                number = number_head + str(i)
                save_as_multiple_file(
                    number,
                    self.x_size,
                    self.random_field,
                    file_type,
                    'Realizations',
                )
        else:
            save_as_one_file(path, self.random_field)

    def save_variogram(self, path: str, file_type='csv', save_single=False) -> None:
        if type(self.variogram) == int:
            raise VariogramDoesNotCompute()
        digit = int(np.log10(self.realization_number))
        number_head = ''
        for i in range(digit):
            number_head += '0'
        num_val = 1
        if save_single is False:
            for i in range(self.realization_number):
                if i // num_val == 10:
                    num_val *= 10
                    number_head = number_head[:-1]
                number = number_head + str(i)
                save_as_multiple_file(
                    number,
                    len(self.bandwidth),
                    self.variogram,
                    file_type,
                    'Variogram',
                )
        else:
            save_as_one_file(path, self.variogram)
