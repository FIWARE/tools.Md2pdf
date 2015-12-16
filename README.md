# md2pdf

## About

**md2pdf** is a Python package which allows you to generate a PDF document from a set of Markdown files.


## Installing dependencies

**Important: When following next instructions, make sure that Pandoc v1.15.1 is installed.** Using a greater version may introduce incompatibilities with md2pdf (ie. an anomalous behaviour have been detected in Pandoc v1.15.2 when converting tables).

### Ubuntu

1. Install [Python 2.7](https://www.python.org/) from repository.

        sudo apt-get install python2.7

2. Install PIP (Python packages manager) from repository.

        sudo apt-get install python-pip

3. Download and install [Pandoc v1.15.1](https://github.com/jgm/pandoc/releases/1.15.1).

4. Install a full version of [LaTeX](http://www.latex-project.org/) from repository.

        sudo apt-get install texlive-full

5. Download and install [PDFtk](https://www.pdflabs.com/tools/pdftk-server/)

### Windows

1. Install [Python2](https://www.python.org/). Make sure PIP is also installed by marking it in the installation wizard.

2. Install [Pandoc v1.15.1](https://github.com/jgm/pandoc/releases/1.15.1).

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
md2pdf -i markdown-examples/user-cover/markdown-to-pdf.yml -o /var/tmp/orion-user-manual.pdf 
```

For runing unit tests ([unittest](https://docs.python.org/2/library/unittest.html) required), execute (**from within the repository root directory**):

```
python2 markdown_to_pdf/test_markdown_to_pdf.py
```

### Special usage

* It also possible to use a readthedocs configuration instead of the previously described configuration file. 
* Cover metadata could be specified using a different configuration if **-c** option is passed.



## Using the provided Dockerfile

A dockerfile with the configuration needed for use the tool is provided inside the docker folder.

To build the Docker image simply use the command `docker build -t <image_name> .` from docker folder. Don't forget the final dot.

Once the image is created, you can execute it with:

```
docker run --volume=<host_machine_path>:<docker_machine_path> <image_name> -o <docker_machine_output_path> -i <docker_machine_conf_path>
```

Where:
 * **<host_machine_path>** is the folder where the documentation is hosted in your machine.
 * **<docker_machine_path>** is the folder where the <host_machine_path> is mounted in the Docker machine.
 * **<docker_machine_output_path>** is the path to the output file related to the Docker machine.
 * **<docker_machine_conf_path>** is where the configuration is located inside the Docker machine.
 * **<image_name>** is the image name used when the image was created.
 
**Example**:

If we have the folder `/User/username/ExampleEnabler` with an structure like:

```
  -docs/
    - m2pdf.yml
    - README.md
    - Chapter1.md
    - Chapter2.md
  
  -src/
    ...
```

If we want to save the output to ```/User/username/ExampleEnabler/documentation.pdf```  and supposing that we have created the Docker machine with ```docker build -t m2pdf-docker .```

We should generate the documentation with the command:

```
docker run --volume=/User/username/ExampleEnabler/:/m2pdf m2pdf-docker -o /m2pdf/documentation.pdf -i /m2pdf/docs/m2pdf.yml
```

**IMPORTANT NOTE:** All documentation must be located under the <host_machine_path> and alll references between its elements (a link to another document, an image..) should be relatives.


## Markdown guidelines

A list of considerations that must be followed for writing the markdown files is described in the [GUIDELINES](GUIDELINES.md) file.
