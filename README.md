# sauce

🍝 Sauce is a command line tool for searching files.

# Installation

Install [pipsi](https://github.com/mitsuhiko/pipsi#readme) -- a lightweight, python package manager.

    curl https://raw.githubusercontent.com/mitsuhiko/pipsi/master/get-pipsi.py | python

And simply:

    pipsi install .

# Getting started

To show the commands:

    sauce --help

# Usage

By default sauce will search the current directory, walking the file tree, opening and printing all files:

    sauce

To specify a target directory, path or file:

    sauce <path>

For searching lines in files, specify terms to include (-j) or exclude (-k) from results:

    # Any line with foo
    sauce -j foo  
    # Any line with foo or bar
    sauce -j "foo, bar"
    # Any line with foo or bar, while excluding lines with hello
    sauce -j "foo, bar" -k hello

Specify file names to include (-x) or exclude (-y) with search terms:

    # Any file with log in the file name
    sauce -x log  
    # Any file with log or config in the file name
    sauce -x "log, config"
    # While excluding files with sys in the file name
    sauce -x "log, config" -y app

To limit search results to a maximum of 10 lines per file:

    sauce -l 10

Duplicate lines are hidden by default, to show duplicate results:

    sauce -d

To walk through the file results one-by-one, pressing any key to continue:

    sauce -w

To execute predefined search parameters, specify a formatted yaml file:

    sauce -y foo.yaml

Example yaml file:

    files:
      exclude:
        - txt
      include:
        - log
    lines:
      exclude:
        - hello
        - world
      include:
        - error
        - fatal
        - fail
        - warn
    showDuplicates: True
    lineLimits: 1000
    walkResults: True

# Upgrade

To upgrade, make or git pull changes and:

    pipsi upgrade .

# Uninstalling

    pipsi uninstall sauce
