import pandas as pd
import numpy as np
from sklearn.metrics import auc, roc_curve
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


def comb_auc_recall(y_true, y_proba, y_preds, recall_weight):
    '''
    Purpose: Get a combined evalution of AUC and recall that weights recall a bit more heavily since we care the most 
    about accurately identifying fires
    Inputs:
    ------
        y_true:         numpy array
                        array of actual binary y values in test set
        y_proba:        numpy array
                        probability predictions from model
        y_preds:        numpy array
                        binary predictions from model
        recall_weight : float
                        weight for recall value
                 
    Returns:
    --------
        weighted average of AUC and recall
    
    '''
    fpr, tpr, thresholds = roc_curve(y_true, y_proba)
    roc_auc = auc(fpr, tpr)
    recall = recall_score(y_true, y_preds)
    return (roc_auc + 1.25*recall)/2



def EV_binary(y_true, y_preds, V_tp, V_tn, C_fp, C_fn):
    '''
    Purpose: Generate cost sensitive expected value for binary classification of wildfires
    -------
    Inputs:
    ------
        y_true:  numpy array
                 array of actual binary y values in test set
        y_preds: numpy array
                 predictions from model
        V_tp :   float
                 value of a true positive 
        V_tn :   float
                 value of a true negative
        C_fp :   float
                 cost assigned to a false positive (i.e. predicting a wildfire when there is one)
        C_fn :   float
                 cost assigned to a false negative (i.e. predicting no wildfire when there is one)
    Returns:
    -------
        EV :     float
                 expected value for model
    '''
    #Geneate probabilities of wildfires i.e. rate of wildfires in the test set 
    P_1 = np.sum(y_true==1)/y_true.shape[0]
    P_0 = np.sum(y_true==0)/y_true.shape[0]
    cm = pd.DataFrame(confusion_matrix(y_true, y_preds, normalize = 'true'), columns = ['0', '1'], index = ['0','1'])
    TPR = cm.iloc[1,1]
    FPR = cm.iloc[0,1]
    EV = P_1*(TPR*V_tp + (1-TPR)*C_fn) + P_0*(FPR*C_fp + (1 - FPR)*V_tn)
    return EV