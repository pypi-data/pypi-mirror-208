"""Main module."""
# bassmodel/bass.py

import numpy as np
from scipy.optimize import minimize
from scipy.integrate import quad
import matplotlib.pyplot as plt
import numpy as np


"""
Module: bass_functions

This module contains functions related to the Bass diffusion model.

Functions:
- bass_f(t, p, q): Calculate the Bass diffusion function for a given time `t` and parameters `p` and `q`.
-calc_bass_parameters(data)

"""

def diffusion(sales, t = None):
    """
    Fits a Bass diffusion model to sales data using nonlinear least squares optimization.

    Parameters
    ----------

    sales: An array of sales data.
    t: An optional array of time values corresponding to the sales data.
              If not specified, a default time array will be generated.

    :return: A dictionary containing the estimated Bass model parameters p, q, and m.
    """
    if t is None:
        t = np.arange(len(sales))
    else:
        if len(t) != len(sales):
            raise ValueError("The length of 't' must be the same as the length of 'sales'.")

    def objective(w):
        p, q, m = w
        f = m * (1 - np.exp(-(p + q) * t)) / (1 + q / p * np.exp(-(p + q) * t))
        return np.sum((f - sales) ** 2)

    x0 = np.array([0.01, 0.1, np.max(sales)])
    res = minimize(objective, x0, method='Nelder-Mead')
    w = res.x
    return {'p': w[0], 'q': w[1], 'm': w[2]}

def adoption_rate(t, p, q, m, N):
    """
    Parameters
    ----------
    t : float or numpy.ndarray
        Time.
    p : float
        Coefficient of innovation.
    q : float
        Coefficient of imitation.
    m : float
        Total potential market size.
    N : float
        Total number of adopters.

    Returns
    -------
    rate : float or numpy.ndarray
        Adoption rate at time `t`.
    """
    return p * (m - N) + q * N * (N / m)



def bass_f(t, p, q):
    """
    Calculates the fraction of the total market that has adopters at time `t` using the Bass diffusion model.

        Parameters
        ----------
        t : numpy.ndarray
            An array of time values.
        p : float
            Coefficient of innovation.
        q : float
            Coefficient of imitation.

        Returns
        -------
        numpy.ndarray
            The fraction of the total market that adopts at times `t` with parameters `p` and `q`.

        References
        ----------
        Bass, F. M. (1969). A new product growth for model consumer durables. Management science, 15(5), 215-227.
    """
    exp_term = np.exp(-(p + q) * t)
    return (p + q) / p * (exp_term * q) / (1 + (q / p) * exp_term) ** 2


def bass_F(t, p, q):
    """
    Calculates the fraction of the total market that has adopted up to and including time `t` using the Bass diffusion model.

    Parameters
    ----------
    t : numpy.ndarray
        Time values.
    p : float
        Coefficient of innovation.
    q : float
        Coefficient of imitation.

    Returns
    -------
    numpy.ndarray
        The fraction of the total market that has adopted up to and including times `t` with parameters `p` and `q`.

    References
    ----------
    Bass, F. M. (1969). A new product growth for model consumer durables. Management science, 15(5), 215-227.

    """
    exp_term = np.exp(-(p + q) * t)
    return 1 - (q / p) * (1 / (1 + (q / p) * exp_term)) * (1 - exp_term)


def predict_bass_model(params,t):
    """
    Predicts future adoption rates based on a given set of time periods and the estimated Bass model parameters.

    Parameters:
    -----------
    params : tuple
        A tuple of the estimated Bass model parameters (p, q, m)
    t : array-like
        An array-like object of time periods to predict the adoption rates for

    Returns:
    --------
    y_pred : array-like
        An array-like object of predicted adoption rates for the given time periods
    """
    p, q, m = params
    y_pred = m * ((p + q)**2 / p * np.exp(-(p + q) * t)) / (1 + (q / p) * np.exp(-(p + q) * t))**2
    return y_pred

def plot_bass_model(params, y_pred):
    """
    Generates a plot of the predicted adoption rates over time based on the estimated Bass model parameters.

    Parameters:
    -----------
    params : tuple
        A tuple of the estimated Bass model parameters (p, q, m)
    y_pred : array-like
        An array-like object of predicted adoption rates for a set of time periods
    """
    plt.plot(y_pred, label='Predicted')
    plt.xlabel('Time')
    plt.ylabel('Adoption Rate')
    plt.title('Bass Diffusion Model')
    plt.legend()
    plt.show()

def plot_bass(p, q, title):
    """
    Generates a plot of the predicted adoption rates over time based on the estimated Bass model parameters and gies comulativve adapttion too.

    Parameters:
    -----------
    params : tuple
        A tuple of the estimated Bass model parameters (p, q, m)
    title: string
        A string thatgives inforamtion about what the plot is 2
    y_pred : array-like
        An array-like object of predicted adoption rates for a set of time periods
    """
    cum_ad = plt.plot(np.arange(0, 16), [quad(partial(bass_F, p=p, q=q), 0, t)[0] for t in range(0, 16)], label="cumulative adoptions")
    time_ad = plt.plot(np.arange(0, 16), [quad(partial(bass_f, p=p, q=q), 0, t)[0] for t in range(0, 16)], label="adoptions at time t")
    plt.title(f"{title}")
    plt.legend()
    plt.show()