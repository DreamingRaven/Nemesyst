#!/usr/bin/env python3.6
import time  # realtime

startTime = time.time()

# quick python file to wrangle movieLense data set
import pandas as pd
import os
import sys
import struct  # used to accurately calculate python version bits (32/64)
import numpy as np
from scipy.sparse.linalg import svds
from scipy import linalg

from surprise import SVD
from surprise import Dataset
from surprise.model_selection import cross_validate

# creating prepend variable for logging
prePend = "[ " + os.path.basename(sys.argv[0]) + " ] "
print(prePend, "Purpose: calculating eigenvectors and eigenvalues to reduce size and predict missing")
print(prePend, "python version (bit): ", struct.calcsize("P") * 8)  # check if 32 or 64 bit

# outputting debug info
cwd = os.getcwd()
print(prePend, "Current wd: ", cwd)
print(prePend, "Args: ", str(sys.argv))

# setting data folder path with possible args(a if condition else b)
dataFolderPath = "../../../DataSets/ml-20m/"  # this is the default path
dataFolderPath = dataFolderPath if len(sys.argv) == 1 else sys.argv[1]
print(prePend, "Data path:", dataFolderPath)

# second arg
# setting data file name
dataFileName = "pML.csv"  # default value
dataFileName = sys.argv[2] if len(sys.argv) >= 3 else dataFileName
print(prePend, "Data file name: ", dataFileName)

# import data
#dataSet = pd.read_csv(dataFolderPath + dataFileName)

data = Dataset.load_builtin('ml-1m')
algo = SVD()  # instantiate model
test = cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
print(test)

print(prePend, "Fin.", (time.time() - startTime), " seconds.")


# GET IN SHAPE (b-dum ch)
# U, s, Vh = svds(dataSet, k=(min(dataSet.shape) - 1))  # min dimension
# print(prePend, "(", dataFileName, ").shape = ", dataSet.shape)
# print(prePend, "U.shape = ", U.shape)
# print(prePend, "s.shape = ", s.shape)
# print(prePend, "Vh.shape = ", Vh.shape)

# why is U changing shape ??
# sigma = np.zeros(dataSet.shape)
# for i in range(min(Vh.shape)):
#     print(prePend, i, " shape: min=", min(Vh.shape))
#     sigma[i, i] = s[i]
# a1 = np.dot(U, np.dot(sigma, Vh))
#np.allclose(dataSet, a1)