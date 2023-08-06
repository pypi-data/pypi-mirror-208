import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# write a function that takes the following as input:
# - a pandas dataframe
# - a list of column names containing numeric values
# - kind of plot to be displayed (pairplot or heatmap). default is pairplot

# it should plot a bivariate distribution of each column vs. each other column
# using the plot type specified in the kind parameter
# diag_kind and corner parameters to be ignored if kind is heatmap

def plot_bivariate_numeric(data,
                           numcol_names,
                           kind='pairplot',
                           diag_kind='kde',
                           corner=True):
    """
    This function takes a pandas dataframe and a list of column names containing the names of
numeric columns and plots bivariate distribution of each column vs. each other column. The
user can choose the kind of plot to be displayed using the 'kind' parameter. The function
does not return anything.

Parameters:
-----------
data : pandas.DataFrame
    The dataframe containing the data to be plotted.
numcol_names : list of str
    The list of column names containing numeric values.
kind : str (default='pairplot')
    The kind of plot to be displayed. Possible values are 'pairplot', 'heatmap'. Default is
    'pairplot'.
diag_kind : str (default=None)
    The kind of plot for the diagonal subplots. Possible values are 'hist', 'kde'. Default is
    "kde". This parameter is ignored if kind is 'heatmap'.
corner : bool (default=True)
    If True, the corner subplots are not shown. This parameter is ignored if kind is 'heatmap'.
figsize : tuple of int (default=(15,15))
    The size of the figure to be displayed.

    """
    
    if kind == 'pairplot':
        # plot the pairplot with size the figsize parameter
        
        sns.pairplot(data[numcol_names],
                        diag_kind=diag_kind,
                        corner=corner)
        
        # add a title to the figure containing the plot
        plt.suptitle("Bivariate Analysis of numeric features", fontsize='xx-large')
    elif kind == 'heatmap':
        corel = data[numcol_names].corr().round(2)
        sns.heatmap(corel,
                    annot=True,
                    cmap='plasma',
                    vmin=-1,
                    vmax=1,
                    linewidths=1,
                    linecolor='white',
                    mask=np.triu(corel, 1))
        # add a title to the figure
        plt.title("Bivariate Analysis of numeric features-Correlation Heatmap", fontsize='xx-large')
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
    else:
        print("Invalid kind parameter value for plot type. Allowed values are 'pairplot', 'heatmap'")



# write a function that takes the following as input:
# - a pandas dataframe
# - a list of column names containing categorical values


# it should plot a 100% stacked bar chart of each column vs. each other column
# the output should be a square grid of subplots
# the number of rows and columns in the grid of subplots should be equal to the number of categorical columns
# in the main diagonal, subplots of which will be the 100% stacked bar charts of each column vs. itself should not be displayed
# instead in the main diagonal subplots, display countplot of categorical featur


def plot_bivariate_categorical(df_name,catcol_names,figsize=(10,10)):
    """
    This function takes a pandas dataframe and a list of column names containing the names of
categorical columns and plots bivariate distribution of each column vs. each other column as a 100%
stacked bar plot in a square subplot grid. The function does not return anything.

Parameters:
-----------
data : pandas.DataFrame
    The dataframe containing the data to be plotted.
catcol_names : list of str
    The list of column names containing categorical values.
figsize : tuple of int (default=(15,15))
    The size of the figure to be displayed.

    """

    # create a square grid of subplots with the number of rows and columns equal to the number of categorical columns
    fig, ax = plt.subplots(len(catcol_names), len(catcol_names), figsize=figsize)

    # loop through the categorical columns
    for i in range(len(catcol_names)):
        for j in range(len(catcol_names)):

            # if i and j are equal, plot a countplot of the categorical column
            if i == j:
                sns.countplot(data=df_name, x=catcol_names[i], ax=ax[i,j])
                ax[i,j].set_xlabel('')
                ax[i,j].set_ylabel('')
                ax[i,j].set_title(catcol_names[i])

            # if i and j are not equal, plot a 100% stacked bar plot of the categorical columns
            else:
                # cross tabulate the two categorical columns
                ctab = pd.crosstab(df_name[catcol_names[i]],
                                   df_name[catcol_names[j]],
                                   normalize='index').round(2)*100
                # plot the stacked bar plot
                ctab.plot(kind='bar',
                          stacked=True,
                          ax=ax[i,j],
                          legend=True,
                          rot=0,
                          width=0.8,
                          edgecolor='white',
                          linewidth=1)
                # set the legend font size to 25% of the default
                ax[i,j].legend(fontsize='xx-small')
                # add a figure title with fontsize 25% more than the fontsize used for the subplots
                fig.suptitle('Bivariate Analysis of Categorical Features', fontsize='xx-large')

    plt.tight_layout()
    plt.show()

