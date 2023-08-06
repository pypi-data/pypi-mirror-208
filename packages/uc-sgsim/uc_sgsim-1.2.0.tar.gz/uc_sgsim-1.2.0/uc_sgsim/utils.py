import os
from ctypes import Structure, POINTER, c_double, c_int


def save_as_multiple_file(
    number: str,
    size: int,
    field: list,
    file_type: str,
    fieldtype: str,
) -> None:
    idx = number.strip('0')
    os.makedirs(f'./{fieldtype}', exist_ok=True)
    idx = 0 if not idx else int(idx)
    with open(f'./{fieldtype}/{fieldtype}{number}.{file_type}', 'w') as f:
        for j in range(0, size):
            print(
                '%.2d' % (j),
                '%10.6f' % (field[idx, j]),
                file=f,
            )


def save_as_one_file(path: str, field: list) -> None:
    with open(f'{path}', 'w') as f:
        for i in range(len(field[:, 0])):
            for j in range(len(field[0, :])):
                end = '\n' if j == len(field[0, :]) - 1 else ', '
                print(
                    '%10.6f' % (field[i, j]),
                    file=f,
                    end=end,
                )


class SgsimStructure(Structure):
    _fields_ = [
        ('x_grid', c_int),
        ('realization_numbers', c_int),
        ('randomseed', c_int),
        ('vario_flag', c_int),
        ('array', POINTER(c_double)),
    ]


class CovModelStructure(Structure):
    _fields_ = [
        ('bw', c_int),
        ('hs', c_int),
        ('range', c_double),
        ('sill', c_double),
    ]
