from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import numpy as np
import pandas as pd
from typing import Optional
from enum import Enum

# Initialize FastAPI app
app = FastAPI(
    title="Loan Prediction API",
    description="API for predicting loan approval status using machine learning",
    version="1.0.0"
)

# Load the trained model
try:
    model = joblib.load('loan_model.pkl')
except FileNotFoundError:
    raise Exception("Model file 'loan_model.pkl' not found. Please ensure the model is trained and saved.")

# Define enums for categorical fields
class GenderEnum(str, Enum):
    FEMALE = "Female"
    MALE = "Male"

class MaritalStatusEnum(str, Enum):
    NO = "No"
    YES = "Yes"

class EducationEnum(str, Enum):
    NOT_GRADUATE = "Not Graduate"
    GRADUATE = "Graduate"

class SelfEmployedEnum(str, Enum):
    NO = "No"
    YES = "Yes"

class PropertyAreaEnum(str, Enum):
    RURAL = "Rural"
    SEMIURBAN = "Semiurban"
    URBAN = "Urban"

class CreditHistoryEnum(str, Enum):
    NO = "No"
    YES = "Yes"

# Define the input data model
class LoanApplication(BaseModel):
    Gender: GenderEnum = Field(..., description="Gender")
    Married: MaritalStatusEnum = Field(..., description="Marital Status")
    Dependents: int = Field(..., description="Number of dependents (0, 1, 2, or 3+ as 4)", ge=0, le=4)
    Education: EducationEnum = Field(..., description="Education level")
    Self_Employed: SelfEmployedEnum = Field(..., description="Self Employment status")
    ApplicantIncome: float = Field(..., description="Applicant Income", gt=0)
    CoapplicantIncome: float = Field(0.0, description="Coapplicant Income", ge=0)
    LoanAmount: float = Field(..., description="Loan Amount", gt=0)
    Loan_Amount_Term: float = Field(..., description="Loan Amount Term in days", gt=0)
    Credit_History: CreditHistoryEnum = Field(..., description="Credit History")
    Property_Area: PropertyAreaEnum = Field(..., description="Property Area")

    model_config = {
        "json_schema_extra": {
            "example": {
                "Gender": "Male",
                "Married": "Yes",
                "Dependents": 1,
                "Education": "Graduate",
                "Self_Employed": "No",
                "ApplicantIncome": 5849.0,
                "CoapplicantIncome": 0.0,
                "LoanAmount": 146.0,
                "Loan_Amount_Term": 360.0,
                "Credit_History": "Yes",
                "Property_Area": "Semiurban"
            }
        }
    }

# Define the response model
class LoanPredictionResponse(BaseModel):
    loan_status: int = Field(..., description="Loan Status (0: Not Approved, 1: Approved)")
    loan_status_text: str = Field(..., description="Loan Status in text format")
    probability: float = Field(..., description="Probability of loan approval")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Loan Prediction API",
        "description": "Use /predict endpoint to predict loan approval status",
        "docs": "/docs"
    }

@app.post("/predict", response_model=LoanPredictionResponse)
async def predict_loan_status(loan_data: LoanApplication):
    """
    Predict loan approval status based on applicant information
    
    Returns:
    - loan_status: 0 (Not Approved) or 1 (Approved)
    - loan_status_text: Human readable loan status
    - probability: Probability of loan approval
    """
    try:
        # Convert categorical fields to numeric values
        def convert_categorical_to_numeric(loan_data: LoanApplication) -> dict:
            """Convert categorical fields to numeric values as expected by the model"""
            
            # Gender conversion
            gender_numeric = 1 if loan_data.Gender == GenderEnum.MALE else 0
            
            # Marital Status conversion
            married_numeric = 1 if loan_data.Married == MaritalStatusEnum.YES else 0
            
            # Education conversion
            education_numeric = 1 if loan_data.Education == EducationEnum.GRADUATE else 0
            
            # Self Employed conversion
            self_employed_numeric = 1 if loan_data.Self_Employed == SelfEmployedEnum.YES else 0
            
            # Credit History conversion
            credit_history_numeric = 1 if loan_data.Credit_History == CreditHistoryEnum.YES else 0
            
            # Property Area conversion
            property_area_mapping = {
                PropertyAreaEnum.RURAL: 0,
                PropertyAreaEnum.SEMIURBAN: 1,
                PropertyAreaEnum.URBAN: 2
            }
            property_area_numeric = property_area_mapping[loan_data.Property_Area]
            
            return {
                'Gender': gender_numeric,
                'Married': married_numeric,
                'Dependents': loan_data.Dependents,
                'Education': education_numeric,
                'Self_Employed': self_employed_numeric,
                'ApplicantIncome': loan_data.ApplicantIncome,
                'CoapplicantIncome': loan_data.CoapplicantIncome,
                'LoanAmount': loan_data.LoanAmount,
                'Loan_Amount_Term': loan_data.Loan_Amount_Term,
                'Credit_History': credit_history_numeric,
                'Property_Area': property_area_numeric
            }
        
        # Convert input data to numeric format
        numeric_data = convert_categorical_to_numeric(loan_data)
        
        # Create input array in the correct order
        feature_names = ['Gender', 'Married', 'Dependents', 'Education', 'Self_Employed', 
                        'ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 
                        'Loan_Amount_Term', 'Credit_History', 'Property_Area']
        
        input_data = np.array([[numeric_data[feature] for feature in feature_names]])
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        probability = model.predict_proba(input_data)[0][1]  # Probability of class 1 (approved)
        
        # Convert prediction to text
        loan_status_text = "Approved" if prediction == 1 else "Not Approved"
        
        return LoanPredictionResponse(
            loan_status=int(prediction),
            loan_status_text=loan_status_text,
            probability=float(probability)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": model is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)