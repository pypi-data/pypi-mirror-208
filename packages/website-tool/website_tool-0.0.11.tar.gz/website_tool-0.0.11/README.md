# maintain-website-tool

A tool to make it simpler to maintain a website against the increasing entropy on the web.

This tool includes:
- A link checker
- A CLI Interface
- A visualization of the links on a website

## Usage
```
$ python3 -m maintain-website-tool --help
usage: maintain-website-tool [-h] {link} ...

positional arguments:
  {link}
    link      Tools to maintain the links on a website

optional arguments:
  -h, --help  show this help message and exit
```

This tool always outputs to stdout (with one exception at `link check visualize`)
and often takes input from stdin or files. I try to follow UNIX and Linux command
line convention as much as possible and as often as possible.

### `link` Tool
This can be used to:
- Collect a list of all links on your website.
- Collect latency, status and errors for each link on your website.
- Format results as CSV, YAML and JSON
- Take the difference in status, latency and errors between two different checks of a website.
- Visualize the results as a PyVIS Graph with domains as vertices and links as edges.

#### How to check a website
```bash
$ echo "https://example.org" python3 -m maintain-website-tool link --format csv check - > example.org.csv
```

The `link check` command executes a check starting with the websites it receives as a file either from stdin (as in this example) or through some filename. You can even execute checks of multiple sites by providing more than one URI to the check (seperated by newlines).

See `python3 -m maintain-website-tool link check --help` for more information.

#### Usage
```
$ python3 -m maintain-website-tool link --help
usage: maintain-website-tool link [-h] [--format {csv,yaml,yml,json}] [--in-format {csv,yaml,yml,json}]
                                  [--out-format {csv,yaml,yml,json}]
                                  {check,sort,diff,visualize} ...

positional arguments:
  {check,sort,diff,visualize}
    check               Check all the locations in the locations for their reachability, latency and status
    sort                Sort the results from check according to some options
    diff                Take the difference between two check results
    visualize           Visualize the results of a page as a graph stored in a static HTML.

optional arguments:
  -h, --help            show this help message and exit
  --format {csv,yaml,yml,json}, -f {csv,yaml,yml,json}
                        Format to expect for input and output (is overwritten by in-format and out-format
  --in-format {csv,yaml,yml,json}, -in-f {csv,yaml,yml,json}
                        Format to expect from input only
  --out-format {csv,yaml,yml,json}, -out-f {csv,yaml,yml,json}
                        Format to use for output only
```

# Contributing
I want to extend this into a multipurpose tool to help with the maintance of a website.
If you have an idea for other tools to be added, create an issue [here](https://codeberg.org/developers/maintain-website-tool/issues).

## Social Coding
I'm a subscriber to the ideals and principles of [Social Coding](https://coding.social).
