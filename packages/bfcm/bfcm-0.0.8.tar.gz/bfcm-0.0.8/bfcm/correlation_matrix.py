import numpy as np
import pandas as pd
import skfuzzy  
from scipy.stats import chi2_contingency
from statsmodels.stats.weightstats import DescrStatsW


def correlation_matrix(data, types, weights = None):
    """ Generate weighted correlation matrix for a given dataframe.

    :param data: data set
    :type data: Pandas Dataframe
    :param types: attribute types (including outcome class)
    :type types: Numpy array
    :param weights: instance weights
    :type weights: Numpy array
    :return: correlation matrix
    :rtype: Pandas Dataframe
    """

    # if weights is not specified, set weights to 1 for all instances
    if weights is None:
        weights = np.ones(len(data))

    # attributes in data
    attributes = data.columns

    # Remove outcome class
    X = data.iloc[:,:-1]
    

    # Create dataset with symbolic values for numerical features
    if "nominal" in types[:-1]:

        symb_X = X.copy()
        for col in range(len(types)):
            if types[col] == "numeric":
                
                symb_X[symb_X.columns[col]] = symbolized_var(X, X.columns[col])


    
    # Initiate array to store correlations
    correlation_matrix = np.zeros(shape=[len(attributes)-1, len(attributes)-1])

    # Loop over all attributes and calculate correlation for every combination
    for x in range(len(attributes)-1):
        correlation_matrix[x,x] = 1
        for y in range(len(attributes)-1):
            if x != y and y > x:
                if types[x] == "numeric" and types[y] == "numeric":
                    # Pearson if both attributes are numerical
                    correlation_matrix[x,y] = correlation_matrix[y,x] = weighted_pearson(X, attributes[x], attributes[y], weights)
                elif types[x] == "nominal" and types[y] == "nominal":
                    # Crámer's V if both attributes are nominal
                    correlation_matrix[x,y] = correlation_matrix[y,x] = weighted_cramer(X, attributes[x], attributes[y], weights)

                elif types[x] == "numeric" and types[y] == "nominal":
                    # Crámer's V with numerical feature transformed into nominal
                    correlation_matrix[x,y] = correlation_matrix[y,x] = weighted_cramer(symb_X, attributes[y], attributes[x], weights)

                elif types[x] == "nominal" and types[y] == "numeric":
                    # Same as previous condition, with reversed attribute type order
                    correlation_matrix[x,y] = correlation_matrix[y,x] = weighted_cramer(symb_X, attributes[x], attributes[y], weights)

    correlation_matrix =  np.abs(correlation_matrix)

    correlation_matrix = pd.DataFrame(correlation_matrix, columns = attributes[:-1], index = attributes[:-1])

    correlation_matrix.to_csv("correlation_matrix.csv", index=False)

    return correlation_matrix


def fc_means(df, var):
    """ Function to calculate the best number of fuzzy centers for a feature when using fuzzy c-means

    :param df: dataframe containing the feature of interest
    :type df: Pandas dataframe
    :param var: name of the feature for which to calculate the fuzzy centers
    :type var: str
    :return: best number of fuzzy centers
    :rtype: int
    """
    # if var is string
    if isinstance(var, str):
        # get index of var column
        var = df.columns.get_loc(var)
        # pass
    
    # df to numpy
    df = df.values

    xpts = df[:, var].reshape(-1, 1)
    # xpts = df[var]
        
    xpts = xpts[~pd.isnull(xpts)].reshape(-1, 1)


    # Modification
    alldata = np.vstack((xpts.flatten(), xpts.flatten()))
    

    # alldata to np.float64
    alldata = alldata.astype(np.float64)

    fpcs = []
    highest_fpc = 0
    best_cntr = None
    for n_centers in range(2,10):
        cntr, u, u0, d, jm, p, fpc = skfuzzy.cluster.cmeans(alldata, n_centers, 2, error=0.005, maxiter=1000, init=None)
        fpcs.append(fpc)
        if fpc > highest_fpc:
            highest_fpc = fpc
            best_cntr = cntr

    return best_cntr
    
def symbolized_var(df, var):
    """ Function to symbolize a feature using fuzzy c-means

    :param df: dataframe containing the feature of interest
    :type df: Pandas dataframe
    :param var: feature that is to be symbolized
    :type var: str
    :return: _description_
    :rtype: _type_
    """
    # Get fuzzy centers

    cntrs = fc_means(df, var)


    # transform nums in to symbols
    new_var = []

    symb_labels = [str(num) for num in range(1,len(cntrs)+1)]

    for row in df[var]:
        sum_di = 0
        prot_distances = []
        norm_distances = [] 

        for center in cntrs:
            # Euclidean distance
            distance = np.linalg.norm(center - row)
            sum_di += distance
            prot_distances.append(distance)
            
        for item in range(len(prot_distances)):
            norm_distances.append(prot_distances[item] / sum_di)
        
        label = norm_distances.index(min(norm_distances))
        
        new_var.append(symb_labels[label])

    return new_var

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

import sys
if __name__ == "__main__":
    double_args = correlation_matrix(sys.argv)
    print("In mymodule:",double_args)
    

