==================
Bass Model Package
==================

Overview
--------

The Bass Model Package provides various functions for analyzing and predicting the diffusion of innovative products using the Bass Model. This package is based on the paper "Forecasting the Diffusion of Innovative Products Using the Bass Model at the Takeoff Stage" by Suddhachit Mitra and Professor Hovhanissyan lectures.

Features
--------

- Calculate diffusion using the Bass Model.
- Estimate parameters using the `bass_f` function.
- Generate cumulative adoption curve using the `bass_F` function.
- Predict future adoption using the `predict_bass_model` function.
- Plot the predicted adoption curve.

Installation
------------

You can install the Bass Model Package from PyPI using pip:

.. code-block:: shell

    $ pip install mybassm


Usage
-----

The package provides the following main functions:

- diffusion: Calculate the diffusion of the product based on the Bass Model.
- bass_f: Calculates the fraction of the total market that has adopters at time `t` using the Bass diffusion model.
- bass_F: Calculates the fraction of the total market that has adopted up to and including time t using the Bass diffusion model.
- predict_bass_model: Predicts future adoption rates based on a given set of time periods and the estimated Bass model parameters.



Examples
--------

Here's a simple example to demonstrate the usage of the Bass Model Package:

.. code-block:: python

        from mybassm.mybassm import diffusion, bass_f, bass_F, predict_bass_model

        # Calculate diffusion
        diffusion_rate = diffusion(sales, t)

        # Estimate Bass Model parameters
        p, q = bass_f(t, p, q)

        # Generate cumulative adoption curve
        t_values, cumulative_adoption = bass_F(t, p, q)

        # Predict future adoption
        params= p,q,m
        predicted_adoption = predict_bass_model(params, t)

        #Plots the bass model 
        plot_bass_model(params, y_pred)
        plot_bass(p, q, title)


License
-------

The Bass Model Package is released under the MIT License. For more information, see the LICENSE

References
----------

- Suddhachit Mitra, "Forecasting the Diffusion of Innovative Products Using the Bass Model at the Takeoff Stage."
- Professor Hovhanissyan lectures.

Contributing
------------

Contributions are welcome! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request on the `Github <https://github.com/anukzak22/mybassm>`_

Authors
-------

Anahit Zakaryan
