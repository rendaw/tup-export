## What is `tup-export`?

`tup-export` exports a tup project as a simple script.

**note** This feature already exists in `tup` as `tup generate` - but it has some outstanding issues ([https://github.com/gittup/tup/issues/179]).  This may be an alternative until those are resolved.

## Usage

`tup-export` scans the `tup` database, so you must have initialized and configured the tup build before exporting.  You may wish to do a build immediately before exporting to ensure the database is correct.

You must run `tup-export` from the project root (the directory containing `.tup`). The output script is relative to the project root.

For command line details, run `tup-export -h`.

**warning** If you run the generated build script in your working directory it will break tup's build state and further invocations may produce incorrect output.

## Installation

Run `pip install git+https://github.com/Rendaw/tup-export`.

## Current limitations

- Bash output only
- Doesn't handle variable substitutions
- Ignores environment variables
- May not handle some other edge cases
