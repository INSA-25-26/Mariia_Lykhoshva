from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    age: int = Field(ge=1, le=120, description="Age in years")
    workclass: str = Field(min_length=1, description="Work class")
    fnlwgt: int = Field(ge=1, description="Final weight")
    education: str = Field(min_length=1, description="Education level")
    education_num: int = Field(ge=0, alias="education.num", description="Education number of years")
    marital_status: str = Field(min_length=1, alias="marital.status", description="Marital status")
    occupation: str = Field(min_length=1, description="Occupation")
    relationship: str = Field(min_length=1, description="Relationship")
    race: str = Field(min_length=1, description="Race")
    sex: str = Field(min_length=1, description="Sex")
    capital_gain: int = Field(ge=0, alias="capital.gain", description="Capital gain")
    capital_loss: int = Field(ge=0, alias="capital.loss", description="Capital loss")
    hours_per_week: int = Field(ge=1, le=168, alias="hours.per.week", description="Hours worked per week")
    native_country: str = Field(min_length=1, alias="native.country", description="Native country")


class PredictionResponse(BaseModel):
    prediction: bool
    probability: float
