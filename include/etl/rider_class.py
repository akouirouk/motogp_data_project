from pydantic import Field, BaseModel, validator, PositiveInt

from datetime import datetime, date
from typing import Optional


class Rider(BaseModel):
    """Pydantic Base Model for GP Riders."""

    rider_name: str
    hero_hashtag: str
    race_number: PositiveInt = Field(ge=0, le=99)
    team: Optional[str]
    bike: Optional[str]
    representing_country: str = Field(max_length=2)
    place_of_birth: Optional[str]
    date_of_birth: Optional[date]
    height: Optional[PositiveInt] = Field(ge=152, le=200)
    weight: Optional[PositiveInt] = Field(ge=40, le=115)

    # validate dob format
    @validator("date_of_birth", pre=True)
    def parse_dob(cls, value: str) -> date:
        """Parse the Date of Birth of the rider from string to datetime.date object

        Args:
            value (str): The date string

        Returns:
            date: Formatted date of birth
        """

        # if the dob string value is NOT None
        if value:
            # reformat string date into YYYY-MM--DD format
            return datetime.strptime(value, "%d/%m/%Y").date()
