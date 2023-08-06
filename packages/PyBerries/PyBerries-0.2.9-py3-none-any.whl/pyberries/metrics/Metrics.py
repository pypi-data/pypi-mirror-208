import numpy as np
import pandas as pd

def heatmap_metrics(spot_df, **kwargs):
    return (spot_df
                .assign(normXpos = lambda df: df.SpineCurvilinearCoord / df.SpineLength - 0.5, # Normalise to cell length & centre
                        normYpos = lambda df: df.SpineRadialCoord / df.SpineRadius, # Normalise to cell radius
                        x_fork = lambda df: df.SpineCurvilinearCoord - df.SpineLength/2, # Centre without normalising
                        y_fork = lambda df: df.SpineLength
                        )
            )
    
def is_col_larger(df, col='', thr=0, **kwargs):
    return (df
            .assign(Comparison = lambda df: df[col] > thr)
            )
    
def bin_column(df, col='', binsize=1, **kwargs):
    bins =  np.arange(df[col].min(), df[col].max()+2*binsize, binsize)
    df[f'{col}_bin'] = pd.cut(df[col], bins, include_lowest=True, right=False).transform(lambda x: x.mid)
    return df

def tracking_Dapp(df, trim:int=4, exp_time:float=0.012, **kwargs):
    return (df
            .dropna()
            .loc[df.t0_IntervalCount_1 > trim] # Remove tracks of less than 4 frames
            .assign(Dapp=(lambda df: df.t4_MSD_1/(trim*exp_time)))
            )