# md2pdf

## About

**md2pdf** is a Python package which allows you to generate a PDF document from a set of Markdown files.


## Installing dependencies

### Ubuntu

1. Install [Python2](https://www.python.org/).

        sudo apt-get install python2

2. Install [Pandoc](http://pandoc.org/).

        sudo apt-get install pandoc

3. Install [XeLaTeX](http://www.xelatex.org/) and some needed [LaTeX](http://www.latex-project.org/) packages

        sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-extra

4. Download and install [PDFtk](https://www.pdflabs.com/tools/pdftk-server/)

### Windows

1. Install [Python2](https://www.python.org/). Make sure PIP is also installed by marking it in the installation wizard.

2. Install [Pandoc](http://pandoc.org/) v1.15.1.1 from [this download link](https://github.com/jgm/pandoc/releases/download/1.15.1.1/pandoc-1.15.1.1-windows.msi)

3. Install [MiKTeX](http://miktex.org/).
    1. Download MiKTeX 2.9.5721 for [32 bits](http://mirrors.ctan.org/systems/win32/miktex/setup/setup-2.9.5721.exe) or [64 bits](http://mirrors.ctan.org/systems/win32/miktex/setup/setup-2.9.5721-x64.exe).
    2. Run the intaller and select the following:
        1. Download MiKTeX.
        2. Complete MiKTeX.
        3. Select a downloading folder.
    3. **Run again** previous installer.
        1. Select "Install MiKTeX"
        2. Select the downloading folder set in last step.
        3. When presented the option "Install missing packages on-the-fly", select "yes".

4. Install [PDFtk](https://www.pdflabs.com/tools/pdftk-server/) - Tested version: [pdftk_free-2.02-win](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/pdftk_free-2.02-win-setup.exe)


### OSX

1. Download and install MacTeX <https://tug.org/mactex/mactex-download.html>

2. Download and install Pandoc 1.15.1 version from <https://github.com/jgm/pandoc/releases/>. You need to download the ```.pkg``` binary.

3. Download and install PDFtk-server for Mac OSX from <https://www.pdflabs.com/tools/pdftk-server/>

4. Install pip <https://pip.pypa.io/en/latest/installing/#install-or-upgrade-pip>

## Installing md2pdf

Run the following commands for cloning this repo and installing the Python package for md2pdf.

        git clone git@github.com:FiwareULPGC/markdown_to_pdf.git
        cd markdown_to_pdf
        sudo python setup.py install

## Usage

**md2pdf** is executed as follows

```
md2pdf -i *input_configuration_file* -o *ouput_pdf_file*
```

where *input_configuration_file* is a YAML configuration file containing:
* A list of paths to the Markdown files that we want to include in the PDF. The paths must be relative to the configuration file itself.
* Data related to cover.

An example of the configuration file is below:

```
files_order:
    - 'first-document.md'
    - 'second-document.md'
    - 'third-document.md'

cover_metadata:
    title: 'Document title'
    Author: 'foo barr'
    Another Data: 'data value'
```

Note that the cover metadata section accepts any key-value pair. The title is the only that it's treated specially, the rest simply are placed using a new line per pair with the key in bold.


For generating a PDF from the documentation example, execute:

```
md2pdf -i markdown-examples/user/markdown-to-pdf.yml -o /var/tmp/orion-user-manual.pdf 
```

For runing unit tests ([unittest](https://docs.python.org/2/library/unittest.html) required), execute (**from within the repository root directory**):

```
python2 markdown_to_pdf/test_markdown_to_pdf.py
```
