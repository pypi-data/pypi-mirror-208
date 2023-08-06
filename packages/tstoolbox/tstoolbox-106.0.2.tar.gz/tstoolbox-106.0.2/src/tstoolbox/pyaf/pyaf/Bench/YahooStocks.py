# Copyright (C) 2016 Antoine Carme <Antoine.Carme@outlook.com>
# All rights reserved.

# This file is part of the Python Automatic Forecasting (PyAF) library and is made available under
# the terms of the 3 Clause BSD license

import os
import sys
import traceback

import numpy as np
import pandas as pd
import pyaf.Bench.GenericBenchmark as ben


class cYahoo_Tester(ben.cGeneric_Tester):

    """ """

    def __init__(self, tsspec, bench_name):
        super().__init__(tsspec, bench_name)
        pass
