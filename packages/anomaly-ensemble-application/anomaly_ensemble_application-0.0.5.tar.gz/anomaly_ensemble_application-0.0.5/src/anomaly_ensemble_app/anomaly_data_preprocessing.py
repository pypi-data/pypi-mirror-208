#%%
import anomaly_libs as al

#%%
def find_min_samples(df):
    """
    Definition: min_samples is the minimum number of neighbors that a given point should have in order to be classified as a core point. 

    Choice: Generally, choose min_samples >= dimensionality of the data set.
            For 2-dimensional data, choose DBSCAN's default value of min_samples = 4 (Ester et al., 1996).
            For multi-dimensional data, choose min_samples = 2*dim, where dim= the dimensionlity of the data set (Sander et al., 1998).
    """
    print("Searching for DBSCAN's minimum number of samples")
    min_samples = 2*df.shape[1]

    print("Done with minimum number of samples")
    return(min_samples) 


#%%
def find_eps(df):
    """
    Definition: Eps is the minimum distance between two points below which they are considered neighbors.

    Choice: Choose eps = knee of the k-NN distance graph.
            k-NN distance graph calculates the average distance between each point and its k nearest neighbors.
            Fit a polynomial to the data where eps is the point of maximum curvature.
    """
    print('Searching for the best epsilon')
    min_samples = find_min_samples(df)
    knn = al.NearestNeighbors(n_neighbors=min_samples)
    knn = knn.fit(df)
    distances, indices = knn.kneighbors(df)
    distances = al.np.sort(distances, axis=0)
    distances = distances[:,1]
    kneedle = al.KneeLocator(range(len(indices)), distances, curve='convex', direction='increasing', interp_method="polynomial")
    eps = round(distances[kneedle.knee], 3)

    print("Done with searching for epsilon")

    return(eps)


#%%
def find_seasonal_period(df):
    """
    Definition: Seasonal period is the expected seasonal frequency. 

    Choice: Use Fast Fourier Transform to change the time series into frequency components. 
            Choose the first expected seasonal period at the maximum amplitude.
    """
    print("Stepped into ThymeBoost params' search")
    ## Frequency
    n = df.size # size of sample or data set
    sr = 1 # sample rate
    d = 1./sr # sample space
    freq = al.rfftfreq(n, d) 

    ## Amplitude
    yf = al.rfft(df) # Fourier Transform of real numbers
    yf = abs(yf[0:al.np.size(freq)])
    
    ## expected seasonal frequency at highest amplitude
    if(al.np.argmax(yf) != 0):
        p = int(1 / freq[al.np.argmax(yf)])
    else:                          
        p = int(1 / freq[al.np.argsort(yf, axis=0)[-2]])
    
    print("Done with ThymeBoost parameters' search")

    return(p)


#%%
def detrend(df, id_column, time_column, time_format):
    """
    Definition: Trend is the directional change over time. Detrend means to remove the trend.

    Reason: Time series data needs to be detrended so that its mean does not change over time.
    """
    print("Stepped into detrending")

    df = df.copy()
    df[time_column] = al.pd.to_datetime(df[time_column], format=time_format)
    df = df.set_index(time_column)
    parts = df[id_column].unique()
    output = list()
 
    for pn in parts:
        timeseries = df[df[id_column] == pn]
        timeseries = timeseries[['demand_quantity']]
              
        #Checking for trend with adfuller and detrendning with signal detrend if a trend is identified
        result = al.adfuller(timeseries.values)
        
        if result[1] > 0.05:
            detrended = al.signal.detrend(timeseries)
            timeseries['demand_quantity'] = detrended
                
        #Return the output
        output.append(timeseries)

    output = al.pd.concat(output)
    output.reset_index(inplace=True)
    df.reset_index(inplace=True)
    df.index.names = ['key']
    output.index.names = ['key']
    df.join(output, on='key', lsuffix='o_')
    print('Done with detrending')
    print(f"Printing head of df after detrend \n {df.head(5)}")

    return(df)


#%%
def deseasone(df, id_column, time_column, time_format):
    """
    Definition: Seasonality is the repetitive cyclic pattern over regular interval of period or time. Deseasonalize means to remove the seasonality.

    Reason: Time series data needs to be deseasonalized so that its variance does not vary over time.
    """
    print('Stepped into Deseasonalization')

    df = df.copy()
    df[time_column] = al.pd.to_datetime(df[time_column], format=time_format)
    df = df.set_index(time_column)
    parts = df[id_column].unique()
    output = list()
 
    for pn in parts:

        timeseries = df[df[id_column]==pn]
        timeseries = timeseries.drop(columns=id_column)
              
        #Checking for seasonality and deseasonalize
        seasonality = timeseries['demand_quantity'].autocorr()
        if seasonality > 0.75:
            tmp = timeseries.copy()
            tmp['dmd_no_seasonality'] = tmp['demand_quantity'].diff(12)
            tmp['dmd_no_seasonality'] = tmp['dmd_no_seasonality'].fillna(0)
            average = tmp['demand_quantity'].mean()
            tmp['demand_no_seasonlity'] = average+tmp['dmd_no_seasonality'] 
            
            ts_decompose = al.seasonal_decompose(x=timeseries, model='additive')
            deseasonalized = timeseries.demand_quantity.values - ts_decompose.seasonal
            
            timeseries['demand_quantity'] = deseasonalized
        
        #Return the output
        output.append(timeseries)
    output = al.pd.concat(output)
    output.reset_index(inplace=True)

    df.reset_index(inplace=True)
    df.index.names = ['key']
    output.index.names = ['key']
    df.join(output, on='key', lsuffix='o_')

    print('Done with deseasonalization')
    print(f"Printing head of df after deseason \n {df.head(5)}")

    return(df)


#%% 
def parameters_oc_svm(X, y, trials=10):
    """
    """
    print("Stepped into OCSVM parameters' search(kernel & nu)")
    study = al.optuna.create_study(direction="maximize")

    for _ in range(trials):
        #print(f"Trial #{_}")
        trial = study.ask()  # `trial` is a `Trial` and not a `FrozenTrial`.
    
        nu = trial.suggest_float('nu', 0.1, 1, step=0.1)
        k = trial.suggest_categorical('k', ('linear', 'poly', 'rbf', 'sigmoid'))
    
        oc_svm_model = al.OneClassSVM(kernel=k, nu=nu)
        labels = oc_svm_model.fit_predict(X)
        labels = labels-1
        labels = al.np.where(labels==-2,1,labels)
        accuracy = al.metrics.accuracy_score(y, labels)
        
        study.tell(trial, accuracy)  # tell the pair of trial and objective value
        trial = study.best_trial
        best_nu = format(trial.params['nu'])
        best_kernel = format(trial.params['k'])

    print(f"Found the best kernel for OCSVM: >>>> {best_kernel}")
    print(f"Found the best nu for OCSVM: >>>> {best_nu}")

    return(float(best_nu), best_kernel)


#%% 
def parameters_lof(X, y, trials=10):
    """
    """
    print("Searching for LOF's best algorithm")
    study = al.optuna.create_study(direction="maximize")

    for _ in range(trials):
        print(f"Trial #{_}")
        trial = study.ask()  # `trial` is a `Trial` and not a `FrozenTrial`.
    
        k = trial.suggest_categorical('k', ('ball_tree', 'auto', 'kd_tree', 'brute'))
        contamination = trial.suggest_float('contamination', 0.01, 0.5, step=0.1)
    
        lof_model = al.LocalOutlierFactor(algorithm=k, contamination=contamination)
        labels = lof_model.fit_predict(X)
        labels = labels-1
        labels = al.np.where(labels==-2, 1, labels)
        accuracy = al.metrics.accuracy_score(y, labels)
        
        study.tell(trial, accuracy)  # tell the pair of trial and objective value
        trial = study.best_trial
        best_alg = format(trial.params['k'])
        best_cont = format(trial.params['contamination'])

    print(f"Found the best LOF's algorithm: >>>> {best_alg} \n Best contamination rate for LOF: >>>> {best_cont}")

    return(best_alg, float(best_cont))

# %%
