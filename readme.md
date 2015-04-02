## What is `tup-export`?

`tup-export` exports a tup project as a simple script.

**note** This feature already exists in `tup` as `tup generate` - but it has some outstanding issues ([https://github.com/gittup/tup/issues/179]).  This may be an alternative until those are resolved.

## Usage

`tup-export` scans the `tup` database, so you must have initialized and configured the tup build before exporting.  `tup-export` runs `tup scan` so the output should always be up-to-date.

You must run `tup-export` from the project root (the directory containing `.tup`).

The output script is relative to the project root.

For command line usage, run `tup-export -h`.

## Installation

Run `pip install git+https://github.com/Rendaw/tup-export`.

## Current limitations

- Bash output only
- Doesn't handle variable/group substitutions
- Ignores environment variables
- May not handle some other edge cases
