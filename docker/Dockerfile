FROM ubuntu
MAINTAINER Fiware ULPGC <fiware@ulpgc.es>

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-extra texlive -y
RUN apt-get install unzip git python python-pip wget build-essential -y
RUN apt-get install pdftk -y

RUN wget https://github.com/jgm/pandoc/releases/download/1.15.1/pandoc-1.15.1-1-amd64.deb && dpkg -i pandoc-1.15.1-1-amd64.deb

RUN wget https://github.com/FiwareULPGC/fiware-markdown-to-pdf/archive/develop.zip && unzip develop.zip && cd fiware-markdown-to-pdf-develop && python setup.py install && cd


ENTRYPOINT ["markdown_to_pdf"]

#CMD ["--help"]