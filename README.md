## Introduction

This project is for doing an unbinned `B0 → K* μ μ` angular observable fit based on this
[paper](https://arxiv.org/abs/1504.00574) but using Tensorflow. The fitting is done to a generated toy signal.
See [coeffs.py](./b_meson_fit/coeffs.py) for the values used. This dissertation produced from this work can be found
at [here](./Dissertation.pdf).

## Requirements

Ensure Tensorflow `1.14` is installed either via from source,
or the `tensorflow-cpu` or `tensorflow-gpu` pip packages. E.g.
```
pip install --user --upgrade 'tensorflow-gpu==1.14.*'
```

Install dependencies:
```
pip install --user --upgrade --upgrade-strategy only-if-needed -r requirements.txt
```

To run scripts at the CLI your `PYTHONPATH` will need setting correctly. One way of doing that is adding
`export PYTHONPATH="/path/to/repo"` to your `~/.bashrc`.

## Development

This software has been developed on Linux with Python 3.6 and the [PyCharm](https://www.jetbrains.com/pycharm/) IDE.
The unit tests and scripts should just run within PyCharm with no configuration necessary. Whilst none of this software
has been tested on Windows, there aren't any known reasons why it wouldn't run.

The first time scripts are run it may take a long time to start when using the GPU as CUDA creates its compute cache.
Subsequent runs should all start faster.

Unit tests can be run from the CLI by running the following from the project folder:

```
$ python -m unittest
```

## Fitting

The script [fit.py](./bin/fit.py) can be used to run a fitting ensemble. Run `./bin/fit.py --help` to see all options
and defaults.

You can run it for multiple iterations with either the `-i` or `--iterations` arguments. E.g.:

```
$ ./bin/fit.py -i 1000
```

Results can be logged to a CSV file with the `-c` or `--csv` arguments. If the script is quit, it will continue
appending to the same file when it is restarted. E.g.:

```
$ ./bin/fit.py -i 1000 -c myfile.csv
```

The model to use for the signal coefficients can be specified with the `-S` or `--signal-model` options. The
 default is `SM`. E.g.:

```
$ ./bin/fit.py -i 1000 -c SM_run.csv -S SM
$ ./bin/fit.py -i 1000 -c NP_run.csv -S NP
```

The initialization scheme for the fit coefficients can be chosen with the `-f` or `--fit-init` options. 
You can use a specific algorithm. E.g.:

```
$ ./bin/fit.py -f TWICE_LARGEST_SIGNAL_SAME_SIGN
```

The algorithms available are:

 * `TWICE_LARGEST_SIGNAL_SAME_SIGN`: Initialize coefficients from `0` to `2x` the largest value for each coefficient
  in all signal models. This is the default.
 * `TWICE_CURRENT_SIGNAL_ANY_SIGN`: Initialize coefficients from `-2x` to `+2x` the value in the signal model used.
 * `CURRENT_SIGNAL`: Initialize coefficients to the same values as the signal model used.
 
Alternatively the fit coefficients can all be initialized to a specific value.
To do that specify a floating point number. E.g.:

```
$ ./bin/fit.py -f 123.456
```

The target device (e.g. `GPU:0`, `GPU:1`, `CPU:0` etc.) can be specified with `-d` or `--device`. This can be useful
if you want to start multiple scripts in parallel running on different devices. The value defaults to `GPU:0`. E.g.:

```
$ ./bin/fit.py -i 1000 -c myfile_gpu3.csv -d GPU:3
```

The optimizer (`-o`/`--opt-name`), learning rate (`-r`/`--learning-rate`) and additional optimizer parameters
(`-p`/`--opt-param`) can be supplied. E.g.

```
$ ./bin/fit.py -o Adam -r 0.01 -p beta_1 0.95 -p epsilon 1e-3
```

Gradient clipping by global norm is disabled by default, but can be enabled with the `-P` or `--grad-clip` arguments.
E.g.

```
$ ./bin/fit.py -P 2.5
```

The fits will be considered converged when the maximum gradient for any coefficient is less than `5e-7`. You can change
this value with the `-u` or `--grad-max-cutoff` arguments:

```
$ ./bin/fit.py -u 1e-8
```

If you set `-u`/`--grad-max-cutoff` or change the optimizer defaults, you may also want to specify 
`-m`/`--max-step`. This controls the max number of iterations before a fit is restarted
(defaults to 20,000). If the initialisation scheme randomises coefficients then the signal will be retried, otherwise a
new signal will be generated. E.g.:

```
$ ./bin/fit.py -u 1e-8 -m 100000
```

## Q test statistic

The script [q\_test\_statistic.py](./bin/q_test_statistic.py) can be used to generate Q test statistics. The script
allows all options that [fit.py](./bin/fit.py) does.

Additionally the `-n`/`--null-model` and  `-t`/`--test-model` arguments are mandatory. These specify which
signal coefficient model the P-wave fit coefficients should be fixed to for the null and test hypotheses respectively.

An example usage is:

```
$ ./bin/q_test_statistic.py -c Q_NP.csv -i 1000 -S NP -t NP -n SM
$ ./bin/q_test_statistic.py -c Q_SM.csv -i 1000 -S SM -t NP -n SM
```

## Plotting

Various scripts exist to generate plots. They should be runnable within PyCharm, or if you want to export the plots,
runnable at the CLI with the optional `-w` or `--write-svg` options. Some scripts require the string `%name%` within
the `--write-svg` argument string which will be replaced for example when writing plotting of coefficients. Run
any script with `-h` or `--help` to see the full list of options and defaults. Some scripts will also output
values of interest when they run.

Plot Breit-Wigner distributions:

```
$ ./bin/plot_breit_wigner.py -w breit_wigner.svg
```

Plot spin amplitudes (takes an optional `-S`/`--signal-model` argument):

```
$ ./bin/plot_amplitudes.py -S NP -w amplitude_NP_%name%.svg
```

Plot angular observables (takes an optional `-S`/`--signal-model` argument):

```
$ ./bin/plot_angular_observables.py -S NP -w observable_NP_%name%.svg
```

Plot S-wave fraction (takes an optional `-S`/`--signal-model` argument):

```
$ ./bin/plot_frac_s.py -S NP -w frac_s_NP.svg
```

Plot differential decay rate (takes an optional `-S`/`--signal-model` argument):

```
$ ./bin/plot_differential_decay_rate.py -S NP -w differential_decay_rate_NP.svg
```

Plot generated signal events for each independent variable (takes optional `-S`/`--signal-model` and
`-s`/`--signal-count` arguments):

```
$ ./bin/plot_signal.py -S NP -w signal_NP_%name%.svg
```

Plot fit distributions (takes a list of CSV files from [fit.py](./bin/fit.py) and an optional name for each one
to put in the legend):

```
$ ./bin/plot_fit_distributions.py -w fit_single_%name%.svg fit1.csv
$ ./bin/plot_fit_distributions.py -w fit_combined_%name%.svg fit1.csv fit2.csv
$ ./bin/plot_fit_distributions.py -w fit_combined_named_%name%.svg fit1.csv:'Fit 1' fit2.csv:'Fit 2'
```

Plot pulls (takes a list of CSV files from [fit.py](./bin/fit.py) and an optional name for each one
to put in the legend):

```
$ ./bin/plot_pulls.py -w pull_single_%name%.svg fit1.csv
$ ./bin/plot_pulls.py -w pull_combined_%name%.svg fit1.csv fit2.csv
$ ./bin/plot_pulls.py -w pull_combined_named_%name%.svg fit1.csv:'Fit 1' fit2.csv:'Fit 2'
```

Plot confidence levels for each coefficient (takes a single CSV file from [fit.py](./bin/fit.py)):

```
$ ./bin/plot_confidence.py -w confidence_%name%.svg fit1.csv
```

Plot a fit stat (signal, abs\_signal, diff, std_err, pull\_mean) against another stat (takes mandatory
`-x`/`--x-axis` and `-y`/`--y-axis` arguments plus a list of CSV files from [fit.py](./bin/fit.py) and an optional 
name for each one to put in the legend):

```
$ ./bin/plot_fit_stats.py -x abs_signal -y std_err -w std_err_vs_abs_signal.svg fit1.csv:'Fit 1' fit2.csv:'Fit 2'
```

Plot Q statistics and calculate sigma level (takes two mandatory arguments for the SM and NP csv file from
[q\_test\_statistic.py](./bin/q_test_statistic.py) to use. Also takes an optional `-b`/`--bins` argument to control
the number of histogram bins to calculate for plotting):

```
$ ./bin/plot_q_test_statistic.py -w q_test_statistic.svg q_sm.csv q_np.csv
```

## Using Tensorboard

[Tensorboard](https://www.tensorflow.org/guide/summaries_and_tensorboard) can be used to tune the optimizer. Values
will be logged for Tensorboard from either the [compare\_optimizers.py](./bin/compare_optimizers.py),
[fit.py](./bin/fit.py), or [q\_test\_statistic.py](./bin/q_test_statistic.py) scripts with the `-l` or `--log` arguments.
Note that logging statistics has a large performance hit so should not be used for production runs.
Once scripts that have logging enabled start, they will output the command to start Tensorboard.
Additionally they will output a `Filter regex` that can be used in the left hand pane of the `Scalars` page to filter
that particular run.

## Profiling

Profiling can be achieved through the [profile.py](./bin/profile.py) script and viewed in Tensorboard. More about how
to use the `Profile` tab can be found
 [here](https://www.tensorflow.org/tensorboard/r2/tensorboard_profiling_keras#trace_viewer).

The script must be run as root due to Nvidia's 
["recent permission restrictions"](https://devtalk.nvidia.com/default/topic/1047744/jetson-agx-xavier/jetson-xavier-official-tensorflow-package-can-t-initialize-cupti/post/5319306/#5319306).
You can run it from the project folder with:
```
$ sudo -E --preserve-env=PYTHONPATH ./bin/profile.py
```
Once the script starts it will output the command to start Tensorboard (which shouldn't be run as root).

If you get errors when running it about missing CUPTI libraries then you will need to locate your CUPTI lib
directory and add it to ldconfig. For Gentoo Linux this can be done with:

```
# echo '/opt/cuda/extras/CUPTI/lib64' > /etc/ld.so.conf.d/cupti.conf
# ldconfig
```

That directory is almost certainly different in other Linux distributions.

Note that the Profile tab in Tensorboard only works in Chrome. In Firefox you will get a blank page.

## Publication Data

Data was generated for publication by running the [generate\_data.sh](./bin/generate_data.sh) bash script.

Values and plots were subsequently mined by the [process\_data.sh](./bin/process_data.sh) bash script. This
script will log to the file `results/process_data.log` so that outputted values of interest can be later found.

## Misc scripts

The other scripts take no arguments and do the following:

* [benchmark.py](./bin/benchmark.py): Tests speed of key fit functions. Frequently used to test for performance 
regressions during development. You should run this before and after modifying PDF terms as Tensorflow's 
[autograph](https://www.tensorflow.org/guide/autograph) can be quite particular
* [coeff\_contours.py](./bin/coeff_contours.py): Produces a surface plot of the negative log likelihood by scanning
over two coefficients whilst keeping the rest at signal values. Used during early development to ensure minima
existed. To change the two coefficients plotted, change the `cx_idx` and `cy_idx` IDs in that file.
* [coeff\_curves.py](./bin/coeff_curves.py): Produces plots of the negative log likelihood for each coefficient by
scanning them whilst keeping the rest at signal values. Used during early development to ensure minima existed.
* [compare\_optimizers.py](./bin/compare_optimizers.py): Takes combinations of optimizer algorithms and parameters
defined in the `combos` variable in that file and logs the fits for viewing in Tensorboard. Useful for picking
macro machine learning options (e.g. which optimizer to use). For more subtle settings an ensemble fit should be
performed instead as [compare\_optimizers.py](./bin/compare_optimizers.py) fixes all initial coefficients to `1.0`
so that comparison is possible - which isn't very realistic.
* [table\_mean\_err\_pull.py](./bin/table_mean_err_pull.py): Output the LaTeX for a table of signal values, means,
standard errors and pull means for a given CSV fit file. Takes a CSV file as a single argument. Used for publication
* [table\_signal\_coeffs.py](./bin/table_signal_coeffs.py): Output the LaTeX for a table of all the coefficient values.
Used for publication.
* [time\_taken.sh](./bin/time_taken.sh): Takes a CSV file as an argument and outputs the average time taken per fit.


## Making modifications

Listed here are some modifications you may wish to make and how to do them. At minimum, you should check
the unit tests still pass before you commit.

### Adding/changing signal coefficients

To add a new signal model or modify existing signal model coefficients, see the `_signal_coeffs` list in
[coeffs.py](./b_meson_fit/coeffs.py).

### Changing trainable coefficients

To change what coefficients are trained by Tensorflow, modify the `fit_trainable_idxs` list in 
[coeffs.py](./b_meson_fit/coeffs.py). IDs `0-11` correspond to `a_para` followed by `12-23` for `a_perp`,
`24-35` for `a_0` and `36-47` for `a_00`. Within each block of 12, the first 6 are `left` and the last
6 are `right`. Within those blocks the first 3 are `real` and the last 3 are `imaginary`. Those blocks of
3 correspond to `alpha`, `beta` and `gamma`. So for example, 2 is `a_para_l_re_gamma`, 3 is
`a_para_l_im_alpha`, 6 is `a_para_r_re_alpha` and 47 is `a_00_r_im_gamma`.

### Changing the masses and decay widths for BW distributions

Modify the `mass_*` and `decay_width_*` values at the top of
[breit\_wigner.py](./b_meson_fit/breit_wigner.py).

## Roadmap

Fixes needed:

* Change signal coefficient values to ones that produce correct shaped observable plots (see paper)
* Replace `a_00_*` signal coefficient values with proper values (see paper)
* If a fit is partially written to a CSV, the signal coefficients are changed, and then the fit is resumed, the fitting
script will rightly complain about the change and refuse to continue. However if the TWICE\_LARGEST\_SIGNAL\_SAME\_SIGN
algorithm is being used and either another signal model is added or another signal model is changed, then when resuming
the fit script won't notice if the coefficient initialisation values are different to what they were when the ensemble
started. One way of fixing this would be to write an extra header row in the CSV to say what the initialisation values
were when first started. The fit script could either continue using those, or refuse to start if they're different.

Further work:

* Tune the optimizer better to improve fitting performance and quality.
* Add support for B0 bar (implement CP-averaged and CP-asymmetric observables)
* Add background. Will need B-meson mass term in PDF, a background event generator composed of polynomials,
and fitting based on nuisance parameters for those polynomials.

Potential cleanups:

* Move uses of `csv.DictReader` into a CSV reader class
* Move calculating means, std errs, pulls etc. to a library. Possibly part of above.
* Split `signal.py` into other files (e.g. `observables.py`, `decay_rate.py`). Without negatively affecting fit
performance, address the fact that some of those  functions take a flat coefficient list but others take amplitudes
(the  3 `decay_rate_angle_integrated*()` functions are a good example of this inconsistency as can be seen
in `plot_frac_s.py`)
* Combine plotters into single script