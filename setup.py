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
      version='0.1',
      description='Python module for generating a PDF document from a set of Markdown files',
      url='https://github.com/FiwareULPGC/fiware-markdown-to-pdf',
      author='FIWARE ULPGC',
      author_email='fiware@ulpgc.es',
      license='',
      packages=setuptools.find_packages(),
      include_package_data=True,
      install_requires=[
        'pyyaml>=3.11'
      ],
      entry_points={
        'console_scripts': [
          'markdown_to_pdf = markdown_to_pdf.markdown_to_pdf:main',
        ],
      },
      classifiers=[ 
        'Development Status :: 3 - Alpha',
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

