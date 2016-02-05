# FIWARE MArkdown to PDF release notes

## 0.2.2
### Release date 5/02/2016 

### New features
* Repository transfered to FIWARE organization.
* Added LICENSE file.
* Added CONTRIBUTORS file.



## 0.2.1
### Release date 15/01/2016 

### New features
* Added releases notes
* md2pdf_version env var added to Dockerfile

### Fixed bugs
* Fixed dependencies due to backward incompatibility since pandoc1.16 


----

## 0.2 Release notes

* If no cover metadata are provided, the tool tries to generate it automatically.
* Now is possible to use a readthedocs configuration file or the default one.
* Cover metadata now could be specified using a different configuration file if the -c option is used.
* PDF margins have been reduced.
* Now pandoc filters are used for some operations.
* Now the tool checks the installation requirements before starting to process the input files.
* Enhanced link navigation.
* Detected a bug related to pandoc and SVG images.
* Fixed minor bugs.
