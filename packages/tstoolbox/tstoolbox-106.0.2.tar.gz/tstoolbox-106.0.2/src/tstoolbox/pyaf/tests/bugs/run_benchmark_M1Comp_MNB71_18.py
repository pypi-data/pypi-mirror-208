import warnings

import numpy as np
import pandas as pd
import pyaf.Bench.MComp as mcomp
import pyaf.Bench.TS_datasets as tsds

with warnings.catch_warnings():
    warnings.simplefilter("error")
    tester1 = mcomp.cMComp_Tester(tsds.load_M1_comp(), "M1_COMP")
    tester1.testSignals("MNB71")
