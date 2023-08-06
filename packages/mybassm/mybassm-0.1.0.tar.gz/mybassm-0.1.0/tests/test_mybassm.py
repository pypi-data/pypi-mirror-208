#!/usr/bin/env python

"""Tests for `markbassmodel` package."""

import pytest


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string



from mybassm.mybassm import diffusion, bass_f, bass_F, predict_bass_model
import numpy as np

def test_diffusion():
    sales = np.array([10, 20, 30, 40, 50])
    t = np.array([1, 2, 3, 4, 5])
    params = diffusion(sales, t)
    assert isinstance(params, dict)
    assert 'p' in params and 'q' in params and 'm' in params

def test_bass_f():
    t = np.array([1, 2, 3, 4, 5])
    p = 0.03
    q = 0.25
    result = bass_f(t, p, q)
    assert isinstance(result, np.ndarray)
    assert len(result) == len(t)

def test_bass_F():
    t = np.array([1, 2, 3, 4, 5])
    p = 0.03
    q = 0.25
    result = bass_F(t, p, q)
    assert isinstance(result, np.ndarray)
    assert len(result) == len(t)

def test_predict_bass_model():
    params = (0.03, 0.25, 100)
    t = np.array([6, 7, 8, 9, 10])
    result = predict_bass_model(params, t)
    assert isinstance(result, np.ndarray)
    assert len(result) == len(t)
    
test_diffusion()
