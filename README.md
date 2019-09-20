# Taptimise
Second generation tap optimisation algorithm for the eWaterPay project.

### Installation (verbose)
Verify your python and pip distributions are correctly installed. You can test this by running `python -V` and `pip -V`. On some machines with both python 2 & 3 these commands are replaced with `python3 -V` and `pip3 -V` respectively.

#### With Git (recommended)

If [Git](https://git-scm.com/download/win) is installed and accesable from the command line (test with `git --version`). Install Taptimise using pip with: `pip install git+https://github.com/ConorWilliams/taptimise` verify the installation by running: `taptimise -V`.

#### Without Git 

Press on the "Clone or download" button and "Download ZIP". Extract the ZIP archive. Cd into the extracted folder (probably `taptimise-master`) and install Taptimise with `pip install .` (inluding the .) verify the installation by running: `taptimise -V`.

### Basic Use
To run Taptimise with the default setting use:
`taptimise pat/to/file.csv tap_load`. The csv containing the house positions
should be formatted exactly as per the
[example](https://github.com/ConorWilliams/taptimise/tree/master/test) csv's.
I.e comma no space, newline separates houses. The path to the csv file can be
relative or absolute. Taptimise should produce a report
(`pat/to/file_report.html`) containing the optimised tap positions.

### Advanced Use

Taptimise can accept several command line flags to tweak the optimisation.

*  `-h`, `--help`, show help message and exit.
*  `-v`, `--version`, show version and exit.
*  `-n NUM_TAPS`, --num-taps `NUM_TAPS` number of taps to attempt to place. Defaults to the minimum required to supply enough water to the village.
*  `-m MAX_DISTANCE`, `--max-distance MAX_DISTANCE`, maximum house-tap separation. Defaults to infinity.
*  `-b BUFFER_SIZE`, `--buffer-size BUFFER_SIZE` size of each houses internal buffer. Defaults to a multiple (5x) of the number of taps.
*  `-s STEPS`, `--steps STEPS`, number of cooling steps per scale. Defaults to a multiple of the square root of the number of taps.
* `--num-scales NUM_SCALES`, set the number of length scales in the problem. Defaults to automatic detection.
* `--disable-auto`, disables auto rerun if biggest house-tap separation is greater than MAX_DISTANCE.
* `--disable-debug`, disable saving run/debug data.

Setting a maximum separation with `-m` will trigger automatic reruns each using more taps until a solution is found.

Increasing the number of simulation steps with `-s` will improve the result at the expense of longer compute time.
