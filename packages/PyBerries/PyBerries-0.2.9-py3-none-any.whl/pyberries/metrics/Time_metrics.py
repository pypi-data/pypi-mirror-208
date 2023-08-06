import pandas as pd

def add_movmean(col, span):
    return lambda df: pd.concat([weighted_movmean(data[col], span, data['nCells']).interpolate(limit=5) for _,data in df.groupby('Group')], axis=0)

def interpolate_col(col='Time_min'):
    return lambda df: pd.concat([data[col].interpolate(limit=5) for _,data in df.groupby('Group')], axis=0)

def weighted_movmean(data, window, weights):
    '''
    Parameters
    ----------
    data : pandas series
        Series to perform the weighted moving average on
    window : int
        Number of points in the moving average window
    weights : pandas series
        Weights to be applied to the moving average (must have same size as data)

    Returns
    -------
    moving_average : pandas series
        Weighted moving average of data
    '''
    return (data
            .mul(weights)
            .rolling(window, min_periods=0, center=True)
            .sum()
            .div(weights
                 .rolling(window, min_periods=0, center=True)
                 .sum()
                 )
            )

def Cell_length(df, timeBin=1, col:str='SpineLength', **kwargs):
    movmean_span = round(10 / timeBin)
    return (df
            .groupby(by=['Group', pd.Grouper(key='TimeDelta', freq=f"{timeBin}min")], sort=False)
            .agg(Time_min=('Time_min','mean'),
                SpineLength=(col,'mean'),
                nCells=('PositionIdx','count')
                )
            .reset_index()
            .assign(Time_min = interpolate_col(col='Time_min'),
                    SpineLength_movmean = add_movmean(col, movmean_span))
            )

def Object_count(df, timeBin=1, col:str='SpotCount', thr=1, **kwargs):
    movmean_span = round(10 / timeBin)
    return (df
            .groupby(by=['Group', pd.Grouper(key='TimeDelta', freq=f"{timeBin}min")], sort=False)
            .agg(Time_min=('Time_min','mean'),
                nCells=('PositionIdx','count'),
                ObjectFrac=(col,lambda x: x.ge(thr).mean()),
                noObjectFrac=(col,lambda x: x.eq(0).mean()),
                ObjectCount=(col, 'sum')
                )
            .reset_index()
            .assign(Time_min = interpolate_col(col='Time_min'),
                       **{f'{k}_movmean': add_movmean(k, movmean_span)
                          for k in ['ObjectFrac', 'noObjectFrac', 'ObjectCount']}
                    )
            )

def Object_classifier(df, timeBin=1, col:str='ClassIdx', **kwargs):
    movmean_span = round(10 / timeBin)
    n_classes = max(df[col])
    return (df
            .groupby(by=['Group', pd.Grouper(key='TimeDelta', freq=f"{timeBin}min")], sort=False)
            [col]
            .value_counts()
            .unstack(fill_value=0)
            .rename(columns = {k: f'ObjectClass_{k}' for k in range(1,n_classes+1)})
            .join(df
                .groupby(by=['Group', pd.Grouper(key='TimeDelta', freq=f"{timeBin}min")], sort=False)
                .agg(Time_min=('Time_min','mean'),
                    nCells=('PositionIdx','count')
                    )
                )
            .reset_index()
            .assign(Time_min = interpolate_col(col='Time_min'),
                    **{f'ObjectClass_{k}': lambda df, col=f'ObjectClass_{k}': df[col]/df['nCells']
                        for k in list(range(1,n_classes+1))},
                    **{f'ObjectClass_{k}_movmean': add_movmean(f'ObjectClass_{k}', movmean_span)
                        for k in list(range(1,n_classes+1))}
                    )
            )

def Object_intensity(df, timeBin=1, col:str='MeanIntensity', **kwargs):
    movmean_span = round(10 / timeBin)
    return (df
            .groupby(by=['Group', pd.Grouper(key='TimeDelta', freq=f"{timeBin}min")], sort=False)
            .agg(Time_min=('Time_min','mean'),
                MeanIntensity=(col,'mean'),
                MaxIntensity=(col, 'max'),
                nCells=('PositionIdx','count')
                )
            .reset_index()
            .assign(Time_min = interpolate_col(col='Time_min'),
                    **{f'{k}_movmean': add_movmean(k, movmean_span)
                        for k in ['MeanIntensity', 'MaxIntensity']}
                    )
            )
    
def Column_quantile(df, timeBin=1, col:str='TrackLength', quantile=0.95, drop_duplicates_by=[], **kwargs):
    movmean_span = round(10 / timeBin)
    return (df
            .drop_duplicates(subset=drop_duplicates_by)
            .groupby(by=['Group', pd.Grouper(key='TimeDelta', freq=f"{timeBin}min")], sort=False)
            .agg(Time_min = ('Time_min', 'mean'),
                 nCells = ('PositionIdx','count'),
                 Column_quantile = (col, lambda x: x.quantile(q=quantile))
                 )
            .reset_index()
            .assign(Time_min = interpolate_col(col='Time_min'),
                    **{f'{k}_movmean': add_movmean(k, movmean_span)
                        for k in ['Column_quantile']}
                    )
            )
    
def Column_aggregation(df, timeBin=1, col:str='TrackLength', agg='mean', drop_duplicates_by=[], **kwargs):
    movmean_span = round(10 / timeBin)
    return (df
            .drop_duplicates(subset=drop_duplicates_by)
            .groupby(by=['Group', pd.Grouper(key='TimeDelta', freq=f"{timeBin}min")], sort=False)
            .agg(Time_min = ('Time_min', 'mean'),
                 nCells = ('PositionIdx','count'),
                 Column_agg = (col, agg)
                 )
            .reset_index()
            .assign(Time_min = interpolate_col(col='Time_min'),
                    **{f'{k}_movmean': add_movmean(k, movmean_span)
                        for k in ['Column_agg']}
                    )
            )
    
def Fluo_intensity(df, exp_time, **kwargs):
    return (df
            .groupby(by=['Group', 'Frame'], sort=False)
            .agg(MeanIntensity = ('RecBIntensity', 'mean'),
                 Background = ('Background', 'mean')
                 )
            .reset_index()
            .assign(Laser_time = lambda df: pd.concat([data.Frame * exp_time for _,data in df.groupby('Group')], axis=0),
                    MeanIntensity = lambda df: pd.concat([(data.MeanIntensity - data.Background) / (data.MeanIntensity.iloc[0] - data.Background.iloc[0]) for _,data in df.groupby('Group')], axis=0)
                    )
            )