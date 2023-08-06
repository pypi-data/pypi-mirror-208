import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plot_univariate_numeric(df, numcols_name, subplot_cols=3, kind="box"):
    """
    This function takes a pandas dataframe and a list of column names containing
    numeric values and plots univariate distribution of each column. The user can
    choose the kind of plot to be displayed using the 'kind' parameter. The function
    returns a matplotlib figure object.

    Parameters:
    -----------
    df : pandas.DataFrame
        The dataframe containing the data to be plotted.
    numcols_name : list of str
        The list of column names containing numeric values.
    subplot_cols : int (default=3)
        The number of subplots columns to display.
    kind : str (default='box')
        The kind of plot to be displayed. Possible values are 'box', 'hist', and
        'density'.

    Returns:
    --------
    None
    """
    numcols_len = len(numcols_name)
    subplot_rows = 1
    # handle edge case when subplot_cols > numcols_len
    if subplot_cols >= numcols_len:
        subplot_cols = numcols_len
    else:
        subplot_rows = int(np.ceil(numcols_len/subplot_cols))

        
    fig, axes = plt.subplots(subplot_rows,subplot_cols,figsize=(subplot_cols*3,subplot_rows*3))


    # if subplot_rows == 1 or subplot_cols==1 then the axes object will be a 1D array
    # so we need to handle this case differently
    if (subplot_rows == 1) | (subplot_cols == 1):
        for i in range(numcols_len):
            if kind == "box":
                sns.boxplot(x=numcols_name[i],data=df,ax=axes[i])
            elif kind == "hist":
                sns.histplot(x=numcols_name[i],data=df,ax=axes[i])
            elif kind == "density":
                sns.kdeplot(x=numcols_name[i],
                            data=df,
                            ax=axes[i],
                            fill=True, color="blue", alpha=.5, linewidth=1)
            else:
                raise ValueError("kind parameter can only take values 'box', 'hist', or 'density'")
        
        # remove the excess axes
        excess_plots = subplot_rows*subplot_cols - numcols_len
        if excess_plots > 0:
            for i in range(numcols_len,subplot_rows*subplot_cols):
                fig.delaxes(axes[i//subplot_cols,i%subplot_cols])
        plt.tight_layout()
    else: # if subplot_rows > 1 then the axes object will be a 2D array
        for i in range(numcols_len):
            if kind == "box":
                sns.boxplot(x=numcols_name[i],data=df,ax=axes[i//subplot_cols,i%subplot_cols])
            elif kind == "hist":
                sns.histplot(x=numcols_name[i],data=df,ax=axes[i//subplot_cols,i%subplot_cols])
            elif kind == "density":
                sns.kdeplot(x=numcols_name[i],
                            data=df,
                            ax=axes[i//subplot_cols,i%subplot_cols],
                            fill=True, color="blue", alpha=.5, linewidth=1)
            else:
                raise ValueError("kind parameter can only take values 'box', 'hist', or 'density'")
        
        # remove the excess axes
        excess_plots = subplot_rows*subplot_cols - numcols_len
        if excess_plots > 0:
            for i in range(numcols_len,subplot_rows*subplot_cols):
                fig.delaxes(axes[i//subplot_cols,i%subplot_cols])
        plt.tight_layout()
    # add suptitle
    fig.suptitle("Univariate Analysis: Numeric Features",fontsize=20)
    plt.tight_layout()



def plot_univariate_categorical(df, catcols_name, subplot_cols=3, kind="count",figsize=(10,10)):
    """
    This function takes a pandas dataframe and a list of column names containing
    categorical values and plots univariate distribution of each column. The user
    can choose the kind of plot to be displayed using the 'kind' parameter. The
    function returns a matplotlib figure object.

    Parameters:
    -----------
    df : pandas.DataFrame
        The dataframe containing the data to be plotted.
    catcols_name : list of str
        The list of column names containing categorical values.
    subplot_cols : int (default=3)
        The number of subplots columns to display.
    kind : str (default='count')
        The kind of plot to be displayed. Possible values are 'count', and
        'proportion'.
    figsize : tuple (default=(10,10))

    Returns:
    --------
    None
    """
    catcols_len = len(catcols_name)
    subplot_rows = 1
    # handle edge case when subplot_cols > numcols_len
    if subplot_cols >= catcols_len:
        subplot_cols = catcols_len
    else:
        subplot_rows = int(np.ceil(catcols_len / subplot_cols))
    fig, axes = plt.subplots(subplot_rows, 
                             subplot_cols, 
                             figsize=(max(subplot_cols*3,figsize[0]),max(subplot_rows*3,figsize[1])))


    # if subplot_rows == 1 or subplot_cols==1 then the axes object will be a 1D array
    # so we need to handle this case differently
    if (subplot_rows == 1) | (subplot_cols == 1):
        for i in range(catcols_len):
            if kind == "count":
                sns.countplot(y=catcols_name[i], 
                              data=df, 
                              ax=axes[i],
                              order=df[catcols_name[i]].value_counts().index)
            elif kind == "proportion":
                # compute the proportions using value_counts(normalize=True)
                data = df[catcols_name[i]].value_counts(normalize=True).reset_index()

                # plot the piechart using matplotlib pie function
                axes[i].pie(x=data[catcols_name[i]], labels=data["index"],
                            autopct="%.2f%%")
                axes[i].set_title(catcols_name[i])
            else:
                raise ValueError("kind parameter can only take values 'count', or 'proportion'")

        # remove the excess axes
        excess_plots = subplot_rows * subplot_cols - catcols_len
        if excess_plots > 0:
            for i in range(catcols_len, subplot_rows * subplot_cols):
                fig.delaxes(axes[i])
        plt.tight_layout()
    else:  # if subplot_rows > 1 then the axes object will be a 2D array
        for i in range(catcols_len):
            if kind == "count":
                sns.countplot(y=catcols_name[i], 
                              data=df, 
                              ax=axes[i // subplot_cols, i % subplot_cols],
                              order=df[catcols_name[i]].value_counts().index)
            elif kind == "proportion":
                # compute the proportions using value_counts(normalize=True)
                data = df[catcols_name[i]].value_counts(normalize=True).reset_index()

                # plot the piechart using matplotlib pie function
                axes[i // subplot_cols, i % subplot_cols].pie(x=data[catcols_name[i]], labels=data["index"],
                                                              autopct="%.2f%%")
                axes[i // subplot_cols, i % subplot_cols].set_title(catcols_name[i])
            else:
                raise ValueError("kind parameter can only take values 'count', or 'proportion'")
        excess_plots = subplot_rows * subplot_cols - catcols_len
        if excess_plots > 0:
            for i in range(catcols_len, subplot_rows * subplot_cols):
                fig.delaxes(axes[i // subplot_cols, i % subplot_cols])
        plt.tight_layout()
    # add suptitle
    fig.suptitle("Univariate Analysis: Categorical Features", fontsize=20)
    plt.tight_layout()

   