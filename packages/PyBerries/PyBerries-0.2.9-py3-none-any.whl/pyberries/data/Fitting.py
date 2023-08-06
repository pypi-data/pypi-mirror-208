import numpy as np
import pandas as pd
import inspect
from warnings import warn
from scipy.optimize import curve_fit
from .util import arg_to_list

def get_model(model_type=''):
    if model_type == 'monoexp_decay':
        def model(x, a, b):
            return a*np.exp(-b*x, dtype='float64')
    elif model_type == 'biexp_decay':
        def model(x, a, b, c, d):
            return a*np.exp(-b*x, dtype='float64') + c*np.exp(-d*x, dtype='float64')
    elif model_type == 'monoexp_decay_offset':
        def model(x, a, b, c):
            return a*np.exp(-b*x) + c
    return model

def make_fit(df_in, x:str, y:str, model, groupby:str='Group', p0=None):
    fit_results = dict()
    for name, data in df_in.groupby(groupby, sort=False):
        groupName = '-'.join(map(str, name)) if isinstance(name, tuple) else str(name)
        try:
            popt,_ = curve_fit(model, data[x], data[y], p0=p0)
            fit_results[groupName] = popt
        except:
            print(f'Fit for dataset {name} failed')
    return fit_results

def get_rates(fit_results, model, model_type, dt=1):
    dt = arg_to_list(dt)
    if model_type == 'monoexp_decay':
        assert len(inspect.getfullargspec(model).args) == 3, 'Model does not match with model type'
        rates = pd.DataFrame(columns=['Group', 'Rate'])
        for j, grp in enumerate(fit_results.keys()):
            popt = fit_results[grp]
            dt_grp = dt[j] if len(dt) > 1 else dt[0]
            rates.loc[j] = {'Group':grp, 'Rate':popt[1]/dt_grp}
        rates = rates.astype({'Group':'category', 'Rate':'float64'})
    elif model_type == 'biexp_decay':
        assert len(inspect.getfullargspec(model).args) == 5, 'Model does not match with model type'
        rates = pd.DataFrame(columns=['Group', 'Rate type', 'Rate', 'Population'])
        i=0
        for j, grp in enumerate(fit_results.keys()):
            popt = fit_results[grp]
            dt_grp = dt[j] if len(dt) > 1 else dt[0]
            rates.loc[i] = {'Group':grp, 'Rate type':'Fast', 'Rate':popt[1]/dt_grp, 'Population':popt[0]/(popt[0]+popt[2])}
            i+=1
            rates.loc[i] = {'Group':grp, 'Rate type':'Slow', 'Rate':popt[3]/dt_grp, 'Population':popt[2]/(popt[0]+popt[2])}
            i+=1
        rates = rates.astype({'Group':'category', 'Rate type':'category', 'Rate':'float64', 'Population':'float64'})
    elif model_type == 'monoexp_decay_offset':
        assert len(inspect.getfullargspec(model).args) == 4, 'Model does not match with model type'
        rates = pd.DataFrame(columns=['Group', 'Amplitude', 'Rate', 'Offset'])
        for j, grp in enumerate(fit_results.keys()):
            popt = fit_results[grp]
            dt_grp = dt[j] if len(dt) > 1 else dt[0]
            rates.loc[j] = {'Group':grp, 'Amplitude':popt[0], 'Rate':popt[1]/dt_grp, 'Offset':popt[2]}
        rates = rates.astype({'Group':'category', 'Amplitude':'float64', 'Rate':'float64', 'Offset':'float64'})
    else:
        warn(f'Model type "{model_type}" not found')
    return rates