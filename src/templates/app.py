import pandas as pd
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import joblib
from fastapi import FastAPI 
from pydantic import Field,BaseModel
from typing import Literal
from pathlib import Path

app=FastAPI()
BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "artifacts" / "model.pkl"

BASE_DIR = Path(__file__).resolve().parents[2]
preprocessor_PATH = BASE_DIR / "artifacts" / "preprocessor.pkl"

preprocessor=joblib.load(preprocessor_PATH)
best_model = joblib.load(MODEL_PATH)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class prediction_math_score(BaseModel):
    math_score:float

class Student_Data(BaseModel):

    gender:Literal['female','male']
    race_ethnicity:Literal['group B', 'group C', 'group A', 'group D', 'group E']
    parental_level_of_education:Literal[ "bachelor's degree","some college","master's degree","associate's degree","high school",  "some high school"]
    lunch:Literal['standard', 'free/reduced']
    test_preparation_course:Literal['none', 'completed']
    reading_score:int=Field(ge=0,le=100)
    writing_score:int=Field(ge=0,le=100)

@app.get('/')
def welcome():
    print("Welcome to Student's math score predictor")

@app.post('/predict')
def predict(data:Student_Data):

    input_row=pd.DataFrame([{
        "gender":data.gender,
        "race_ethnicity":data.race_ethnicity,
        "parental_level_of_education":data.parental_level_of_education,
        "lunch":data.lunch,
        "test_preparation_course":data.test_preparation_course,
        "reading_score":data.reading_score,
        "writing_score":data.writing_score
    }])

    input_df_preprocessed=preprocessor.transform(input_row)
    prediction=best_model.predict(input_df_preprocessed)

    return prediction_math_score(
        math_score=float(prediction[0])
    )
