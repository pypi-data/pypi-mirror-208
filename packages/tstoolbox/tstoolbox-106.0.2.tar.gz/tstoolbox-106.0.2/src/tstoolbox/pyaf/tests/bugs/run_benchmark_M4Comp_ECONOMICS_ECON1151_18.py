import warnings

import numpy as np
import pandas as pd
import pyaf.Bench.MComp as mcomp
import pyaf.Bench.TS_datasets as tsds

lType = "ECONOMICS"

with warnings.catch_warnings():
    warnings.simplefilter("error")
    tester = mcomp.cMComp_Tester(tsds.load_M4_comp(lType), "M4_COMP_" + lType)
    tester.testSignals("ECON1151")
    # tester7.testAllSignals()
    # tester.run_multiprocessed();
