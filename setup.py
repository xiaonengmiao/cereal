#!/usr/bin/env python

__copyright__ = "Copyright (C) 2019 Techcat_ Haohan Li"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from setuptools import setup, find_packages


def main():
    version_dict = {}
    init_filename = "cereal/version.py"
    exec(compile(open(init_filename, "r").read(), init_filename, "exec"), version_dict)

    setup(name='cereal',
          version=version_dict["VERSION_TEXT"],
          description="A python lite explorer for crypto even analysis and learn",
          long_description=open("README.md", "rt").read(),
          url='',
          author='techcat_ Haohan Li',
          author_email='haohan@v.systems',
          license='MIT',
          packages=find_packages(),
          scripts=['cereal/bin/cereal'],
          python_requires=">=3.0",
          zip_safe=False,
          install_requires=[
              "sphinx",
              "docopt",
              "python-telegram-bot",
          ],
          )


if __name__ == "__main__":
    main()
