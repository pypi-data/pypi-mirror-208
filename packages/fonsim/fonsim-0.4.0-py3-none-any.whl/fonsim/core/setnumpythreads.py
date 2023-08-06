"""
https://gitlab.com/abaeyens/fonsim/-/issues/19

2022, June 04
"""
import os


def setnumpythreads(nb_threads=1):
    os.environ["MKL_NUM_THREADS"] = str(nb_threads)
    os.environ["NUMEXPR_NUM_THREADS"] = str(nb_threads)
    os.environ["OMP_NUM_THREADS"] = str(nb_threads)
