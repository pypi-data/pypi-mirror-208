import skfuzzy  
import numpy as np
import pandas as pd


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
