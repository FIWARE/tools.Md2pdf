# markdown_to_pdf

## About

**markdown_to_pdf** is a Python package which allows you to generate a PDF document from a set of Markdown files.


## Installing (Ubuntu)

1. Install [Python2](https://www.python.org/).

        sudo apt-get install python2

2. Install [Pandoc](http://pandoc.org/).

        sudo apt-get install pandoc

3. Install [XeLaTeX](http://www.xelatex.org/) and some needed [LaTeX](http://www.latex-project.org/) packages

        sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-extra

4. Run the following commands for cloning this repo and installing the Python package.

        git clone git@github.com:FiwareULPGC/markdown_to_pdf.git
        cd markdown_to_pdf
        sudo python setup.py install

## Usage

**markdown_to_pdf** is executed as follows

```
markdown_to_pdf *ouput_pdf_file* *input_configuration_file*
```

where *input_configuration_file* is a YAML configuration file containing a list of paths to the Markdown files that we want to include in the PDF. The paths must be relative to the configuration file itself.

For generating a PDF from the documentation example, execute:

```
markdown_to_pdf /var/tmp/orion-user-manual.pdf markdown-examples/user/markdown-to-pdf.yml
```

For runing unit tests ([unittest](https://docs.python.org/2/library/unittest.html) required), execute (**from within the repository root directory**):

```
python2 markdown_to_pdf/test_markdown_to_pdf.py
```
