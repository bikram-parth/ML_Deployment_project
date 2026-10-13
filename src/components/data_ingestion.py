import os
import sys
from src.exception import Custom_Exception
from src.logger import logging
from dataclasses import dataclass
import pandas as pd

from sklearn.model_selection import train_test_split
from src.components.data_transformation import Data_transformation_config,Data_transformation

from src.components.model_trainer import model_trainer_ingest,model_trainer_

@dataclass
class DataIngestionConfig:
    raw_data_path:str=os.path.join('artifacts','data.csv')
    train_data_path:str=os.path.join('artifacts','train.csv')
    test_data_path:str=os.path.join('artifacts','test.csv')

class DataIngestion:
    def __init__(self):
        self.ingestion_config=DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info("Enter the data ingestion method or component")
        try:
            df=pd.read_csv('src/notebook/stud.csv')
            logging.info("Read the Dataset as DataFrame")

            os.makedirs('artifacts',exist_ok=True)
            df.to_csv(self.ingestion_config.raw_data_path,index=False,header=True)


            train_set,test_set=train_test_split(df,test_size=0.20,random_state=42)

            train_set.to_csv(self.ingestion_config.train_data_path,index=False,header=True)

            test_set.to_csv(self.ingestion_config.test_data_path,index=False,header=True)

            logging.info("Ingestion of the data is complete")

            return(
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
            )
        except Exception as e:
            raise Custom_Exception(e,sys)

if __name__=='__main__':
    obj=DataIngestion()
    train_set,test_set=obj.initiate_data_ingestion()

    transformation_obj=Data_transformation()
    X_train_preprocessed,X_test_preprocessed,y_train,y_test,_=transformation_obj.initiate_datatransformation(train_set,test_set)

    model_trainer_object=model_trainer_()
    model_object,model_score=model_trainer_object.initiate_model_trainer(X_train_preprocessed,X_test_preprocessed,y_train,y_test)


