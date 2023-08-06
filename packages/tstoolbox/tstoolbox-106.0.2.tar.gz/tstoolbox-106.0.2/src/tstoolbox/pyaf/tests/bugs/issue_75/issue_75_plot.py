import numpy as np
import pandas as pd
import pyaf.Bench.TS_datasets as tsds
import pyaf.ForecastEngine as autof

b1 = tsds.load_ozone()
df = b1.mPastData

# df.tail(10)
# df[:-10].tail()
# df[:-10:-1]
# df.describe()


lEngine = autof.cForecastEngine()
lEngine

H = b1.mHorizon
# lEngine.mOptions.enable_slow_mode();
# lEngine.mOptions.mDebugPerformance = True;
lEngine.train(df, b1.mTimeVar, b1.mSignalVar, H)
lEngine.getModelInfo()
print(lEngine.mSignalDecomposition.mTrPerfDetails.head())

lEngine.mSignalDecomposition.mBestModel.mTimeInfo.mResolution

try:
    lEngine.standrdPlots("outputs/my_ozone_issue_75")
    assert 0
except:
    print("OK")

lEngine.standardPlots("outputs/my_ozone_issue_75")
