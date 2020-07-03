#!/usr/bin/env python

from __future__ import print_function
import subprocess
import sys
import os




def check_all_requirements():
    is_pandoc_installed()
    is_pdftk_installed()
    is_xelatex_installed()
    #is_false_installed()
    
    pass



def is_pandoc_installed():
    FNULL = open(os.devnull, 'w')
    try:
        subprocess.check_call(["pandoc","--version"],stdout=FNULL, stderr=subprocess.STDOUT)
    except Exception as e:
        print("Aborted: pandoc is not correctly installed.")
        sys.exit(1)
        FNULL.close()

    FNULL.close()
def is_pdftk_installed():
    FNULL = open(os.devnull, 'w')
    try:
        subprocess.check_call(["pdftk","--version"],stdout=FNULL, stderr=subprocess.STDOUT)
    except Exception as e:
        print("Aborted: pdftk is not correctly installed.")
        sys.exit(1)
        FNULL.close()

    FNULL.close()


def is_xelatex_installed():
    FNULL = open(os.devnull, 'w')
    try:
        subprocess.check_call(["xelatex","--version"],stdout=FNULL, stderr=subprocess.STDOUT)
    except Exception as e:
        print("Aborted: xelatex is not correctly installed.")
        sys.exit(1)
        FNULL.close()

    FNULL.close()


def is_false_installed():
    FNULL = open(os.devnull, 'w')
    try:
        subprocess.check_call(["false_program","--version"],stdout=FNULL, stderr=subprocess.STDOUT)
    except Exception as e:
        print("Aborted: false_program is not correctly installed")
        sys.exit(1)
        FNULL.close()

    FNULL.close()