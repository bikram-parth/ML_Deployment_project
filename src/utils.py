import sys
import os
from src.exception import Custom_Exception
from src.logger import logging
import joblib
from sklearn.metrics import r2_score


def setup(file_path,object):
    try:
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok=True)
        joblib.dump(object,file_path)

    except Exception as e:
        raise Custom_Exception(e,sys)


def train(model,X_train_preprocessed,X_test_preprocessed,y_train,y_test):
    model_name=model()
    model_name.fit(X_train_preprocessed,y_train)
    y_pred=model_name.predict(X_test_preprocessed)

    return(
        model_name,
        r2_score(y_true=y_test,y_pred=y_pred)
    )

def get_first(dict):
    key=None
    value=None
    for keys in dict:
        key=keys
        value=dict[key]
        break
    return(key,value)
        

