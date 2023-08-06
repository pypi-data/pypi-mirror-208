pysyn-data Package
==================

This package is for generating synthetic data using 4 models i.e
Conditional Genrative Adveserial Networks(CTGAN), Gaussian Mixture Model
(GMM), Prinicipal Component Analysis (PCA) and Bayesian Network (BN). It
also informs the user which model will work best based on the input data
characterisitics.

Package Intallation
-------------------

For installing the pysyn-data package the following command has to be
run:

.. code:: bash

   pip install pysyn-data

Functions Usage
---------------

generate_data:
~~~~~~~~~~~~~~

::

   import pysyn_data as psd
   syn_data_list= psd.generate_data(df=data, discrete_cols=discrete_cols, models=['bn','ctgan','gmm','pca'],req_size=5000,target_class=target_class,do_PCA=False)

The above function generates synthetic data of size 5000 using the above
4 models i.e BN, CTGAN, GMM and PCA. It also takes input of discrete
columns if there are any in the input dataset. User has the option of
doing PCA before generating the required synthetic data

predict_best_models:
~~~~~~~~~~~~~~~~~~~~

::

   psd.predict_best_models(df=data,discrete_cols=discrete_cols)

This function shows user the best augmentation model which will work
according to the input data. The used metrics are number of discrete
columns to number of continuous columns ratio, number of features to
number of samples ratio, number of samples and number of features
individually.
