# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
import numpy as np
import pyaf.ForecastEngine as autof
import pyaf.Bench.TS_datasets as tsds


# %matplotlib inline

# %%

# %%
b1 = tsds.load_airline_passengers()
df = b1.mPastData

# %%
import sys

sys.executable

# %%
lEngine = autof.cForecastEngine()
lEngine.mOptions.mDebugCycles = False
lEngine

# %%
lEngine.train(df, "time", "AirPassengers", 12)

# %%
lEngine.getModelInfo()

# %%
lEngine.standrdPlots()

# %%

# %%
lEngine.mSignalDecomposition.mTrPerfDetails

# %%
dfapp = df.copy()
dfapp.tail()

# %%
dfapp1 = lEngine.forecast(dfapp, 15);

# %%
dfapp1.info()

# %%
dfapp1.tail(15)

# %%
dfapp1.describe()

# %%
