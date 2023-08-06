#%%
from . import anomaly_libs as al

# %% Isolation Forest
def fit_iforest(X, **kwargs):
    """
    Add your description here
    """
    ifo = al.IsolationForest(contamination=kwargs['contamination'])
    ifo_labels = ifo.fit_predict(X)
    
    return(ifo_labels)


# %% DBSCAN
def fit_dbscan(X, **kwargs):
    '''
    This function builds the DBSCAN model and returns the labels(clusters) for each row of data.
    It takes as parameters X - which is the data set that should be clustered (labeled)
    eps or epsilor, which is a very critical parameter for the model
    min_samples - The number of samples (or total weight) in a neighborhood for a point to be considered as a core point. This includes the point itself.
    '''
    dbscan_model = al.DBSCAN(eps=kwargs['eps'], min_samples=kwargs['min_samples']).fit(X)
    dbscan_labels = dbscan_model.labels_

    # Converting clusters to 1
    dbscan_labels[al.np.where(dbscan_labels!=-1)] = 1
    
    return(dbscan_labels)


# %%
def fit_ThymeBoost(X, **kwargs):
    """
    Add your description here
    """
    boosted_model = al.tb.ThymeBoost()
    ThymeBoost_model = boosted_model.detect_outliers(X['demand_quantity'],
                                       trend_estimator='linear',
                                       seasonal_estimator='fourier',
                                       seasonal_period=kwargs['p'],
                                       global_cost='maicc',
                                       fit_type='global')
    
    TB_output = ThymeBoost_model[['outliers']]
    TB_output.outliers = TB_output.outliers.replace({True: '-1', False: '1'})
    tb_labels = TB_output['outliers'].tolist()
    
    return(tb_labels)


# %%
# One-Class SVM
def fit_ocsvm(X, **kwargs):
    """
    Add your description here
    """
    oc_svm = al.OneClassSVM(kernel=kwargs['kernel'], nu=kwargs['nu'])
    ocsvm_labels = oc_svm.fit_predict(X)
    return(ocsvm_labels)


# %% LOF

def fit_lof(X, **kwargs):
    """
    Add your description here
    """
    lof = al.LocalOutlierFactor(algorithm=kwargs['algorithm'], contamination=kwargs['contamination'])
    lof_labels = lof.fit_predict(X)
    
    return(lof_labels)


#%%
#TADGAN
def fit_tadgan(X, **kwargs):
    '''
    '''
    #Change the timeformat
    print("Inside TADGAN")
    print(type(X), X.columns)
    X = X.rename(columns={'yyyymm':'timestamp','demand_quantity':'value'})
    X['timestamp'] = al.pd.to_datetime(X['timestamp'], format='%Y%m')
    X['timestamp'] = (X['timestamp'] - al.pd.Timestamp("1970-01-01")) // al.pd.Timedelta('1s')
    
    hyperparameters = {'keras.Sequential.LSTMTimeSeriesRegressor#1': {'epochs': kwargs['epochs'],'verbose': True}}
    orion = al.Orion(pipeline='lstm_dynamic_threshold', hyperparameters=hyperparameters)
    orion.fit(X)
    anomalies = orion.detect(X)
    anomalies_selected = anomalies[anomalies['severity']>kwargs['limit']].reset_index(drop=True)
    
    X['label'] = 0

    for index in anomalies_selected.index:
        print(index)
        X['label'] = X.apply(lambda row: 1 if (row['timestamp'] > anomalies_selected['start'][index]) & (row['timestamp']<(anomalies_selected['end'][index]+1)) else row['label'], axis=1)
        labels = X['label']
    
    return (labels)
# %%
