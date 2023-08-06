#%%
import anomaly_libs as al
import anomaly_models as am
#tracker = al.EmissionsTracker()

# %%
def election(voters, n_voters, threshold):
    """
    Election is the function that is calculating how many models categorized the data point as out/in lier
    Based on that number, it computes the average score. Summ of all results divided by the number of models/voters.
    v - is the DataFrame with indexes and categories of each model(voter)
    n_voters - the number of models that were trained/fit for this run.
    """
    
    for col in voters.columns:
        voters[col] = voters[col].astype(int)

    print("### Starting the election ...")
    voters = voters.replace(1, 0) # replacing inlier with 0 to be able to compute the average
    voters = voters.replace(-1, 1) # replacing outlier with 1 to be able to compute the average
    sum_votes = voters.sum(axis='columns') # summing all votes(0, 1) and to know how many models categorized the point as outlier
    election_results = sum_votes / n_voters # simple average. Later to be used with a threshold for final determination (outlier/inlier)
    
    voters['labels'] = election_results
    voters['labels'] = voters['labels'].apply(lambda x: 1 if x >= threshold else 0)
    print(voters.labels.value_counts())
    print("### Election complete!")

    return(voters)


# %%
#def get_labels(df, id, time_column, models, threshold=0.6, X=0, eps=0.2, min_samples=4, contamination=0.07, p=12, k='linear', nu=1, alg='auto', e=4, l=3):
def get_labels(X, **kwargs):
    """ 
    df - data frame to be used
    id - the column which contains the spare parts
    models - number of models to be fit
    eps - epsilon for DBSCAN
    min_samples - minimum number of samples for DBSCAN
    contamination - contamination rate for Isolation Forest
    p - seasonal period for ThymeBoost
    k - the kernel for OCSVM
    alg - the algorithm for LOF
    e - number of epochs for TADGAN
    l - limit for TADGAN
    """
    # Initiating containers to append labels from each fit of each model
    print("### Initiating contatiners for votes")
    print('Current version >>> 0.3.13')

    elements_to_itterate = X[kwargs['id']].drop_duplicates()

    models_dict = {
        'dbscan': {
            'function': am.fit_dbscan,
            'exec_time':0,
            'labels':[],
            'params':{'eps':kwargs['eps'], 'min_samples':kwargs['min_samples']}},
        'iforest': {
            'function': am.fit_iforest,
            'exec_time':0,
            'labels':[], 
            'params': {'contamination':kwargs['iforest_cont']}},
        'ThymeBoost': {
            'function': am.fit_ThymeBoost,
            'exec_time':0,
            'labels':[], 
            'params':{'p':kwargs['p']}},
        'ocsvm': {
            'function': am.fit_ocsvm,
            'exec_time':0,
            'labels':[],
            'params':{'kernel':kwargs['k'], 'nu':kwargs['nu']}},
        'lof': {
            'function': am.fit_lof,
            'exec_time':0,
            'labels':[],
            'params':{'algorithm':kwargs['alg'], 'contamination':kwargs['lof_cont']}}#,
        # 'tadgan': {
        #     'function': am.fit_tadgan,
        #     'exec_time':0,
        #     'co2_impact':0,
        #     'labels':[], 
        #     'params':{'epochs':kwargs['e'], 'limit':kwargs['l']}}
    }

    print("### Containers initiated")


    print("### Preparing the Data Frame")
    df = X.copy()

    for spare_part in elements_to_itterate:
        part_df = df.where(df[kwargs['id']] == spare_part).dropna()
        tadgan_df = part_df.copy()
        part_df.drop([kwargs['id'], kwargs['time_column']], axis=1, inplace=True)
        for model in kwargs['models']:
            if model == 'tadgan':
                time_start = al.time.time()
                model_labels = models_dict[model]['function'](tadgan_df, **models_dict[model]['params'])
                models_dict[model]['labels'].extend(model_labels)
                time_passed = al.time.time() - time_start
                models_dict[model]['exec_time'] += time_passed
            else:
                # tracker.start()
                time_start = al.time.time()
                model_labels = models_dict[model]['function'](part_df, **models_dict[model]['params'])
                models_dict[model]['labels'].extend(model_labels)
                time_passed = al.time.time() - time_start
                models_dict[model]['exec_time'] += time_passed
                # emissions: float = tracker.stop()
                # if emissions is None:
                #     models_dict[model]['co2_impact'] += 0
                # else:
                #     models_dict[model]['co2_impact'] += emissions
            

    labels_list = []
    for k, v in models_dict.items():
        labels_list.append(al.np.array(v['labels']).transpose())


    transposed_array = al.np.array(labels_list)#.T
    transposed_array = transposed_array.tolist()
    results_df = al.pd.DataFrame(labels_list)
    results_df = results_df.transpose().set_axis(kwargs['models'], axis=1, inplace=False)
    print(results_df.head(10))

    print("### Preparing for election.")
    election_results = election(results_df, len(kwargs['models']), kwargs['threshold'])

    return(election_results, models_dict)

# %%
