
def select_features_corr_imp(df, feat_import, rho_cutoff, n_features):
    '''
    Purpose:
    -------
    Generate list of n_features that are ranked in top feature importances from a RF model and that are below a
    certain cutoff for correlation with all other current features in the model
    
    Inputs:
    ------
        df -          pandas DataFrame
                      training dataframe
        feat_import - pandas DataFrame
                      DataFrame of feature importances from a Random Forest model - must have columns "col" and 
                      "feature_importance"
        rho_cutoff -  float 
                      max correlation coefficient allowed 
        n_features -  int
                      number of features to select
    '''
    feat_import.sort_values(['feature_importance'], inplace = True, ascending = False)
    full_feature_list = feat_import['col'].tolist()
    selected_features = [feat_import['col'].iloc[0]]
    i = 1
    while len(selected_features)<= n_features:
        f = full_feature_list[i]
        #print(f)
        test_features = selected_features + [f]
        corr_df = df[test_features].corr()
        #print(corr_df)
        #print(corr_df[corr_df[f]!=1][f].max())
        if corr_df[corr_df[f]!=1][f].max()< rho_cutoff:
            selected_features.append(f)
            i+= 1
        else:
            i+= 1
        
            
    #final full correlation dataframe for sanity check
    output_corr_df = df[selected_features].corr()
    return selected_features, output_corr_df