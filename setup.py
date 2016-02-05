from setuptools import setup
import setuptools
import os
from os import mkdir, umask
from shutil import rmtree
import errno


def get_packages(package):
    """Return root package and all sub-packages."""
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


setup(name='markdown_to_pdf',
      version='0.2.2',
      description='Python module for generating a PDF document from a set of Markdown files',
      url='https://github.com/Fiware/tools.Md2pdf',
      author='FIWARE ULPGC',
      author_email='fiware@ulpgc.es',
      license='MIT',
      packages=setuptools.find_packages(),
      include_package_data=True,
      install_requires=[
        'pyyaml>=3.11',
        'markdown>=2.6.2',
        'pypandoc>=0.9.9',
        'pandocfilters<=1.2.4'
      ],
      entry_points={
        'console_scripts': [
          'markdown_to_pdf = markdown_to_pdf.markdown_to_pdf:main',
          'md2pdf = markdown_to_pdf.markdown_to_pdf:main',
          'md2pdf_pandoc_filter = markdown_to_pdf.pandoc_filters:main',
          'md2pdf_pandoc_paragraph_filter = markdown_to_pdf.paragraph_filters:main'
        ],
      },
      classifiers=[ 
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Documentation',
        'Topic :: Text Processing',
      ],
      zip_safe=False)

