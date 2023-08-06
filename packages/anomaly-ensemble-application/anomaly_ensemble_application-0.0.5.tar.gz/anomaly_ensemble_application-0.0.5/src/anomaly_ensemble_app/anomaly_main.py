#%%
from regex import D
import anomaly_detection as ad # importing the notebook for anomaly detection. The notebook is called anomaly_detection. It contains the functions which are actually detecting the anomaly and the voting system (ensamble method)
import anomaly_libs as al # in this notebook we specify all the libs which are needed for the whole package
import anomaly_data_preprocessing as adp # data preprocessing steps. Detrend/Deseason/Find eps/n_samples for DBSCAN and seasonality period for ThymeBoost

#! New cell
# %%
# If labels are provided - we can compute the performance metrics, otherwise return only labels
# As well, if labels are provided and the labels column is correctly specified, then we can compute the performance metrics, and find somewhat best parameters for OCSVM, LOF, ThymeBoost and DBSCAN
# When looking to detect anomalies, you should create an instance of the AnomalyDetection class [ex. ad_some_spefics = AnomalyDetection(parameters for the __init__ function)]
# Using class intances you can build different models in the same time and compare their results without having to redo all from the beginning.
available_models = ['dbscan', 'iforest', 'ThymeBoost', 'lof', 'tadgan', 'ocsvm']

class AnomalyDetection():
    # must have: data_set, id_column, time_column, time_format, labels - if any

    
    def __init__(self, data_set, id_column, features, time_column, time_format, models=['full'], labels=False):
        """
        Initiation of the class instance. 
        This function initiates all the attributes of the object.
        Later on the user can change their value by calling the object (ex. ad_some_spefics.ocsv_nu = your value)
        This function is also checking the current Python version, if it is higher than 3.7 then TADGAN model will be excluded from the list of models.
        """
        self.data_set = data_set
        self.labels = labels
        self.id_column = id_column
        self.features = features
        self.time_column = time_column
        self.time_format = time_format
        self.models = models
        self.dbscan_eps = 0.2 
        self.dbscan_n_samples = 5
        self.iforest_contamination = 0.07
        self.ocsvm_kernel = 'linear'
        self.ocsvm_nu = 0.6 
        self.lof_alg = 'auto'
        self.lof_contamination = 'auto'  # if no labels provided, we can't find the best contamination rate, therefore will go with auto
        self.threshold = 0.7
        self.tadgan_epochs = 4
        self.tadgan_limit = 3
        self.thyme_boost_p = 12
        self.final_df = 0
        self.full_df = 0
        self.performance_df = 0
            
    
        python_version = al.platform.python_version()
        splitted_version = python_version.split('.')
        joined_version = float('.'.join(splitted_version[0:2]))
        if self.models == ['full'] or 'tadgan' in self.models:
            if joined_version > 3.7:
                self.models = available_models
                print(f"With Python {python_version} it won't be possible to fit TADGAN, for that you need Python 3.7 \n Skipping TADGAN")
                self.models.remove('tadgan')
                print(self.models)
            else:
                print("All good we can run on a full speed!")
                self.models = available_models#['dbscan', 'iforest', 'ThymeBoost', 'ocsvm', 'lof']#, 'tadgan']

        print(f"These are the models to be fit: {self.models}")
        print(f"Default parameters are:\nDBSCAN_epsilon={self.dbscan_eps}\nDBSCAN_n_samples={self.dbscan_n_samples}\nOCSVM kernel={self.ocsvm_kernel}\nOCSVM nu={self.ocsvm_nu}\nLOF algorithm={self.lof_alg}\nLOF contamination={self.lof_contamination}\nThymeBoost p={self.thyme_boost_p}")


    # This function will find the best parameters for the given data so that the user can get the best results
    def find_parameters(self):
        """
        As the name states, this function will try to find the best parameters for our models. But this can be done only if the target/labels columns is provided.
        First, it will detrend and deseason the data.
        Then it will find the eps and min samples for DBSCAN and the seasonal period of ThymeBoost
        If labels are provided, we can find the best parameters for OCSVM(best kernel and best nu) and LOF(the best algorithm)
        """
        print("--------------------------\n\t\t Here will be a progress bar\n--------------------------")
        #def find_parameters(input_DF, time_column, time_format, features, labels, id_column, models=['full']):
        if self.labels!=False:
            data_set = self.data_set[[self.time_column, self.id_column, self.features, self.labels]]    
        else:
            data_set = self.data_set[[self.time_column, self.id_column, self.features]]

        # Detrending and deseasoning the data
        detrended_df = adp.detrend(data_set, self.id_column, self.time_column, self.time_format)
        deseasonalized_df = adp.deseasone(detrended_df, self.id_column, self.time_column, self.time_format)

        self.data_set = deseasonalized_df
        # Finding the best params for DBSCAN and ThymeBoost
        self.dbscan_eps = adp.find_eps(self.data_set[[self.features]])
        self.dbscan_n_samples = adp.find_min_samples(self.data_set)
        self.thyme_boost_p = adp.find_seasonal_period(self.data_set[[self.time_column]])

        if self.labels!=False:
            # Finding the best parameters for OCSVM, LOF 
            self.ocsvm_nu, self.ocsvm_kernel = adp.parameters_oc_svm(self.data_set[[self.features]], self.data_set[self.labels]) 
            self.lof_alg, self.lof_contamination = adp.parameters_lof(self.data_set[[self.features]], self.data_set[self.labels])
        else:
            print("Sorry can't find best parameters for OCSVM and LOF. But you can provide your inputs. check how to change class instance attributes")
        
        print(f"Suggested parameters are:\nDBSCAN_epsilon={self.dbscan_eps}\nDBSCAN_n_samples={self.dbscan_n_samples}\nOCSVM kernel={self.ocsvm_kernel}\nOCSVM nu={self.ocsvm_nu}\nLOF algorithm={self.lof_alg}\nLOF contamination={self.lof_contamination}\nThymeBoost p={self.thyme_boost_p}")
        return self.dbscan_eps, self.dbscan_n_samples, self.thyme_boost_p, self.ocsvm_kernel, self.ocsvm_nu, self.lof_alg, self.lof_contamination

    # This function will find the best parameters for the given data so that the user can get the best results
    def user_parameters(self):
        """
        As the name states, this function will try to find the best parameters for our models. But this can be done only if the target/labels columns is provided.
        First, it will detrend and deseason the data.
        Then it will find the eps and min samples for DBSCAN and the seasonal period of ThymeBoost
        If labels are provided, we can find the best parameters for OCSVM(best kernel and best nu) and LOF(the best algorithm)
        """
        print("--------------------------\n\t\t Here will be a progress bar\n--------------------------")
        self.dbscan_eps, self.dbscan_n_samples, self.thyme_boost_p, self.ocsvm_kernel, self.ocsvm_nu, self.lof_alg, self.lof_contamination = self.find_parameters()
        
        user_dbscan_eps = input(f"Current value of DBSCAN epsilon is {self.dbscan_eps}\n Do you want to change it?(Y/N): ")
        if user_dbscan_eps.casefold() == 'y':
            self.dbscan_eps = input("Enter DBSCAN epsilon: ") or self.dbscan_eps

        user_dbscan_n_samples = input(f"Current value of DBSCAN min_samples is {self.dbscan_n_samples}\n Do you want to change it?(Y/N):")
        if user_dbscan_n_samples.casefold() == 'y':
            self.dbscan_n_samples = input("Enter DBSCAN n_samples: ") or self.dbscan_n_samples
        
        user_ocsvm_kernel = input(f"Current value of OCSVM kernel is {self.ocsvm_kernel}\n Do you want to change it?(Y/N):")
        if user_ocsvm_kernel.casefold() == 'y':
            self.ocsvm_kernel = input("Enter OCSVM kernel: ") or self.ocsvm_kernel

        user_ocsvm_nu = input(f"Current value of OCSVM nu is {self.ocsvm_nu}\n Do you want to change it?(Y/N):")
        if user_ocsvm_nu.casefold() == 'y':
            self.ocsvm_nu = input("Enter OCSVM nu: ") or self.ocsvm_nu

        user_lof_alg = input(f"Current value of LOF algorithm is {self.lof_alg}\n Do you want to change it?(Y/N):")
        if user_lof_alg.casefold() == 'y':
            self.lof_alg = input("Enter LOF algorithm: ") or self.lof_alg

        user_lof_contamination = input(f"Current value of LOF contamination is {self.lof_contamination}\n Do you want to change it?(Y/N):")
        if user_lof_contamination.casefold() == 'y':
            self.lof_contamination = input("Enter LOF contamination: ") or self.lof_contamination
        
        user_thyme_boost_p = input(f"Current value of ThymeBoost p is {self.thyme_boost_p}\n Do you want to change it?(Y/N):")
        if user_thyme_boost_p.casefold() == 'y':
            self.thyme_boost_p = input("Enter ThymeBoost p: ") or self.thyme_boost_p

        print(f"User input parameters are:\nDBSCAN_epsilon={self.dbscan_eps}\nDBSCAN_n_samples={self.dbscan_n_samples}\nOCSVM kernel={self.ocsvm_kernel}\nOCSVM nu={self.ocsvm_nu}\nLOF algorithm={self.lof_alg}\nLOF contamination{self.lof_contamination}\nThymeBoost p={self.thyme_boost_p}")
        return self.dbscan_eps, self.dbscan_n_samples, self.thyme_boost_p, self.ocsvm_kernel, self.ocsvm_nu, self.lof_alg, self.lof_contamination

    # This function will detect anomalies within the given data. It will return a table with each model's performance as well as final labels of the app. 
    def find_anomalies(self):
        """
        This function will prepare the hyperparameters and call the function get_labels from anomaly_detection module
        After the the labels are computed, next the election function will be called which will retunr the results from the voting/election
        Based on the results, if the labels are passed, the function will call the performance metrics.
        data_set - the input data (data in which anomalies should be detected) [params: NxM dataset]
        id_column - index column or the column with distinct names
        time_column - the base data column. The most important date column [series/feature]
        time_format - needed to check the seasonality and trend [params ex: YYYY-MM-DD]
        """
        print("--------------------------\n\t\t Here will be a progress bar\n--------------------------")
        full_df = self.data_set.copy()
        work_data_set = self.data_set[[self.time_column, self.id_column, self.features]]

        models = full_df.columns.values.tolist()

        user_choice = input("Do you wish to change suggested best parameters (Y/N): ")
        if user_choice.casefold() == 'y':
            self.dbscan_eps, self.dbscan_n_samples, self.thyme_boost_p, self.ocsvm_kernel, self.ocsvm_nu, self.lof_alg, self.lof_contamination = self.user_parameters()
        else:
            self.dbscan_eps, self.dbscan_n_samples, self.thyme_boost_p, self.ocsvm_kernel, self.ocsvm_nu, self.lof_alg, self.lof_contamination = self.find_parameters()

        parameters = {
            "id":self.id_column, 
            "time_column":self.time_column, 
            "models":self.models, 
            "threshold":self.threshold, 
            "eps":self.dbscan_eps, 
            "min_samples":self.dbscan_n_samples, 
            "iforest_cont":self.iforest_contamination, 
            "p":self.thyme_boost_p, 
            "k":self.ocsvm_kernel, 
            "nu":self.ocsvm_nu, 
            "alg":self.lof_alg,
            "lof_cont":self.lof_contamination,
            "e":self.tadgan_epochs, 
            "l":self.tadgan_limit}

        print(work_data_set.head(5))
        results_df, results_dict = ad.get_labels(work_data_set, **parameters) 
        self.full_df = self.data_set.join(results_df)
        self.final_df = self.full_df.copy()
        self.final_df.drop(self.models, axis=1, inplace=True)

        if self.labels!=False:
            print("Computing performance metrics")
            accuracy = []
            exec_time = []
            #co2 = []
            precision = []
            recall = []
            f1_score = []
            for m in self.models:
                print(m)
                e_time = round(results_dict[m]['exec_time'], 3)
                #co2_impact = results_dict[m]['co2_impact']
                acc = round(al.metrics.accuracy_score(self.full_df.true_outlier, self.full_df[m]), 3)
                pre = round(al.metrics.precision_score(self.full_df.true_outlier, self.full_df[m]), 3)
                rec = round(al.metrics.recall_score(self.full_df.true_outlier, self.full_df[m]), 3)
                f1 = round(al.metrics.f1_score(self.full_df.true_outlier, self.full_df[m]), 3)
                accuracy.append(acc)
                precision.append(pre)
                recall.append(rec)
                f1_score.append(f1)
                exec_time.append(e_time)
                #co2.append(co2_impact)

            performance = al.np.array([self.models, accuracy, precision, recall, f1_score, exec_time]).T.tolist()
            self.performance_df = al.pd.DataFrame(performance, columns=['Model', 'Accuracy', 'Precision', 'Recall', 'F1 score', 'Time'])#, 'Time'])
            return self.performance_df
            print("Got performance metrics")

#! New cell
#%% This part should stay always commented. Decoment it only when you want to debug the package. Add your data set's path/separator/feature column name
# # Add your dataset here
# tracker = al.EmissionsTracker()
# tracker.start()
original_data = "syntethic_original.csv"
original_DF = al.pd.read_csv(original_data, sep=";")

# data_file = "synthetic_input_data.csv"
# data_set = al.pd.read_csv(data_file, sep=";")

# # Make a copy of the dataframe
# input_DF = data_set.copy()

features = "demand_quantity" # Specify the feature column

# Currently every model has the same weight during the voting (Democracy). Future steps - to add weight for each model's prediction.
# TADGAN is available, for now, only if the Python version is lower than 3.8
#anomaly_detection_obj = AnomalyDetection(data_set=input_DF, id_column='spare_part_id', features='demand_quantity', time_column='yyyymm', time_format='%Y%m')#['DBSCAN', 'IsolationForest', 'LOF', 'OCSVM', 'TADGAN'])#, labels='true_outlier')
# #%%
anomaly_detection_labels = AnomalyDetection(data_set=original_DF, id_column='spare_part_id', features='demand_quantity', time_column='yyyymm', time_format='%Y%m', labels='true_outlier')
#best_parameters = anomaly_detection_labels.find_parameters() # the user should decide which models are to be fit so that we know which parameters we try to find
anomalies = anomaly_detection_labels.find_anomalies() # get params directly. Define with default 
#print(anomalies)
#! New cell
#%%
# Change suggested/default parameters
anomaly_detection_labels.performance_df
print(anomaly_detection_labels.performance_df)
# emissions: float = tracker.stop()
# print(f"Emissions: {emissions}")
# print(f"So far, {0 if emissions==None else emissions*1000} CO2 was generated by this script")

# %%
