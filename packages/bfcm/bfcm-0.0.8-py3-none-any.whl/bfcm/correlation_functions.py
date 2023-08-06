import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from statsmodels.stats.weightstats import DescrStatsW


def weighted_pearson(df, var1, var2, weights):
    """ Function to calculate the weighted pearson coefficient between two features

    :param df: dataframe containing the two features of interest
    :type df: Pandas dataframe
    :param var1: name of the first feature
    :type var1: str
    :param var2: name of the second feature
    :type var2: str
    :param weights: instance weights
    :type weights: list
    :return: weighted pearson correlation coefficient
    :rtype: float
    """

    df = df[[var1, var2]]

    # df to np array
    if isinstance(df, pd.DataFrame):
        df = df.to_numpy()
    # df to np.float64
    df = df.astype(np.float64)


    d1 = DescrStatsW(df, weights=weights)

    return d1.corrcoef[0][1]


def weighted_cramer(df, var1, var2, weights):
    """ Function to calculate the weighted Cramer's V between two features

    :param df: dataframe containing the two features of interest
    :type df: Pandas dataframe
    :param var1: name of the first feature
    :type var1: str
    :param var2: name of the second feature
    :type var2: str
    :param weights: instance weights
    :type weights: list
    :return: weighted Cramer's V correlation coefficient
    :rtype: float
    """


    var1_cats = np.unique(df[var1])
    var1_cats_len = len(var1_cats)
    var2_cats = np.unique(df[var2])
    var2_cats_len = len(var2_cats)

    cont = np.zeros((var1_cats_len, var2_cats_len))

    weights = np.array(weights)

    
    for i in range(var1_cats_len):
        for j in range(var2_cats_len):
            cont[i,j] = weights[(df[var1] == var1_cats[i]) & (df[var2] == var2_cats[j])].sum()

    stat, p, dof, exptected = chi2_contingency(cont)

    cramer = np.sqrt((stat)/(np.sum(weights)*(np.min([var1_cats_len-1,var2_cats_len-1]))))
    
    return cramer



if __name__ == "__main__":
    pass
