# md2pdf

## About

**md2pdf** is a Python package which allows you to generate a PDF document from a set of Markdown files.


## Markdown guidelines

A list of considerations that must be followed for writing the markdown files is described in the [GUIDELINES](GUIDELINES.md) file.

## Quick Start Guide (with Docker)

This section assumes that you already have installed Docker in your machine. If you don't, you can install it following the instruccions for your operating system in <https://docs.docker.com/engine/installation/>

### Using a Read the Docs or MkDocs configuration file

If you have a *Read the Docs* or *MkDocs* configuration file, you can use it directly with md2pdf.

For example, if you have your documentation under the folder `/Users/myusername/myEnabler` with an structure like:

```
docs/
  Introduction.md
  User-Guide.md
  ....
  images/
src/
mkdocs.yml
...
```

You can run the command 

```
docker run -v=/Users/myusername/myEnabler:/md2pdf fiwareulpgc/markdown-to-pdf -i /md2pdf/mkdocs.yml -o /md2pdf/documentation.pdf
```

And it will generate the documentation in the file `/Users/myusername/myEnabler/documentation.pdf`

#### Executable example
If you copy the directory `markdown-examples/` to `/Users/myusername/markdown-examples` and run:
```
docker run -v=/Users/myusername/markdown-examples:/md2pdf fiwareulpgc/markdown-to-pdf -i /md2pdf/mkdocs_user-cover.yml -o /md2pdf/documentation.pdf
```
### Using a custom configuration file

If you **don't use** a Read the Docs or MkDocs configuration file, you should provide a configuration file specifying the files order and the cover metadata.

For example, if you have a directory like:

```
docs/
  Introduction.md
  User-Guide.md
  ....
  images/
src/
md2pdf.yml
...
```

Where `md2pdf.yml` is like:

```
files_order:
    - 'docs/Introduction.md'
    - 'docs/User-guide.md'
    ...
cover_metadata:
    title: 'Document title'
    Author: 'foo barr'
    Another Data: 'data value'
    
```

**Note:** Path to the documentation file should be relative.


You can run the command with Docker using:

```
docker run -v=/Users/myusername/myEnabler:/md2pdf fiwareulpgc/markdown-to-pdf -i /md2pdf/md2pdf.yml -o /md2pdf/documentation.pdf
```

#### Executable example

If you copy the directory `markdown-examples/usercover/` to `/Users/myusername/usercover` and run:

```
docker run -v=/Users/myusername/usercover:/md2pdf fiwareulpgc/markdown-to-pdf -i /md2pdf/md2pdf.yml -o /md2pdf/documentation.pdf
```

The file documentation.pdf should have been generated in /Users/myusername/usercover

## Detailed instructions 
### Installing dependencies (without Docker)

**Important: When following next instructions, make sure that Pandoc v1.15.1 is installed.** Using a greater version may introduce incompatibilities with md2pdf (ie. an anomalous behaviour have been detected in Pandoc v1.15.2 when converting tables).

#### Ubuntu

1. Install [Python 2.7](https://www.python.org/) from repository.

        sudo apt-get install python2.7

2. Install PIP (Python packages manager) from repository.

        sudo apt-get install python-pip

3. Download and install [Pandoc v1.15.1](https://github.com/jgm/pandoc/releases/1.15.1).

4. Install a full version of [LaTeX](http://www.latex-project.org/) from repository.

        sudo apt-get install texlive-full

5. Download and install [PDFtk](https://www.pdflabs.com/tools/pdftk-server/)

#### Windows

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


#### OSX

1. Download and install MacTeX <https://tug.org/mactex/mactex-download.html>

2. Download and install Pandoc 1.15.1 version from <https://github.com/jgm/pandoc/releases/>. You need to download the ```.pkg``` binary.

3. Download and install PDFtk-server for Mac OSX from <https://www.pdflabs.com/tools/pdftk-server/>

4. Install pip <https://pip.pypa.io/en/latest/installing/#install-or-upgrade-pip>

### Installing md2pdf

Run the following commands for cloning this repo and installing the Python package for md2pdf.

        git clone git@github.com:FiwareULPGC/markdown_to_pdf.git
        cd markdown_to_pdf
        sudo python setup.py install

### Usage

**md2pdf** is executed as follows

```
md2pdf -i <input_configuration_file> -o <ouput_pdf_file>
```

where *\<input_configuration_file\>* could be a **Read the Docs or MkDocs** configuration file.



If you don't use a **Read the Docs or MkDocs** configuration file, you should provided a YAML configuration file containing:
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


**Cover metadata notes:**
* The cover metadata section accepts any key-value pair. The title is the only that it's treated specially, the rest simply are placed using a new line per pair with the key in bold.
* The cover metadata could be specified using a different configuration file if **-c** option is passed ```md2pdf -i conf-file.yml -c cover_metatada.yml -o output.pdf```.

For generating a PDF from the documentation example, execute:

```
md2pdf -i markdown-examples/user-cover/markdown-to-pdf.yml -o /var/tmp/orion-user-manual.pdf 
```

For runing unit tests ([unittest](https://docs.python.org/2/library/unittest.html) required), execute (**from within the repository root directory**):

```
python2 markdown_to_pdf/test_markdown_to_pdf.py
```



### Usage with Docker


The tool is published in the Docker Hub repository as fiwareulpgc/markdown-to-pdf. You can also build it from the dockerfile provided inside the docker folder. 

 To build the Docker image with the Dockerfile simply use the command `docker build -t <image_name> .` inside the docker folder. Don't forget the final dot.

Once the image is created, you can execute it with:

```
docker run --volume=<host_machine_path>:<docker_container_path> <image_name> -o <docker_container_output_path> -i <docker_container_conf_path>
```

If you are using the Docker Hub container simply replace **<image_name>** by **fiwareulpgc/markdown-to-pdf**:

```
docker run --volume=<host_machine_path>:<docker_container_path> fiwareulpgc/markdown-to-pdf -o <docker_container_output_path> -i <docker_container_conf_path>
```

Where:
 * **<host_machine_path>** is the folder where the documentation is hosted in your machine.
 * **<docker_container_path>** is the folder where the <host_machine_path> is mounted in the Docker container.
 * **<docker_container_output_path>** is the path to the output file related to the Docker container.
 * **<docker_container_conf_path>** is where the configuration is located inside the Docker container.
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

If we are using the Docker Hub Container the command should be:

```
docker run --volume=/User/username/ExampleEnabler/:/m2pdf fiwareulpgc/markdown-to-pdf -o /m2pdf/documentation.pdf -i /m2pdf/docs/m2pdf.yml
```

 
**IMPORTANT NOTE:** All documentation must be located under the <host_machine_path> and all references between its elements (a link to another document, an image..) should be relative.

