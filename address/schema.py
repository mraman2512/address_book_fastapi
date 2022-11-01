from pydantic import BaseModel, Field


class Address(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    zipcode: int
    longitude: float = Field(gt=-180, lt=180)
    latitude: float = Field(gt=-90, lt=90)


class Retrive(BaseModel):
    radius: int
    longitude: float = Field(gt=-180, lt=180)
    latitude: float = Field(gt=-90, lt=90)
