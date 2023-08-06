![licence](https://img.shields.io/github/license/Zncl2222/Stochastic_UC_SGSIM)
![python](https://img.shields.io/pypi/pyversions/uc-sgsim)
![language](https://img.shields.io/badge/Solutions-black.svg?style=flat&logo=c%2B%2B)
![language](https://img.shields.io/badge/Solutions-black.svg?style=flat&logo=python)
[![ci](https://github.com/Zncl2222/Stochastic_UC_SGSIM/actions/workflows/github-pre-commit.yml/badge.svg)](https://github.com/Zncl2222/Stochastic_UC_SGSIM/actions/workflows/github-pre-commit.yml)
[![build](https://github.com/Zncl2222/Stochastic_UC_SGSIM/actions/workflows/cmake.yml/badge.svg)](https://github.com/Zncl2222/Stochastic_UC_SGSIM/actions/workflows/cmake.yml)
[![build](https://github.com/Zncl2222/Stochastic_UC_SGSIM/actions/workflows/codeql.yml/badge.svg)](https://github.com/Zncl2222/Stochastic_UC_SGSIM/actions/workflows/codeql.yml)
[![codecov](https://codecov.io/github/Zncl2222/Stochastic_UC_SGSIM/branch/main/graph/badge.svg?token=3qZt0OqDNI)](https://app.codecov.io/github/Zncl2222/Stochastic_UC_SGSIM)

#### Python Sonar Cloud state
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=zncl2222_Stochastic_UC_SGSIM_py&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=zncl2222_Stochastic_UC_SGSIM_py)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=zncl2222_Stochastic_UC_SGSIM_py&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=zncl2222_Stochastic_UC_SGSIM_py)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=zncl2222_Stochastic_UC_SGSIM_py&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=zncl2222_Stochastic_UC_SGSIM_py)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=zncl2222_Stochastic_UC_SGSIM_py&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=zncl2222_Stochastic_UC_SGSIM_py)


#### C Sonar Cloud state
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=zncl2222_Stochastic_UC_SGSIM_c&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=zncl2222_Stochastic_UC_SGSIM_c)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=zncl2222_Stochastic_UC_SGSIM_c&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=zncl2222_Stochastic_UC_SGSIM_c)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=zncl2222_Stochastic_UC_SGSIM_c&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=zncl2222_Stochastic_UC_SGSIM_c)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=zncl2222_Stochastic_UC_SGSIM_c&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=zncl2222_Stochastic_UC_SGSIM_c)


<h3 align="center">

> __Warning__
> This project is still in the pre-dev stage, the API usuage may be subject to change

</h3>

## UnConditional Sequential Gaussian SIMulation (UCSGSIM)

<h3 align="center">An unconditional random field generation tools that are easy to use.</h3>

## Introduction of UCSGSIM
Sequential Gaussian Simulation is a random field generation method which was based on the kriging interporlation method.

Unconditonal simulation don't follow the patterns of "data", but follow the users's settings like mean and variance.

**The core ideas of UCSGSIM are:**
1. Create the grid (no any data value exist now).

$$ \Omega\to R $$

2. Visit random point of the model (draw one random value of the x_grid)

$$ X = RandomValue(\Omega),  X:\Omega\to R $$

3. Select the **theoritical covariance model** to use, and set the **sill** and **range** properly.

$$ Gaussian = (C_{0} - s)(1 - e^{-h^{2}/r^{2}a})$$

$$ Spherical = (C_{0} - s)(3h/2r - h^3/2r^3)$$

$$ Exponential = (C_{0} - s)(1 - e^{-h/ra})$$

4. If there have more than 1 data value closed to the visted point (depend on the **range** of covariance model), then go next step. Else draw the random value from normal distribution as the simulation results of this iteration.

$$ Z_{k}({X_{simulation}}) = RandomNormal(m = 0 ,\sigma^2 = Sill)$$

5. Calculate **weights** from the **data covaraince** and **distance coavariance**

$$ \sum_{j=1}^{n}\omega_{j} = C(X_{data}^{i},X_{data}^{i})C^{-1}(X_i,X_i), i=1...N $$

6. Calculate the **kriging estimate** from the **weight** and **data value**

$$ Z_{k}(X_{estimate}) = \sum_{i=1}^{n} \omega_{i} Z(X_{data}) + (1- \sum_{i=1}^{n} \omega_{i} m_{g}) $$

7. Calculate the **kriging error (kriging variance)** from **weights** and **data covariance**

$$ \sigma_{krige}^{2} = \sum_{i=1}^{n}\omega_{i}C(X_{data}^{i},X_{data}^{i}) $$

8. Draw the random value from the normal distribution and add to the **kriging estimate**.

$$ Z(X_{simulation}) = Z(X_{estimate}) + RandomNormal(m = 0, \sigma^2 = \sigma_{krige}^{2}) $$

9. Repeat 2 ~ 8 until the whole model are simulated.

10. Repeat 1 ~ 9 with different **randomseed number** to produceed mutiple realizations.

## Installation
```bash
pip install uc-sgsim
```

## Features
* One dimensional unconditional randomfield generation with sequential gaussian simulation algorithm
* Enable to use muti-cores to run the simulation (mutiprocessing)
* Run C to generate randomfield in python via ctype interface, or just generate randomfield in python with numpy and scipy library.



## Example
```py
import matplotlib.pyplot as plt
import uc_sgsim as uc
from uc_sgsim.cov_model import Gaussian

if __name__ == '__main__':
    x = 151  # Model grid, only 1D case is support now
    bw_s = 1  # lag step
    bw_l = 35  # lag range
    randomseed = 12321  # randomseed for simulation
    a = 17.32  # effective range of covariance model
    C0 = 1  # sill of covariance model

    nR = 10  # numbers of realizations in each CPU cores,
    # if nR = 1 n_process = 8
    # than you will compute total 8 realizations

    # Create Covariance model first
    Cov_model = Gaussian(bw_l, bw_s, a, C0)

    # Create simulation and input the Cov model
    sgsim = uc.UCSgsim(X, Cov_model, nR)  # Create class instance that generate field in python
    sgsim_c = uc.UCSgsimDLL(x, Cov_model, nR) # Create class instance that generate field in c

    # Start compute with n CPUs
    sgsim.compute_async(n_process=8, randomseed=454) # Generate field (python)
    sgsim_c.compute(n_process=2, randomseed=151) # Generate field (c)

    sgsim.mean_plot('ALL')  # Plot mean
    sgsim.variance_plot()  # Plot variance
    sgsim.cdf_plot(x_location=10)  # CDF
    sgsim.hist_plot(x_location=10)  # Hist
    sgsim.variogram_compute(n_process=2)  # Compute variogram before plotting
    # Plot variogram and mean variogram for validation
    sgsim.vario_plot()
    # Save random_field and variogram
    sgsim.save_random_field('randomfield.csv', save_single=True) # save in single file
    sgsim.save_variogram('') # save each field individually

    # plt.show() to show the matplotlib plot
    plt.show()

    # Please note that the parameter "n_realizations" means the number of realizations calculate in each process,
    # so this case will generate total 20 * 4(process) = 80 realizations

```


<p align="center">
   <img src="https://github.com/Zncl2222/Stochastic_SGSIM/blob/main/figure/Realizations.png"  width="40%"/>
   <img src="https://github.com/Zncl2222/Stochastic_SGSIM/blob/main/figure/Mean.png"  width="40%"/>
   <img src="https://github.com/Zncl2222/Stochastic_SGSIM/blob/main/figure/Variance.png"  width="40%"/>
   <img src="https://github.com/Zncl2222/Stochastic_SGSIM/blob/main/figure/Variogram.png"  width="50%"/>
   <img src="https://github.com/Zncl2222/Stochastic_SGSIM/blob/main/figure/HIST.png"  width="40%"/>
   <img src="https://github.com/Zncl2222/Stochastic_SGSIM/blob/main/figure/CDF.png"  width="50%"/>
</p>

## Future plans
* 2D unconditional randomfield generation
* GUI mode in pyhton package
* More covariance models
* More kriging methods (etc. Oridinary Kriging)
* Performance enhancement
* More completely documents and easy to use designs.

## Performance
<p align="center">
<img src="https://github.com/Zncl2222/Stochastic_SGSIM/blob/main/figure/C_Cpp_py_comparision.png"  width="70%"/>
</p>

```
Parameters for testing:

model len = 150

number of realizations = 1000

Range scale = 17.32

Variogram model = Gaussian model

---------------------------------------------------------------------------------------

Testing platform:

CPU: AMD Ryzen 9 4900 hs

RAM: DDR4 - 3200 40GB (Dual channel 16GB)

Disk: WD SN530
```
