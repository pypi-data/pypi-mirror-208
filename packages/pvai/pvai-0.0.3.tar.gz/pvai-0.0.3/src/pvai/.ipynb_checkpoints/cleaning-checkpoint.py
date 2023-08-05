import pandas as pd
import matplotlib.pyplot as plt

def cat_clean_dict(data=None,column=None,minimum=None,plot=True):
    '''
    indx_unw,dict_cat = cat_clean_dict(data=None,column=None,minimum=None,plot=True)
    Uses a pandas dataframe ('data') with a column that contains a categorical parameter.
    All sample categories with a count <= 'minimum' in 'column' are given by indx_unw.
    All sample categories with a count > 'minimum' are sorted by count and given a numerical value, 
        'dict_cat' is the corresponding dictionary
    Avoid plotting when the number of categories is very large.
    '''
    a = data.loc[:,column] # column of interest
    
    bins = Counter(a.astype('str')) # count occurances 
    df = pd.DataFrame.from_dict(bins, orient='index') # make into dataframe
    
    df_unw = df.loc[df[0]<=minimum,:] # condition, this outputs a series, unwanted categories
    print('%i unwanted categories' % (df_unw.index.shape))
    indx_unw = a.loc[a.isin(list(df_unw.index))].index # unwanted samples from original data
    print('%i unwanted samples' % (indx_unw.shape))
    
    df_wanted = df.loc[df[0]>minimum,:] # condition, this outputs a series, good categories
    df_sorted = df_wanted.sort_values(by = [0],ascending = False,inplace=False) # sorted by occurence
    title_str = ('%s' % a.name)
    print('%i categories for %s' % (df_sorted.index.shape[0],title_str))
    
    dict_cat = np.array( [df_sorted.index,np.arange(0,len(df_sorted.index))] ).T

    if plot:
        if len(df_sorted)>100:
            print('Warning: More than 100 categories to be plotted!')
        ax = df_sorted.plot(kind='bar',legend=False,figsize=(6,4),title=title_str)
        ax.set_ylabel('Aantal samples per categorie')
        plt.tick_params(
                axis='x',          # changes apply to the x-axis
                which='both',      # both major and minor ticks are affected
                bottom=True,       # ticks along the bottom edge are off
                top=False,         # ticks along the top edge are off
                labelbottom=True)  # labels along the bottom edge are off
        
    return indx_unw,dict_cat


def num_clean_dist(data=None,column=None,binsize=0.01,condition=False,**kwargs):
    ''' 
    unwanted_samples,ax = num_clean_dist(data=None,column=None,binsize=0.01,condition=False,**kwargs)
    Clean the distribution by trimming the ends.
    If condition = True, also provide 'minimum' and 'maximum' values for the data.   
    '''
    a = data.loc[:,column]
    b = pd.to_numeric(a,errors='coerce')
    
    fig,ax=plt.subplots(1,1,figsize=(4,5))
    
    if condition:
        data.loc[:,column]= b
        unwanted_samples = b[(b<kwargs['minimum'])|(b>kwargs['maximum'])].index # these i don't want
        print('condition elimination: %i' % (len(unwanted_samples)))
        d = b[(b>kwargs['minimum'])&(b<kwargs['maximum'])] # condition

        av = d.mean()
        stddev = d.std()
        
        ax.hist(d,bins=np.arange(kwargs['minimum']-binsize/2,kwargs['maximum']+binsize,binsize),rwidth=0.9) 
        ax.set_xlim([kwargs['minimum']-binsize/2,kwargs['maximum']+binsize/2])
        ax.set_ylabel('sample count')
        s = ('avg: %.2f\nstd: %.2f' % (av,stddev))
        plt.text(kwargs['x_text'], 0.8, s, fontsize=12,transform=ax.transAxes)
        return unwanted_samples,ax
        
    else:
        av = b.mean()
        stddev = b.std()
        
        ax.hist(b,bins=np.arange(min(b)-binsize/2,max(b)+binsize,binsize),rwidth=0.9) 
        ax.set_ylabel('sample count')
        s = ('avg: %.2f\nstd: %.2f' % (av,stddev))
        plt.text(kwargs['x_text'], 0.8, s, fontsize=12,transform=ax.transAxes)
        return 'no unwanted samples',ax
