from src.utils import logging
from src.exception import Custom_Exception
import sys
from dataclasses import dataclass
import os
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import AdaBoostRegressor,GradientBoostingRegressor
from src.utils import setup,train,get_first
from xgboost import XGBRegressor
from sklearn.metrics import r2_score

@dataclass
class model_trainer_ingest:
    model_file_path:str=os.path.join('artifacts/model.pkl')

class model_trainer_:
    def __init__(self):
        self.model_file_path_var=model_trainer_ingest()

    def initiate_model_trainer(self,X_train_preprocessed,X_test_preprocessed,y_train,y_test):
        try:
            best_model={}

            linear_model,linear_model_score=train(LinearRegression,X_train_preprocessed,X_test_preprocessed,y_train,y_test)

            best_model[linear_model]=linear_model_score

            knn_model,knn_model_score=train(KNeighborsRegressor,X_train_preprocessed,X_test_preprocessed,y_train,y_test)
            
            best_model[knn_model]=knn_model_score

            ada_model,ada_model_score=train(AdaBoostRegressor,X_train_preprocessed,X_test_preprocessed,y_train,y_test)
            
            best_model[ada_model]=ada_model_score

            grad_model,grad_model_score=train(GradientBoostingRegressor,X_train_preprocessed,X_test_preprocessed,y_train,y_test)
            
            best_model[grad_model]=grad_model_score

            X_g_model,Xg_model_score=train(XGBRegressor,X_train_preprocessed,X_test_preprocessed,y_train,y_test)
            
            best_model[X_g_model]=Xg_model_score

            sorted_dict = dict(sorted(best_model.items(), key=lambda x: x[1], reverse=True))

            model_object,model_r2_score=get_first(sorted_dict)

            setup(file_path=self.model_file_path_var.model_file_path,object=model_object)

            return(model_object,model_r2_score)
        
        except Exception as e:
            raise Custom_Exception(e,sys)





