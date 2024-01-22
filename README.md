# rust-brew

A simple script which publishes Rust crates as brew packages.

## Quick Start

Install and authenticate the GitHub cli with ```brew install gh``` and ```gh auth login```

Clone the repo with ```git clone https://github.com/tfsingh/rust-brew && cd rust-brew```

Execute the script with ```python main.py```. You can either fill in the relevant information as it's prompted or edit lines 5-7 in main.py.

## Other

Homebrew dependencies can be added on line 8 as a list of strings.

The script can be run in debug mode by setting "debug" on line 9 to True.