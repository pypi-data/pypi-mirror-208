# -*- coding: utf-8 -*-

from os import listdir
from os.path import join, exists
import json
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
from warnings import warn
from .util import dict_val_to_list, arg_to_list, set_to_several_objects
import pyberries as pyb

class DatasetPool():
    
    def __init__(self,
                 path,
                 dsList,
                 groups=[],
                 metadata={},
                 filters={},
                 preprocessing={}
                 ):
        
        path = arg_to_list(path)
        dsList = arg_to_list(dsList)
        preprocessing = dict_val_to_list(preprocessing)

        self.path = path
        self.dsList = dsList
        self._parents = dict()

        for i, ds in enumerate(dsList):
            ds_path = path[0] if len(path) == 1 else path[i]
            assert exists(ds_path), f'Bacmman folder not found: {ds_path}'
            assert exists(join(ds_path, ds)), f'Dataset {ds} not found.\nMaybe looking for {" or ".join([x for x in listdir(ds_path) if x.startswith(ds[0:6])])}?'
            assert (len(groups) >= len(dsList)) or not groups, 'If groups are provided, one group should be defined per dataset'

            # Load configuration
            cf = join(ds_path, ds, f"{ds}_config.json")
            with open(cf, errors='ignore') as f:
                conf = json.load(f)
                object_class_names = [c["name"] for c in conf["structures"]["list"]]
                object_parents = [c["segmentationParent"] for c in conf["structures"]["list"]]

            # Add Viewfield object if measurement table is available
            if exists(join(ds_path, ds, f"{ds}_{-1}.csv")):
                object_class_names.insert(0, 'Viewfield')
                object_parents.insert(0, [])
                start_table = -1
            else:
                start_table = 0

            # Load data tables
            k = 0
            for j, obj in enumerate(object_class_names, start_table):
                df_in = pd.read_csv(join(ds_path, ds, f"{ds}_{j}.csv"), sep=';', low_memory=False)
                df_in['Dataset'] = ds
                df_in['Group'] = groups[i] if groups else i
                df_in[['Dataset', 'Group']] = df_in[['Dataset', 'Group']].astype('category')
                if obj in preprocessing.keys():
                    if len(preprocessing[obj]) == 1:
                        df_in = df_in.transform(preprocessing[obj][0])
                    elif len(preprocessing[obj]) > 1:
                        assert len(preprocessing[obj]) == len(self.dsList), 'If multiple pre-processings are provided, there should be one per dataset'
                        if preprocessing[obj][i]:
                            df_in = df_in.transform(preprocessing[obj][i])
                df = df_in if obj not in self.__dict__.keys() else pd.concat([self[obj], df_in], axis=0)
                setattr(self, obj, df)
                self._parents[obj] = object_class_names[object_parents[k][0]-start_table] if object_parents[k] else 'Viewfield'
                k+=1
            print(f'Dataset {ds}: loaded objects {object_class_names}')
        self.objects = list(self._parents.keys())
        for obj in self.objects:
            self[obj].reset_index(drop=True, inplace=True)

        self.add_metadata(metadata)
        self.apply_filters(filters)


    def __getitem__(self, name):
        return getattr(self, name)
    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def describe(self, agg, include='all'):
        include = arg_to_list(include)
        for obj in self.objects:
            df = self[obj]
            if include != ['all']:
                df = df.filter(items=include + ['Dataset', 'Group'])
                if not [item for item in list(df.columns) + ['All'] if item in include]:
                    df = pd.DataFrame()
            print(f'{obj}')
            if df.empty:
                print('No data')
            else:
                df1 = (df
                    .groupby('Dataset', sort=False)
                    .agg(nObjects = ('Dataset', 'count'))
                    )
                df2 =(df
                    .loc[:, ~df.columns.isin(['Position','PositionIdx','Indices','Frame','Idx','Time','Group'])]
                    .groupby('Dataset', sort=False)
                    .agg(agg, numeric_only=True)
                    )
                if isinstance(agg, list):
                    df2.columns = df2.columns.map(' ('.join) + ')'
                df3 = df[['Group', 'Dataset']].drop_duplicates().set_index('Dataset')
                df_out = df3.join([df1, df2])
                display(df_out)

    def has_na(self, object_name=None):
        if object_name:
            objects = arg_to_list(object_name)
        else:
            objects = self.objects
        for obj in objects:
            df = self[obj].loc[:, ~self[obj].columns.isin(['Position','PositionIdx','Indices','Frame','Idx','Time','Group','Dataset'])]
            if not df.empty:
                print(f'{obj}')
                display(df.isna().sum())

    def dropna(self, object_name=None, **kwargs):
        if object_name:
            objects = arg_to_list(object_name)
        else:
            objects = self.objects
        for obj in objects:
            if not self[obj].empty:
                self[obj] = self[obj].dropna(**kwargs)

    def fillna(self, object_name=None, col=None, **kwargs):
        if object_name:
            objects = arg_to_list(object_name)
        else:
            objects = self.objects
        for obj in objects:
            if not self[obj].empty:
                if col:
                    self[obj][col] = self[obj][col].fillna(**kwargs)
                else:
                    self[obj] = self[obj].fillna(**kwargs)
    
    def head(self, nlines:int=5):
        for obj in self.objects:
            print(f'{obj}')
            if self[obj].empty:
                print('No data')
            else:
                display(self[obj].head(nlines))
    
    def add_metadata(self, metadata):
        metadata = set_to_several_objects(metadata, self.objects)
        metadata = dict_val_to_list(metadata)
        for obj in metadata.keys():
            if not self[obj].empty:
                df = self[obj]
                for var in metadata[obj]:
                    df[var.replace(' ', '_')] = 0
                    if var == 'DateTime':
                        df['TimeDelta'] = 0
                        df['Time_min'] = 0
                    for i, ds in enumerate(self.dsList):
                        ds_path = self.path[0] if len(self.path) == 1 else self.path[i]
                        for pos in df.loc[df['Dataset'] == ds].Position.unique():
                            metadata_filename = f'{pos}_c0.txt' if exists(join(ds_path, ds, 'SourceImageMetadata', f'{pos}_c0.txt')) else f'{pos}_c0_t0.txt'
                            with open(join(ds_path, ds, 'SourceImageMetadata', metadata_filename)) as f:
                                value = next((line for line in f if var in line), None)
                                # Add metadata value to the current dataset and position
                                df.loc[(df['Position'] == pos) & (df['Dataset'] == ds), var.replace(' ', '_')] = value.split('=')[-1][:-1] # Remove line break (last character)
                        if 'DateTime' in df.columns:
                            df.loc[df['Dataset'] == ds] = (df.loc[df['Dataset'] == ds]
                                                            .assign(DateTime = lambda df: pd.to_datetime(df.DateTime, format='%Y%m%d %H:%M:%S.%f'),
                                                                    TimeDelta = lambda df: df.DateTime - df.DateTime.iloc[0],
                                                                    Time_min = lambda df: df.TimeDelta.dt.total_seconds().div(60)
                                                                    )
                                                            )
                self[obj] = df
    
    def apply_filters(self, filters):
        filters = set_to_several_objects(filters, self.objects)
        filters = dict_val_to_list(filters)
        for obj, filter in filters.items():
            if len(filter) == 1:
                setattr(self, obj, self[obj].query(filter[0]))
            elif len(filter) > 1:
                assert len(filter) == len(self.dsList), 'If multiple filters are provided, there should be one per dataset'
                df = pd.DataFrame()
                i=0
                for _, data in self[obj].groupby('Dataset', sort=False):
                    if filter[i]:
                        df = pd.concat([df, data.query(filter[i])], axis=0)
                    else:
                        df = pd.concat([df, data], axis=0)
                    i+=1
            # Propagate filters to children (if any)
            for child, parent in self._parents.items():
                if parent == obj:
                    self.propagate_filters(parent, child)

    def propagate_filters(self, parent:str, child:str):
        self.get_parent_indices(obj=child)
        self[child] = (self[child]
                            .merge(self[parent][['Dataset', 'PositionIdx', 'Indices']], suffixes=(None, '_tmp'), left_on = ['Dataset', 'PositionIdx', 'ParentIndices'], right_on=['Dataset', 'PositionIdx', 'Indices'])
                            .transform(lambda df: df.loc[:, ~df.columns.str.contains('_tmp')])
                            )

    def rename_object(self, rename:dict):
        for old_name, new_name in rename.items():
            if new_name in self.objects:
                self[new_name] = pd.concat([self[new_name], self[old_name]], axis=0).reset_index(drop=True, inplace=True)
            else:
                self[new_name] = self[old_name]
                self._parents[new_name] = self._parents[old_name]
            for child, parent in self._parents.items():
                if parent == old_name:
                    self._parents[child] = new_name
            delattr(self, old_name)
            del self._parents[old_name]
            self.objects = list(self._parents.keys())

    def get_parent_indices(self, obj:str, indices:str='Indices', newcol:str='ParentIndices'):
        self[obj][newcol] = (self[obj]
                                    [indices]
                                    .str.split('-', expand=True)
                                    .iloc[:,:-1]
                                    .agg('-'.join, axis=1)
                                    )
    
    def get_idx(self, obj:str, idx:int=0, indices:str='Indices', newcol:str='ParentIdx'):
        self[obj][newcol] = (self[obj]
                                    [indices]
                                    .str.split('-', expand=True)
                                    .iloc[:,idx]
                                    .astype('int64')
                                    )
        
    def fuse_columns(self, obj:str, cols:list=[], new:str='new_col'):
        self[obj][new] = self[obj][cols].astype('str').agg('-'.join, axis=1)

    def normalise(self, object_name:str, col:str='', normalise_by:str='', new_col:str=''):
        if new_col in self[object_name].columns:
            self[object_name].drop(columns=new_col, inplace=True)
        if new_col:
            self[object_name] = (self[object_name]
                                            .assign(new_tmp = lambda df: df[col] / df[normalise_by])
                                            .rename(columns={'new_tmp':new_col})
                                            )
        else:
            self[object_name] = (self[object_name]
                                            .assign(new_tmp = lambda df: df[col] / df[normalise_by])
                                            .drop(columns=col)
                                            .rename(columns={'new_tmp':col})
                                            )

    def add_from_parent(self, object_name:str, col:list=[]):
        parent = self._parents[object_name]
        self.get_parent_indices(obj=object_name)
        for c in col:
            self[object_name] = (self[object_name]
                                        .merge(self[parent][['PositionIdx', 'Indices', c]], suffixes=(None, '_tmp'), left_on = ['PositionIdx', 'ParentIndices'], right_on=['PositionIdx', 'Indices'])
                                        .transform(lambda df: df.loc[:, ~df.columns.str.contains('_tmp')])
                                        )

    def add_columns(self, object_name:str, metrics, **kwargs):
        df = self[object_name]
        for m in metrics:
            if m == 'Heatmap':
                df = pyb.metrics.heatmap_metrics(df, **kwargs)
            elif m == 'is_col_larger':
                df = pyb.metrics.is_col_larger(df, **kwargs)
            elif m == 'bin_column':
                df = pyb.metrics.bin_column(df, **kwargs)
            elif m == 'Dapp':
                df = pyb.metrics.tracking_Dapp(df, **kwargs)
            else:
                ValueError(f'Metric "{m}" not found')

    def get_timeseries(self, object_name:str, metric, **kwargs):
        df_in = self[object_name]
        if metric == 'SpineLength':
            df_out = pyb.metrics.Cell_length(df_in, **kwargs)
        elif metric == 'ObjectCount':
            df_out = pyb.metrics.Object_count(df_in, **kwargs)
        elif metric == 'ObjectClass':
            df_out = pyb.metrics.Object_classifier(df_in, **kwargs)
        elif metric == 'Intensity':
            df_out = pyb.metrics.Object_intensity(df_in, **kwargs)
        elif metric == 'Quantile':
            df_out = pyb.metrics.Column_quantile(df_in, **kwargs)
        elif metric == 'Aggregation':
            df_out = pyb.metrics.Column_aggregation(df_in, **kwargs)
        elif metric == 'Fluo_intensity':
            df_out = pyb.metrics.Fluo_intensity(df_in, **kwargs)
        else:
            ValueError(f'Metric "{metric}" not found')
        self[f'{object_name}_timeseries'] = df_out

    def plot_preset(self, preset:str, object_name:str='', drop_duplicates_by=[], return_axes:bool=False, **kwargs):
        hue = kwargs.get('hue','')
        if isinstance(hue, list):
            self.fuse_columns(obj=object_name, cols=hue, new='_'.join(hue))
            kwargs['hue'] = '_'.join(hue)
        if object_name:
            df_in = self[object_name].copy()
            if drop_duplicates_by:
                df_in = df_in.drop_duplicates(subset = drop_duplicates_by)
        _,ax = plt.subplots(dpi=130)
        if preset == 'histogram':
            ax = pyb.plots.plot_histogram(df_in, ax=ax, **kwargs)
        elif preset == 'histogram_fit':
            ax = pyb.plots.plot_histogram_fit(df_in, ax=ax, **kwargs)
        elif preset == 'bar':
            ax = pyb.plots.barplot(df_in, ax=ax, **kwargs)
        elif preset == 'line':
            ax = pyb.plots.lineplot(df_in, ax=ax, **kwargs)
        elif preset == 'line_fit':
            ax = pyb.plots.plot_line_fit(df_in, ax=ax, **kwargs)
        elif preset == 'scatter':
            ax = pyb.plots.scatterplot(df_in, ax=ax, **kwargs)
        elif preset == 'datapoints_and_mean':
            ax = pyb.plots.plot_datapoints_and_mean(df_in, dsList=self.dsList, ax=ax, **kwargs)
        elif preset == 'heatmap':
            ax = pyb.plots.plot_heatmap(df_in, ax=ax, **kwargs)
        elif preset == 'timeseries':
            ax = pyb.plots.plot_timeseries(df_in, ax=ax, **kwargs)
        elif preset == 'boxplot':
            ax = pyb.plots.boxplot(df_in, ax=ax, **kwargs)
        elif preset == 'boxenplot':
            ax = pyb.plots.plot_boxenplot(df_in, ax=ax, **kwargs)
        elif preset == 'spot_tracks':
            lineage = kwargs.pop('lineage','')
            self.fuse_columns(obj=object_name, cols=['Idx','BacteriaLineage'], new='Track')
            if lineage:
                df_in = df_in.copy().query('BacteriaLineage == @lineage')
            ax=pyb.plots.lineplot(df_in, hue='Track', sort=False, ax=ax, **kwargs)
        elif preset == 'rates_summary':
            ax = pyb.plots.plot_rates_summary(ax=ax, **kwargs)
        elif preset == 'grey_lines_and_highlight':
            ax = pyb.plots.plot_grey_lines_and_highlight(df_in, ax=ax, **kwargs)
        else:
            warn('Plot preset not found!')
        if return_axes: return ax