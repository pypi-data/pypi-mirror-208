"""
The MIT License (MIT)

Copyright (c) 2021-present UnrealFar & TheGenocides
Copyright (c) 2023-present Sengolda

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
import platform
import sys

import requests

import pytwot


def show_version():
    entries = []

    entries.append("- Python v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}".format(sys.version_info))
    entries.append("- pytwot v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}".format(pytwot.version_info))
    entries.append(f"- requests v{requests.__version__}")
    uname = platform.uname()
    entries.append("- system info: {0.system} {0.release} {0.version}".format(uname))
    print("\n".join(entries))


def core(args):
    if args.version:
        show_version()
    else:
        print(
            "Hi Thank you for using pytwot! You can do can do `python3 -m pytwot --version` for version info!\n\nDocs: https://py-tweet.readthedocs.io/ \nGithub: https://github.com/sengolda/pytwot/"
        )


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-v", "--version", action="store_true", help="shows the library versioninfo")
    argparser.set_defaults(func=core)
    return argparser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
