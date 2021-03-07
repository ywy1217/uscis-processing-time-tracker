# Acknowledgement
# This script is adapted from 'APMonitor.com'
# Original Website: https://apmonitor.com/che263/index.php/Main/PythonRegressionStatistics

import pandas as pd
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy import stats
import uncertainties.unumpy as unp
import uncertainties as unc


def lin1d_f(x, a, b):
    return a * x + b


def pred_band(x, xd, yd, p, func=lin1d_f, conf=0.95):
    # x = requested points
    # xd = x data
    # yd = y data
    # p = parameters
    # func = function name
    alpha = 1.0 - conf  # significance
    N = xd.size  # data sample size
    var_n = len(p)  # number of parameters
    # Quantile of Student's t distribution for p=(1-alpha/2)
    q = stats.t.ppf(1.0 - alpha / 2.0, N - var_n)
    # Stdev of an individual measurement
    se = np.sqrt(1. / (N - var_n) * np.sum((yd - func(xd, *p)) ** 2))
    # Auxiliary definitions
    sx = (x - xd.mean()) ** 2
    sxd = np.sum((xd - xd.mean()) ** 2)
    # Predicted values (best-fit model)
    yp = func(x, *p)
    # Prediction band
    dy = q * se * np.sqrt(1.0 + (1.0 / N) + (sx / sxd))
    # Upper & lower prediction bands.
    lpb, upb = yp - dy, yp + dy
    return lpb, upb


def conf_band(x_new, p, func=lin1d_f, conf=0.95):
    # x_new = requested points
    # p = parameters (now correlated a and b in this application)
    # func = function name

    # calculate regression confidence interval
    # print('params,', p)
    py = func(x_new, *p)
    nom = unp.nominal_values(py)
    std = unp.std_devs(py)

    conf_band_percent = stats.norm.ppf((1.0 + conf) / 2.0)
    lcb, ucb = nom - conf_band_percent * std, nom + conf_band_percent * std

    return nom, lcb, ucb


def curve_fit_package(px, x, y, func=lin1d_f, conf=0.95):

    popt, pcov = curve_fit(func, x, y)
    popts_with_unc = unc.correlated_values(popt, pcov)

    # # retrieve parameter values
    # print('Optimal Values')
    # print('a: ' + str(popt[0]))
    # print('b: ' + str(popt[1]))
    # # compute r^2
    # r2 = 1.0 - (sum((y - lin1d_f(x, *popt)) ** 2) / ((n - 1.0) * np.var(y, ddof=1)))
    # print('R^2: ' + str(r2))
    # # calculate parameter confidence interval

    # print('Uncertainty')
    # print('a: ' + str(popts_with_unc[0]))
    # print('b: ' + str(popts_with_unc[1]))

    # get confidence intervals and prediction band
    # print('confidence level:', conf)
    nom, lcb, ucb = conf_band(px, popts_with_unc, func, conf=conf)
    lpb, upb = pred_band(px, x, y, popt, func, conf=conf)
    conf_bands = (lcb, ucb)
    pred_bands = (lpb, upb)

    return nom, conf_bands, pred_bands, popts_with_unc


if __name__ == '__main__':
    # x = pd.Series(data=range(50))
    # y = x + np.random.rand(50)
    # import data
    url = 'https://apmonitor.com/che263/uploads/Main/stats_data.txt'
    data = pd.read_csv(url)
    x = data['x'].values
    y = data['y'].values
    n = len(y)

    px = np.linspace(14, 24, 100)

    nom_val, (lcb, ucb), (lpb, upb), fit_coefs = curve_fit_package(px, x, y)

    fig, ax = plt.subplots()

    # plot data
    plt.scatter(x, y, s=1)
    # plot the regression
    plt.plot(px, nom_val, c='black', label='y=({:.3e}) x + ({:.3e})'.
             format(*(unp.nominal_values([fit_coefs[0], fit_coefs[1]]))))

    # uncertainty lines (95% confidence)
    verts = list(zip(px, lcb)) + list(zip(px[::-1], ucb[::-1]))
    poly = Polygon(verts, closed=True, fc='orange', ec='orange', alpha=0.2,
               label="CI (95%)")
    ax.add_patch(poly)
    # plt.plot(px, lcb, c='orange', label='95% Confidence Region')
    # plt.plot(px, ucb, c='orange')

    # prediction band (95% confidence)
    verts = list(zip(px, lpb)) + list(zip(px[::-1], upb[::-1]))
    poly = Polygon(verts, closed=True, fc='c', ec='c', alpha=0.1,
                   label="95% Prediction Band")
    ax.add_patch(poly)
    # plt.plot(px, lpb, 'k--', label='95% Prediction Band')
    # plt.plot(px, upb, 'k--')
    plt.ylabel('y')
    plt.xlabel('x')
    plt.legend(loc='best')
    # save and show figure
    plt.show()
