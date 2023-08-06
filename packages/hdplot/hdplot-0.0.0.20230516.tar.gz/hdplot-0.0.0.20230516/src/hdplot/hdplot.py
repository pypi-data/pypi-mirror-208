#%%

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# import plotly.graph_objects as go
# import plotly.express as px
# import seaborn as sns
# import rfit

#%%
# Create class hdplot to handle plots with new higher dimensions
# Started 2023 Summer
#
class hdplot:
  """
  Create new dimensions in HD plots
  """
  def __init__(self) -> None:
    self.__subplotShape = (1,) # default 1x1
    self.__subplots = np.zeros(1).reshape(1,1) # store the arrays of subplot figure objects
    return
  
  def scatterplot(self, x, y, color, hdd):
    """
    Create scatterplot with x, y, color, and higher-dim data
    Args:
        x (numeric list or pd.series or np.ndarray): x values
        y (numeric list or pd.series or np.ndarray): y values
        color (numeric or discrete list or pd.series or np.ndarray): color values (numeric or discrete)
        hdd (numeric list or pd.series or np.ndarray): extra dimension data values
    """
    # check x values
    # check y values
    # check color values
    # check hdd values
    xs = self.__setXs(x)
    ys = self.__setYs(y)
    colors = self.__setColors(color)
    hdds = self.__setHdds(hdd)
    # choose modules (plt, sns, or plotly)
    # create plots...
    return
  
  def __setXs(self, x):
    """
    check x values, and set into standard format
    Args:
        x (numeric list or pd.series or np.ndarray): x data
    return : np.ndarray
    """
    arr = x.copy()
    # check and set arr
    return arr

  def __setYs(self, y): # probably can be combined with x as a single function
    """
    check y values, and set into standard format
    Args:
        y (numeric list or pd.series or np.ndarray): y data
    return : np.ndarray
    """
    arr = y.copy()
    # check and set arr
    return arr

  def __setColors(self, color):
    """
    check color values, and set into standard format
    Args:
        color (numeric or discrete list or pd.series or np.ndarray): color data
    return : np.ndarray
    """
    arr = color.copy()
    # check and set arr
    return arr

  def __setHdds(self, hdd):
    """
    check higher-dim data values, and set into standard format
    Args:
        hdd (numeric list or pd.series or np.ndarray): color data
    return : np.ndarray
    """
    arr = hdd.copy()
    # check and set arr
    return arr



#%%
