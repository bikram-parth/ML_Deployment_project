import os
from src.logger import logging
from src.exception import Custom_Exception
import sys
import pandas as pd
import seaborn as sns
import numpy as np
from dataclasses import dataclass
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder,OneHotEncoder,StandardScaler,OrdinalEncoder
from sklearn.impute import SimpleImputer
from src.utils import setup

@dataclass
class Data_transformation_config:
    preprocessor_file_path:str=os.path.join('artifacts/preprocessor.pkl')

class Data_transformation:
    def __init__(self):
        self.preprocessor_file_path_var=Data_transformation_config()

    def datatransformation_object(self):
        try:
            logging.info("Started Synthesing the preprocessor object")

            numerical_col=['reading_score','writing_score']
            cat_col=['gender','race_ethnicity','parental_level_of_education','lunch','test_preparation_course']

            logging.info(f"Numerical _col : {numerical_col}")
            logging.info(f"Categorical_col : {cat_col}")

            numerical_pipeline=Pipeline(steps=[
            ('simpleimputer',SimpleImputer(strategy='median')),
            ('standard_Scalar',StandardScaler())   
            ])

            categorical_pipeline=Pipeline([
            ('simpleimputer',SimpleImputer(strategy='most_frequent')),
            ('one_hot',OneHotEncoder(handle_unknown='ignore')),
            ])

            preprocessor=ColumnTransformer(transformers=[
            ('numerical',numerical_pipeline,numerical_col),
            ('cat_',categorical_pipeline,cat_col)
            ])

            return preprocessor
        
        except Exception as e:
            raise Custom_Exception(e,sys)
        
    def initiate_datatransformation(self,train_path,test_path):
        try:
            logging.info("Entered The initiate_datatransformation_phase")
            train_data=pd.read_csv(train_path)
            test_data=pd.read_csv(test_path)

            logging.info("Succesfully fetched the training and testing data")

            preprocessor_object=self.datatransformation_object()

            X_train=train_data.drop(columns=['math_score'])
            y_train=train_data['math_score']

            X_test=test_data.drop(columns=['math_score'])
            y_test=test_data['math_score']


            X_train_preprocessed=preprocessor_object.fit_transform(X_train)
            X_test_preprocessed=preprocessor_object.transform(X_test)

            setup(self.preprocessor_file_path_var.preprocessor_file_path,preprocessor_object)

            return(
                X_train_preprocessed,
                X_test_preprocessed,
                y_train,
                y_test,
                self.preprocessor_file_path_var.preprocessor_file_path
            )

        except Exception as e:
            raise Custom_Exception(e,sys)