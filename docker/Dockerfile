FROM ubuntu
MAINTAINER Fiware ULPGC <fiware@ulpgc.es>

ENV md2pdf_version 0.2.2

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-extra texlive -y
RUN apt-get install unzip git python python-pip wget build-essential -y
RUN apt-get install pdftk -y

RUN wget https://github.com/jgm/pandoc/releases/download/1.15.1/pandoc-1.15.1-1-amd64.deb && dpkg -i pandoc-1.15.1-1-amd64.deb

RUN wget https://github.com/Fiware/tools.Md2pdf/archive/$md2pdf_version.zip && unzip $md2pdf_version.zip && cd tools.Md2pdf-$md2pdf_version && python setup.py install && cd


ENTRYPOINT ["markdown_to_pdf"]

#CMD ["--help"]