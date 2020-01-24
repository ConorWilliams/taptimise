# Taptimise
Second generation tap optimisation algorithm for the eWaterPay project.

See the results here: [https://conorwilliams.github.io.](https://conorwilliams.github.io.)

## Installation (verbose)
Verify your python and pip distributions are correctly installed. You can test this by running `python -V` and `pip -V`. On some machines with both python 2 & 3 these commands are replaced with `python3 -V` and `pip3 -V` respectively.

On windows you will need a terminal with root access to install Taptimise i.e you must search `cmd` into your search bar, right click and press "run as administrator".

#### With Git (recommended)

If [Git](https://git-scm.com/download/win) is installed and accesable from the command line (test with `git --version`). Install Taptimise using pip with: `pip install git+https://github.com/ConorWilliams/taptimise` verify the installation by running: `taptimise -V`.

#### Without Git

Press on the "Clone or download" button and "Download ZIP". Extract the ZIP archive. `cd` into the extracted folder (probably `taptimise-master`) and install Taptimise with `pip install .` (including the .) verify the installation by running: `taptimise -V`.

#### Test

Still within the extracted Taptimise folder, to run a full test on one of the example villages run `taptimise test/e1.csv 1000` and view the generated report `test/e1_report.html` in your web browser.

## Usage

#### Basic
To run Taptimise with the default setting use:
`taptimise path/to/file.csv tap_load`. The csv containing the house positions
should be formatted exactly as per the
[example](https://github.com/ConorWilliams/taptimise/tree/master/test) csv's.
I.e comma no space, newline separates houses. The path to the csv file can be
relative or absolute. Taptimise should produce a report
(`pat/to/file_report.html`) containing the optimised tap positions.

#### Advanced

Taptimise can accept several command line flags to tweak the optimisation.

*  `-h`, `--help`, show help message and exit.
*  `-V`, `--version`, show version and exit.
*  `-n NUM`, --num-taps `NUM` number of taps to attempt to place. Defaults to the minimum required to supply enough water to the village.
*  `-m DIST`, `--max-distance DIST`, maximum house-tap separation. Defaults to infinity.
*  `-b SIZE`, `--buffer-size SIZE` size of each houses internal buffer. Defaults to a multiple (5x) of the number of taps.
*  `-s STEPS`, `--steps STEPS`, number of cooling steps per scale per tap.
* `--scales NUM_SCALES`, set the number of length scales in the problem. Defaults to automatic detection.
* `-o OVERLOAD`, `--overload OVERLOAD`, set the overload fraction to enable tap-quantum-tunnelling.
* `--disable-auto`, disables auto rerun if biggest house-tap separation is greater than MAX_DISTANCE.
* `--disable-debug`, disable saving run/debug data.
* `--csv`, writes the optimised tap locations to a csv file as well as the html report.
* `--scribble SCRIBBLE`, lets Taptimise read www.scribblemaps.com native csv output, argument is the house demand.
* `--no-relax`, Disables the final pair wise 'relaxation' stage. Useful for debugging.


Setting a maximum separation with `-m` will trigger automatic reruns each using more taps until a solution is found. This can take a very long time.

Increasing the number of simulation steps with `-s` will improve the result at the expense of longer compute time.

An effective 'auto' mode can be enabled by passing the flags `--steps 10 --scales 1000`. This will cause taptimise to loop through its cooling stage until it detects a stationary state. This is useful if you don't know how many Monte-Carlo steps to use and you don't want to risk overestimating.

Setting the overload fraction with `-o` much less than 1.15 will cause non deterministic results.
