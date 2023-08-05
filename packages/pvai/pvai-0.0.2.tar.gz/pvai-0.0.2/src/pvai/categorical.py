import pandas as pd

def cat_clean_num(data=None,column=None,minimum=None,plot=True):
    '''
    indx_unw,dict_cat = cat_clean_num(data=None,column=None,minimum=None,plot=True)
    Uses a pandas dataframe ('data') with a column that contains a categorical parameter.
    All sample categories with a count <= 'minimum' in 'column' are given by indx_unw.
    All sample categories with a count > 'minimum' are sorted by count and given a numerical value, 
        'dict_cat' is the corresponding dictionary
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
        ax = df_sorted.plot(kind='bar',legend=False,figsize=(6,4),title=title_str)
        ax.set_ylabel('Aantal samples per categorie')
        plt.tick_params(
                axis='x',          # changes apply to the x-axis
                which='both',      # both major and minor ticks are affected
                bottom=True,       # ticks along the bottom edge are off
                top=False,         # ticks along the top edge are off
                labelbottom=True)  # labels along the bottom edge are off
        
    return indx_unw,dict_cat
