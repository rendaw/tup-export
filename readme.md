## What is `tup-export`?

`tup-export` exports a tup project as a simple script.

## Usage

`tup-export` scans the `tup` database, so you must have initialized and configured the tup build before exporting.  `tup-export` runs `tup scan` so the output should always be up-to-date.

For command line usage, run `tup-export -h`.

## Installation

Run `pip install git+https://github.com/Rendaw/tup-export`.

## Current limitations

- Bash output only
- Doesn't handle variable substitutions (Lua builds should be fine)
- Ignores environment variables
- May not handle some edge cases
