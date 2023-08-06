# %%
# Default libs
import pandas as pd
from matplotlib import pyplot as plt # This is not needed for now, at a later phase we might need it to create Artifacts of the model and plot the performance metrics/clusters
import numpy as np
import time # Needed to measure the time it takes to each model to detect anomalies.
import platform # to check user's version of Python
#from codecarbon import EmissionsTracker
#%%
# Detrend & deseason
from statsmodels.tsa.seasonal import seasonal_decompose # To deseason
from scipy import signal # Needed for detrending
from statsmodels.tsa.stattools import adfuller # For deseason
#from statsmodels.formula.api import ols
#%%
# ML models
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors # Needed to suggest the best parameters for DBSCAN
from kneed import KneeLocator # Needed to suggest the best parameters for DBSCAN
from sklearn.svm import OneClassSVM # OCSVM
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor # LOF
from ThymeBoost import ThymeBoost as tb # Careful with the newer versions of NumPy, may cause issues
import optuna # for OCSVM/LOF parameters
from orion import * # for tadgan

from sklearn import metrics # For calculation of the performance metrics of each model. In case we got labels.
from scipy.fft import rfft, rfftfreq # Fast Fourier transformation. Needed to find the best seasonality interval for ThymBoost
# %%
# Checking if the hook between Teams and DevOps is working.
import sys
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
sys.path.append('C:/Users/A374410/AppData/Local/conda/conda/pkgs')
sys.path.append('C:/Users/A374410/.conda/pkgs')
sys.path.append('C:/Python/Anaconda3/pkgs')
sys.path.append('C:/python/anaconda3/envs/anomaly_detection/lib/site-packages')
from orion import *
# %%
