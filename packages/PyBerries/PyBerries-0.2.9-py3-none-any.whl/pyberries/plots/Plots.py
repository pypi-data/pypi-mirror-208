import seaborn as sns

# Decorator function to add plot elements (xlim/ylim, axis labels, plot title,...)
def plot(plot_func):
    def make_plot(df, xlim:tuple=(None, None), ylim:tuple=(None, None), xlabel:str='', ylabel:str='', title:str='', drop_duplicates_by=[], **kwargs):
        if drop_duplicates_by:
            df = df.drop_duplicates(subset = drop_duplicates_by)
        kwargs['hue_order'] = df[kwargs.get('hue')].unique() if kwargs.get('hue', None) else None
        g = plot_func(df, **kwargs)
        g.set(xlabel=xlabel, ylabel=ylabel, title=title, xlim=xlim, ylim=ylim)
        if not g.get_legend() == None: g.get_legend().set_title("")
        return g
    return make_plot

@plot
def histplot(df, **kwargs):
    g = sns.histplot(data=df, **kwargs)
    return g
    
@plot
def barplot(df, **kwargs):
    g = sns.barplot(data=df, **kwargs)
    return g

@plot
def lineplot(df, **kwargs):
    g = sns.lineplot(data=df, **kwargs)
    return g

@plot
def stripplot(df, **kwargs):
    g = sns.stripplot(data=df, **kwargs)
    return g

@plot
def pointplot(df, **kwargs):
    g = sns.pointplot(data=df, **kwargs)
    return g

@plot
def scatterplot(df, **kwargs):
    g = sns.scatterplot(data=df, **kwargs)
    return g

@plot
def boxenplot(df, **kwargs):
    g = sns.boxenplot(data=df, **kwargs)
    return g

@plot
def boxplot(df, **kwargs):
    g = sns.boxplot(data=df, **kwargs)
    return g

@plot
def pointplot(df, **kwargs):
    g = sns.pointplot(data=df, **kwargs)
    return g
