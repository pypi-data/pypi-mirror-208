from tabulate import tabulate
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import make_scorer
from statistics import mean
from sklearn.metrics import precision_score, recall_score, confusion_matrix, classification_report, accuracy_score, f1_score
from matplotlib.backends.backend_pdf import PdfPages
from rpy2 import robjects
from sklearn.datasets import load_digits
import argparse
import matplotlib.pyplot as plt
import glob
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import wasserstein_distance
from scipy.stats import entropy
import torch
import os
import numpy as np
import pickle  # req
import pandas as pd  # req
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture  # req
from sklearn.decomposition import PCA
import random
from time import time
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import make_scorer
from statistics import mean
from sklearn.metrics import precision_score, recall_score, confusion_matrix, classification_report, accuracy_score, f1_score
from rpy2.robjects import r, pandas2ri
import pandas as pd
import numpy as np
import argparse
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
import os
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import ctgan
import pandas as pd
from sklearn.decomposition import PCA
import sys
import warnings
import time
import torch
warnings.filterwarnings("ignore")
label_encoder = preprocessing.LabelEncoder()

def predict_best_models(df, discrete_cols):
  num_disc_cols = len(discrete_cols)
  num_cont_cols = len(df.columns) - num_disc_cols - 1
  dc_ratio = float('inf')
  results_data = []
  if num_cont_cols!=0:
    dc_ratio = num_disc_cols/num_cont_cols
  best_model = 'GMM'
  if dc_ratio>=2:
    best_model = 'BNR'
  results_data.append(['D/C Ratio', dc_ratio,best_model])

  num_features = len(df.columns)
  num_samples = df.shape[0]
  pn_ratio = num_features/num_samples

  best_model = 'GMM'
  if pn_ratio<0.1:
    best_model = 'PCA'
  results_data.append(['P/N Ratio', pn_ratio,best_model])

  best_model = 'GMM'
  results_data.append(['Samples Count', num_samples,best_model])

  if num_features>22:
    best_model = 'GMM/PCA'
  results_data.append(['Features Count', num_features,best_model])

  table = tabulate(results_data, headers=['Characteristics', 'Value', 'Best Model'], tablefmt='orgtbl')

  print(table)
  return table

def gen_gmm(df,discrete_cols,req_size,target_class,do_PCA):
  if "Unnamed: 0" in df.columns.values:
    df.drop(["Unnamed: 0"], axis=1, inplace=True)
  cols = df.columns
  df_cpy = df.copy()
  print('Data Shape: ',df.shape)
  for col in df.columns:
    if is_string_dtype(df[col]):
      df_cpy[col] = label_encoder.fit_transform(df_cpy[col])
  target_col = df_cpy[target_class]
  df_cpy_trim = df_cpy.drop(target_class, axis=1)
  if do_PCA:
    pca = PCA(0.95)
    df_cpy_trim = pca.fit_transform(df_cpy_trim)
    df_cpy_trim = pd.DataFrame(df_cpy_trim)
    df_cpy_trim.columns = df_cpy_trim.columns.astype(str)
    print('Data Shape after PCA: ',df_cpy_trim.shape)
  df_cpy_trim[target_class] = target_col
  pca_cols = df_cpy_trim.columns
  n_components_range = np.arange(2, 20)
  models = [
      GaussianMixture(n_components=n, covariance_type="tied",random_state=0).fit(df_cpy_trim)
      for n in n_components_range
    ]
  bic_data = [m.bic(df_cpy_trim) for m in models]
  min_value_idx = bic_data.index(min(bic_data))
  min_value = n_components_range[min_value_idx]
  print("Minimum for {} components".format(min_value))
  # need to optimize for n components
  model = GaussianMixture(n_components=min_value,covariance_type="full", random_state=0)
  model.fit(df_cpy_trim)
  num_samples = req_size
  print("Model Covergence", model.converged_)
  data_new = model.sample(num_samples)
  data_new = pd.DataFrame(data_new[0])
  data_new.columns = pca_cols
  target_syn_col = data_new[target_class]
  data_new.drop([target_class],axis=1,inplace=True)
  if do_PCA:
    data_new = pca.inverse_transform(data_new)
    data_new = pd.DataFrame(data_new, index=None)
  data_new[target_class] = target_syn_col
  data_new.columns = cols
  for i in df.columns:
    if is_string_dtype(df[i]):
      class_corrector(df_cpy, data_new, i)
      data_new[i] = label_encoder.inverse_transform(data_new[i])
  if is_string_dtype(df[target_class])==False:
    class_corrector(df_cpy, data_new, i)
  print()
  return data_new

def gen_bn(df,discrete_cols,req_size,target_class,do_PCA):
  label_encoder = preprocessing.LabelEncoder()
  pca = PCA(0.95)
  if "Unnamed: 0" in df.columns.values:
    df.drop(["Unnamed: 0"], axis=1, inplace=True)
  cols = df.columns
  print('Data Shape: ',df.shape)
  # df[target_class]= label_encoder.fit_transform(df[target_class])
  target_col = df[target_class]
  data_trim = df.drop([target_class], axis=1)
  if do_PCA:
    for col in df.columns:
      if is_string_dtype(df[col]):
        data_trim[col] = label_encoder.fit_transform(data_trim[col])
  data_cpy = data_trim.copy()
  if do_PCA:
    pca = PCA(0.95)
    data_trim = pca.fit_transform(data_trim)
    data_trim = pd.DataFrame(data_trim)
    data_trim.columns = data_trim.columns.astype(str)
    print('Data Shape after PCA: ',data_trim.shape)
  data_trim[target_class] = target_col
  pca_cols = data_trim.columns
  # ----------Bayesian Network Synthetic Data Generation Part------------------
  robjects.r('''
    install.packages("https://www.bnlearn.com/releases/bnlearn_latest.tar.gz", repos = NULL, type = "source")
    ''')

  pandas2ri.activate()
  robjects.globalenv['df'] = data_trim
  robjects.globalenv['size'] = req_size
  # robjects.globalenv['data_name'] = input_file+"_"
  # robjects.globalenv['syn_file_path'] = syn_file_path

  print('\n Generating Synthetic data file.......\n')

  robjects.r('''
    library(bnlearn)

  data <- df

  data[] <- lapply(data, as.factor)
  
    dag = hc(data, score = 'aic')
    fitted = bn.fit(dag, data)
    syn_data = rbn(fitted, size)

  write.csv(syn_data, 'output_bnr_temp.csv', row.names = FALSE)
  
    ''')

  print('\n Generation Done\n')

  data_new = pd.read_csv('output_bnr_temp.csv')
  data_new.columns = pca_cols
  target_syn_col = data_new[target_class]
  data_new.drop([target_class],axis=1,inplace=True)
  if do_PCA:
    data_new = pca.inverse_transform(data_new)
    data_new = pd.DataFrame(data_new, index=None)
  data_new[target_class] = target_syn_col
  data_new.columns = cols
  if do_PCA==True:
    for col in df.columns:
      if is_string_dtype(df[col]):
        class_corrector(data_cpy, data_new, col)
        data_new[col] = label_encoder.inverse_transform(data_new[col])
  os.remove('output_bnr_temp.csv')
  print()
  return data_new

def gen_ctgan(df,discrete_cols,req_size,target_class,do_PCA):
  label_encoder = preprocessing.LabelEncoder()
  device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
  if "Unnamed: 0" in df.columns.values:
    df = df.drop("Unnamed: 0", axis=1)
  column_names = df.columns
  # Assuming last column of the dataset is the target class
    # target_class = column_names[len(column_names) - 1]
    # Dropping target class
  print('Data Shape: ',df.shape)
  data_trim = df.drop([target_class], axis=1)
  if do_PCA:
    for col in df.columns:
      if is_string_dtype(df[col]):
        data_trim[col] = label_encoder.fit_transform(data_trim[col])
  data_cpy = data_trim.copy()
  if do_PCA:
    pca = PCA(0.95)
    data_trim = pca.fit_transform(data_trim)
    data_trim = pd.DataFrame(data_trim)
    data_trim.columns = data_trim.columns.astype(str)
  num_samples = len(df)
  # Adding target class
  data_trim[target_class] = df[target_class]
  pca_cols = data_trim.columns
  # Synthesizing data
  model = ctgan.CTGAN(batch_size=10,generator_dim=(128, 128),discriminator_dim=(128, 128),epochs=1000,pac=10)
  
  start_time = time.time()
  if do_PCA:
    print('Data Shape after PCA: ',data_trim.shape)
    model.fit(data_trim)
  else:
    model.fit(data_trim, discrete_cols)
  gen_sample = model.sample(req_size)
  print('Time of model training: ', time.time() - start_time)
  gen_sample = pd.DataFrame(gen_sample)
  gen_sample.columns = pca_cols
  target_syn_col = gen_sample[target_class]
  gen_sample.drop([target_class],axis=1,inplace=True)
  if do_PCA:
    gen_sample = pca.inverse_transform(gen_sample)
    gen_sample = pd.DataFrame(gen_sample, index=None)
  gen_sample[target_class] = target_syn_col
  gen_sample.columns = column_names
  if do_PCA==True:
    for col in df.columns:
      if is_string_dtype(df[col]):
        class_corrector(data_cpy, gen_sample, col)
        gen_sample[col] = label_encoder.inverse_transform(gen_sample[col])
  return gen_sample

#--------------------------------------------------------------------------------------------------------------

'''
PCA Generation Implementation 
Functions Code Source:

1.  Synthesising artificial patient-level data for Open Science - an evaluation of five methods
    Michael Allen, Andrew Salmon
    medRxiv 2020.10.09.20210138; doi: https://doi.org/10.1101/2020.10.09.20210138

2.  Karl Pearson F.R.S. (1901) LIII. On lines and planes of closest fit to systems of points in space, The London, Edinburgh, and Dublin Philosophical Magazine and Journal of Science, 2:11, 559-572, DOI: 10.1080/14786440109462720
'''
def get_PCA_model(data, n_components=0):
    label_encoder = preprocessing.LabelEncoder()
   
    # If n_components not passed to function, use number of features in data
    if n_components == 0:
        n_components = min(data.shape[1], data.shape[0])
    

    pca = PCA(n_components)
    transformed_X = pca.fit_transform(data)

    #fit_transform reduces X to the new datasize if n components is specified
    explained_variance = pca.explained_variance_ratio_
    
    # Compile a dictionary to return results
    results = {'model': pca,
               'transformed_X': transformed_X,
               'explained_variance': explained_variance}
    
    return results

def generate_synthetic_data_pca(X_original, y_original, number_of_samples, 
                           n_components=0):
    
    
    # Split the training data into positive and negative
    labels = np.unique(y_original)

    mask = y_original == labels[1]
    X_train_pos = X_original[mask]
    mask = y_original == labels[0]
    X_train_neg = X_original[mask]

    # If number of PCA not passed, set to number fo min(features/samples) in X
    if n_components == 0:
        n_components = min(X_train_pos.shape[1], X_train_pos.shape[0], X_train_neg.shape[1], X_train_neg.shape[0])
    
    # Pass negative and positive label X data sets to Principal Component Analysis 
    pca_pos = get_PCA_model(X_train_pos, n_components)
    pca_neg = get_PCA_model(X_train_neg, n_components)
    
    # Set up list to hold negative and positive label transformed data
    transformed_X = []
    
    # Create synthetic data for positive and neagtive PCA models 
    for pca_model in [pca_pos, pca_neg]:
        
        # Get PCA tranformed data
        transformed = pca_model['transformed_X']
        
        # Get means and standard deviations, to use for sampling
        means = transformed.mean(axis=0)
        stds = transformed.std(axis=0)
    
        # Make synthetic PC data using sampling from normal distributions
        synthetic_pca_data = np.zeros((number_of_samples, n_components))
        for pc in range(n_components):
            synthetic_pca_data[:, pc] = \
                np.random.normal(means[pc], stds[pc], size=number_of_samples)
        transformed_X.append(synthetic_pca_data)
        
    # Reverse transform data to create synthetic data to be used
    X_synthetic_pos = pca_pos['model'].inverse_transform(transformed_X[0])
    X_synthetic_neg = pca_neg['model'].inverse_transform(transformed_X[1])
    y_synthetic_pos = np.full((X_synthetic_pos.shape[0],1), labels[1])
    y_synthetic_neg = np.full((X_synthetic_neg.shape[0],1), labels[0])

    
    # Combine positive and negative and shuffle rows
    X_synthetic = np.concatenate((X_synthetic_pos, X_synthetic_neg), axis=0)
    y_synthetic = np.concatenate((y_synthetic_pos, y_synthetic_neg), axis=0)
    
    # Randomise order of X, y
    synthetic = np.concatenate((X_synthetic, y_synthetic), axis=1)
    shuffle_index = np.random.permutation(np.arange(X_synthetic.shape[0]))
    synthetic = synthetic[shuffle_index]
    X_synthetic = synthetic[:,0:-1]
    y_synthetic = synthetic[:,-1]
                                                                   
    return X_synthetic, y_synthetic


#--------------------------------------------------------------------------------------------------------------

def gen_pca(df,discrete_cols,req_size,target_class,do_PCA):
  label_encoder = preprocessing.LabelEncoder()
  if "Unnamed: 0" in df.columns.values:
    df.drop(["Unnamed: 0"], axis=1, inplace=True)
  print('Data Shape: ',df.shape)
  cols = df.columns
  df_cpy = df.copy()
  for col in df.columns:
    if is_string_dtype(df[col]):
      df_cpy[col] = label_encoder.fit_transform(df_cpy[col])
  target_col = df_cpy[target_class]
  df_cpy_trim = df_cpy.drop(target_class, axis=1)
  if do_PCA:
    pca = PCA(0.95)
    df_cpy_trim = pca.fit_transform(df_cpy_trim)
    df_cpy_trim = pd.DataFrame(df_cpy_trim)
    df_cpy_trim.columns = df_cpy_trim.columns.astype(str)
    print('Data Shape after PCA: ',df_cpy_trim.shape)
  df_cpy_trim[target_class] = target_col
  pca_cols = df_cpy_trim.columns

  X = df_cpy_trim.drop([target_class],axis=1)
  y = df_cpy_trim[target_class]
  X_syn, y_syn = generate_synthetic_data_pca(X, y, int(req_size/2))

  syn_data = pd.DataFrame(X_syn, columns = X.columns)
  syn_data[target_class] = y_syn

  syn_data.columns = pca_cols
  target_syn_col = syn_data[target_class]
  syn_data.drop([target_class],axis=1,inplace=True)
  if do_PCA:
    syn_data = pca.inverse_transform(syn_data)
    syn_data = pd.DataFrame(syn_data, index=None)
  syn_data[target_class] = target_syn_col
  syn_data.columns = cols
  for i in df.columns:
    if is_string_dtype(df[i]):
      class_corrector(df_cpy, syn_data, i)
      syn_data[i] = label_encoder.inverse_transform(syn_data[i])
  if is_string_dtype(df[target_class])==False:
    class_corrector(df_cpy, syn_data, i)
  print()
  return syn_data

def generate_data(df,discrete_cols,models,req_size,target_class,do_PCA):
  disc_cols = discrete_cols.copy()
  print('-------------------------------------------------------------')
  print('"Preprocessing Data................................')
  print()
  df_processed = preprocess_data(df,disc_cols,target_class)
  table = predict_best_models(df,discrete_cols)
  syn_data = []
  for model in models:
    model = model.lower()
    if model=='gmm':
      print('Generating GMM Data................')
      syn_data.append(gen_gmm(df_processed,discrete_cols,req_size,target_class,do_PCA))
      print()
    if model=='bn':
      print('Generating BN Data................')
      syn_data.append(gen_bn(df_processed,discrete_cols,req_size,target_class,do_PCA))
      print()
    if model=='ctgan':
      print('Generating CTGAN Data................')
      syn_data.append(gen_ctgan(df_processed,discrete_cols,req_size,target_class,do_PCA))
      print()
    if model=='pca':
      print('Generating PCA Data................')
      syn_data.append(gen_pca(df_processed,discrete_cols,req_size,target_class,do_PCA))
      print()
  print('--------------------------------------------------------------')
  return syn_data,table

def class_corrector(orig_data,gen_data,class_name):
    min_val = orig_data[class_name].min()
    max_val = orig_data[class_name].max()
    for i in range(len(gen_data)):
      if gen_data[class_name][i]<=min_val:
        gen_data[class_name][i] = int(min_val)
      elif gen_data[class_name][i]>=max_val:
        gen_data[class_name][i]  = int(max_val)
      else:
        gen_data[class_name][i]  = int(round(gen_data[class_name][i]))

    gen_data[class_name] = gen_data[class_name].fillna(0).astype(int)

def delete_duplicates(df):
	df = df.drop_duplicates()
	df = df.reset_index()
	df.drop('index',axis=1,inplace=True)

def preprocess_data(df,discrete_cols,target_class):
  disc_cols = discrete_cols.copy()
  if "Unnamed: 0.1" in df.columns.values:
    df.drop(["Unnamed: 0.1"], axis=1, inplace=True)
  uniqueValues = df.nunique()
  dropCols = []
  for i in range(len(uniqueValues)):
    if(uniqueValues[i] < 2):
      dropCols.append(i)

  for i in disc_cols:
    if df[i].nunique()<2:
      disc_cols.remove(i)

  df.drop(df.columns[dropCols], axis = 1, inplace = True)
  for i in df.columns:
    if i not in disc_cols:
      df[i].fillna((df[i].mean()), inplace=True)
    else:
      if is_numeric_dtype(df[i]):
        df[i].fillna(df[i].max()+1, inplace=True)
      else:
        df[i].fillna('null_value', inplace=True)

  for cl in disc_cols:
    if is_numeric_dtype(df[cl]):
      df[cl] = df[cl].astype(str,copy=False)

  for i in disc_cols:
    if df[i].nunique()<=2:
      disc_cols.remove(i)
  delete_duplicates(df)
  return df







