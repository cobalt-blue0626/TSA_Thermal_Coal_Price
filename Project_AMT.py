#!/usr/bin/env python
# coding: utf-8

# In[2]:


import numpy as np
import pandas as pd
from scipy.stats import norm,shapiro
import statsmodels.tsa.stattools as ts_tool
import statsmodels.tsa.arima.model as ts_model
from bokeh.plotting import ColumnDataSource,figure, output_notebook, show,gridplot
from bokeh.layouts import row
import ipywidgets as widgets
from ipywidgets import interact, interact_manual
from flask import Flask
from bokeh.io import output_file, show,save,reset_output

# output_notebook()


# In[247]:


# app = Flask(__name__)
# @app.route('/')

# def index():
#     return "Hello world"

# if __name__ == "__main__":
#     app.run()


# In[3]:


df = pd.read_csv('data.csv')[['date', 'australia',"indonesia"]]
australia = (df.australia).to_numpy()
indonesia = (df.indonesia).to_numpy()
date = pd.date_range(start="2009-11-01",end="2019-10-31",freq='MS').to_numpy()
date[:10]


# In[4]:


def diff(ts_array, lag_ = 1):
    return(ts_array[lag_:] - ts_array[:len(ts_array) - lag_])


# In[5]:


def stationary_test(ts_array):
    # r = {"adfuller": ts_tool.adfuller(ts_array)[1],"kpss": ts_tool.kpss(ts_array)[1]}
    r1 = "H0 of ADF: Unit root exists, Ha: stationary, with p-value %.6f ,"%(ts_tool.adfuller(ts_array)[1])
    r2 = "H0 of KPSS: stationary, Ha:  Unit root exists, with p-value %.6f"%(ts_tool.kpss(ts_array)[1])
    return r1,r2 
# stationary_test(australia)


# In[6]:


# create a new plot (with a title) using figure
def ts_plot(date_, ts_array):
    
    p = figure(x_axis_type="datetime", plot_width = 800, plot_height = 400, title = "TS plot of thermal coal prices" )
    p.xaxis.axis_label = "Time"#'Time'
    p.yaxis.axis_label = "US Dollars per Metric Ton"#'US Dollars per Metric Ton'
    p.line(date_, ts_array)
    return p

# ts_plot(date[1:],  diff(np.log(australia)), 'Time', 'US Dollars per Metric Ton', 'TS plot of thermal coal prices (AUS)')
# ts_plot(date[1:],  diff(np.log(indonesia)), 'Time', 'US Dollars per Metric Ton', 'TS plot of thermal coal prices (IND)')


# In[8]:


def acf_plot(date, ts_array, title = "ACF plot"):
    
    acf, ci = ts_tool.acf(ts_array, alpha = 0.05)
    p = figure( plot_width = 800, plot_height = 400, title = title)
    p.vbar(x = list(range(1,41)), width = 0.5, bottom = 0,
       top = acf[1:], color="firebrick")
    p.line(x = list(range(1,41)), y = 2/(len(ts_array))**0.5)
    p.line(x = list(range(1,41)), y = -2/(len(ts_array))**0.5)
    p.xaxis.axis_label = "Lag"
    p.yaxis.axis_label = "ACF"
    return p



# In[9]:


def pacf_plot(date, ts_array, title = "PACF plot"):
    
    acf, ci = ts_tool.pacf(ts_array, alpha = 0.05)
    p = figure( plot_width = 800, plot_height = 400, title = title)
    p.vbar(x = list(range(1,41)), width = 0.5, bottom = 0,
       top = acf[1:], color="firebrick")
    p.line(x = list(range(1,41)), y = 2/(len(ts_array))**0.5)
    p.line(x = list(range(1,41)), y = -2/(len(ts_array))**0.5)
    p.xaxis.axis_label = "Lag"
    p.yaxis.axis_label = "PACF"
    return p
#     output_notebook()
#     show(p)
# pacf_plot(date, diff(np.log(australia)), 0.05)


# In[15]:


def fitting_ARIMAX_model( ts_array, exogenous_, p, q, lag_):
    mod = ts_model.ARIMA(ts_array, exog = exogenous_, order = (p,lag_,q))
    res = mod.fit()
    print(res.summary())
    return res.resid, res, res.summary()

# exog_ = np.zeros(120)
# exog_[83] = 1
# residuals, mod ,summary= fitting_ARIMA_model(date, np.log(australia), exog_, (0,1,1))


# In[16]:





# In[17]:


def diagnostics(resid_, date_, lag_ ):
    resid_, date_ = resid_[lag_:], date_[lag_:]
    source = ColumnDataSource(data=dict(
    resid_ = resid_,
    qqplot_x = norm.ppf((np.arange(1,len(resid_) + 1) - 0.5)/len(resid_)),
    qqplot_y = np.sort(resid_),
    date_ = date_,
    date_label = [str(d)[:7] for d in date_[np.argsort(resid_)]],
    ind_sort = np.arange(0, len(resid_))[np.argsort(resid_)],
    ind = np.arange(0, len(resid_))
    ))

    
    s1 = figure(x_axis_type="datetime", plot_width = 400, plot_height = 400, title = "TS plot for residuals",
               tooltips = [("index","@ind")])
    s1.line(x = "date_", y = "resid_",source = source)
    s1.xaxis.axis_label = "Date"
    s1.yaxis.axis_label = "Residuals"

    hist, edges = np.histogram(resid_, density=True)
    
    s2 = figure(plot_width = 400, plot_height = 400, title = "Histagram for residuals")
    s2.quad(top = hist, bottom = 0,left=edges[:-1], right=edges[1:],
           fill_color="navy", line_color="white", alpha=0.5)
    s2.xaxis.axis_label = "Residuals"
    s2.yaxis.axis_label = "Frequency"
    
    acf, ci = ts_tool.acf(resid_, alpha = 0.05)
    s3 = figure(plot_width = 400, plot_height = 400, title = "ACF plot of residuals")
    s3.vbar(x = list(range(1,41)), width = 0.5, bottom = 0,
       top = acf[1:], color="firebrick")
    s3.line(x = list(range(1,41)), y = 2/(len(resid_))**0.5)
    s3.line(x = list(range(1,41)), y = -2/(len(resid_))**0.5)
    s3.xaxis.axis_label = "Lag"
    s3.yaxis.axis_label = "ACF"
    
    s4 = figure(plot_width = 400, plot_height = 400, title = "Q-Q plot of residuals",tooltips = [("date", "@date_label"),("index","@ind_sort")])
    s4.circle(x = "qqplot_x", y = "qqplot_y", source = source)
    y_,x_  = np.quantile(resid_, [0.25, 0.75]), norm.ppf([0.25, 0.75])
    slope = (y_[0] - y_[1])/(x_[0] - x_[1])
    intercept = y_[0] - slope*x_[0]
    line_ = norm.ppf((np.arange(1,len(resid_) + 1) - 0.5)/len(resid_))*slope + intercept
    s4.line(x = norm.ppf((np.arange(1,len(resid_) + 1) - 0.5)/len(resid_)), y = line_)
    s4.xaxis.axis_label = "Theoretical Quantile"
    s4.yaxis.axis_label = "Sample Quantile"
    
    p = gridplot([[s1, s2], [s3, s4]])
    # print("Shapiro Test for normality has p-value:",shapiro(resid_).pvalue)
    # output_file("%s.html"%("diagnostics"))
    # show(p)
    # reset_output()
    # output_notebook()
    return p, shapiro(resid_).pvalue
    
# diagnostics(residuals, date, 1)
# interact(diagnostics(residuals, date, 1));

