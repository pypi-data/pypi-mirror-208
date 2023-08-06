# Copyright (C) 2016 Antoine Carme <Antoine.Carme@outlook.com>
# All rights reserved.

# This file is part of the Python Automatic Forecasting (PyAF) library and is made available under
# the terms of the 3 Clause BSD license

import os
import sys

import numpy as np
import pandas as pd
import pyaf.Bench.GenericBenchmark as ben
import pyaf.Bench.TS_datasets as tsds


class cMComp_Tester(ben.cGeneric_Tester):

    """
    info : https://en.wikipedia.org/wiki/Makridakis_Competitions

    tester1 = cMComp_Tester(tsds.load_M1_comp());
    tester1.testAllSignals();

    tester2 = cMComp_Tester(tsds.load_M2_comp());
    tester2.testAllSignals();
    """

    def __init__(self, tsspec, bench_name):
        super().__init__(tsspec, bench_name)
        pass
