# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2018, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import logging
import os
from collections import OrderedDict, defaultdict
from os.path import basename

import numpy as np

logging.basicConfig(level=logging.ERROR)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import pandas as pd
from htmresearch.frameworks.pytorch.mnist_sparse_experiment import \
  MNISTSparseExperiment

NOISE_VALUES = ["0.0", "0.05", "0.1", "0.15", "0.2", "0.25", "0.3", "0.35",
                "0.4", "0.45", "0.5"]



def plotNoiseCurve(suite, values, results, plotPath, format):
  fig, ax = plt.subplots()
  fig.suptitle("Noise curve")
  ax.set_xlabel("Noise")
  ax.set_ylabel("Accuracy")
  for exp in results:
    values = suite.get_value(exp, 0, values, "last")
    df = pd.DataFrame.from_dict(values, orient='index')
    ax.plot(df["testerror"], **format[exp])

  plt.legend()
  plt.savefig(plotPath)
  plt.close()



def plotDropoutByTotalCorrect(results, plotPath, format):
  fig, ax = plt.subplots()
  fig.suptitle("Dropout by Total Correct")
  ax.set_xlabel("Dropout")
  ax.set_ylabel("Total Correct")
  for exp in results:
    data = OrderedDict(sorted(results[exp].items(), key=lambda x: x[0]))
    ax.plot(data.keys(), data.values(), **format[exp])

  xticks = data.keys()
  ax.xaxis.set_ticks(np.arange(min(xticks), max(xticks) + 0.1, 0.1))
  plt.legend()
  plt.savefig(plotPath)
  plt.close()



if __name__ == '__main__':

  # Initialize experiment options and parameters
  suite = MNISTSparseExperiment()
  suite.parse_opt()
  suite.parse_cfg()
  path = suite.cfgparser.defaults()['path']

  # Load "dense" experiment results
  dense_path = suite.get_exp("DropoutExperimentDense")[0]
  dense = suite.get_exps(path=dense_path)

  # Load "sparse" experiment results
  sparse_path = suite.get_exp("DropoutExperimentSparse")[0]
  sparse = suite.get_exps(path=sparse_path)

  # Plot Noise curve
  dense_format = {exp: {
    "label": "dense,{}".format(basename(exp)),
    "linestyle": "--"
  } for exp in dense}
  sparse_format = {exp: {
    "label": "sparse,{}".format(basename(exp)),
    "linestyle": "-"
  } for exp in sparse}
  format = dict(sparse_format)
  format.update(dense_format)

  # Filter results to dropouts 0.0 and 0.5 only
  results = [exp for exp in dense + sparse if any(map(lambda v: v in exp,
                                                      ["dropout0.0", "dropout0.50"]))]

  plotPath = os.path.join(path, "DropoutExperiment_testerror.pdf")
  plotNoiseCurve(suite=suite, values=NOISE_VALUES, results=results,
                 format=format, plotPath=plotPath)

  # Plot Dropout by Noise
  results = defaultdict(dict)
  for exp in sparse:
    dropout = suite.get_params(exp)["dropout"]
    totalCorrect = suite.get_value(exp, 0, "totalCorrect", "last")
    results["sparse"][dropout] = totalCorrect

  for exp in dense:
    dropout = suite.get_params(exp)["dropout"]
    totalCorrect = suite.get_value(exp, 0, "totalCorrect", "last")
    results["dense"][dropout] = totalCorrect

  format = {"sparse": {"label": "Sparse", "linestyle": "-"},
            "dense": {"label": "Dense", "linestyle": "--"}}

  plotPath = os.path.join(path, "DropoutExperiment_total_correct.pdf")
  plotDropoutByTotalCorrect(results=results, format=format, plotPath=plotPath)
