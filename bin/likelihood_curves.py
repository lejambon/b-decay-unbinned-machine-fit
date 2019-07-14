#!/usr/bin/env python
"""
Plot each coefficient vs. negative log likelihood whilst keeping other coefficients fixed at signal values.

The blue curve is the likelihood curve. The red line denotes the true signal value.
"""

import matplotlib.pyplot as plt
import numpy as np
import tensorflow.compat.v2 as tf

import b_meson_fit as bmf

tf.enable_v2_behavior()

plot_points = 50
plot_min = -12.0
plot_max = 12.0


# Use autograph for performance
@tf.function
def nll(coeffs_, signal_events_):
    return bmf.signal.normalized_nll(coeffs_, signal_events_)


def try_nll(pos_, val):
    # Override the coeff we want to vary
    try_coeffs[pos_] = tf.constant(val)
    return nll(try_coeffs, signal_events)


with bmf.Script() as script:
    signal_coeffs = bmf.coeffs.signal()
    signal_events = bmf.signal.generate(signal_coeffs)
    fit_coeffs = bmf.coeffs.fit()

    # For each amplitude
    for a_idx in range(0, bmf.coeffs.amplitude_count):
        # If this amplitude is fixed in this basis then ignore it
        if not bmf.coeffs.is_trainable(fit_coeffs[a_idx*bmf.coeffs.param_count]):
            continue

        fig, axes = plt.subplots(bmf.coeffs.param_count)
        fig.suptitle(bmf.coeffs.amplitude_latex_names[a_idx])

        # For each param in this amplitude
        for p_idx in range(0, bmf.coeffs.param_count):
            c_idx = a_idx * bmf.coeffs.param_count + p_idx
            bmf.stdout('Processing {} ({})'.format(bmf.coeffs.names[c_idx], c_idx))

            # Set all coeffs to the constant signal ones
            try_coeffs = bmf.coeffs.signal()

            c_range = np.linspace(plot_min, plot_max, plot_points, dtype=np.float32)

            with tf.device('/device:GPU:0'):
                axes[p_idx].plot(c_range, list(map(lambda c_val: try_nll(c_idx, c_val).numpy(), c_range)))

            # Add the param's greek letter on the Y-axis
            axes[p_idx].set_ylabel(bmf.coeffs.param_latex_names[p_idx])

            # Draw a red line to represent the signal
            axes[p_idx].axvline(signal_coeffs[c_idx].numpy(), ymax=0.5, color='r')

        plt.show()
