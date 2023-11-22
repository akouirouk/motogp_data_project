from pydantic import Field, BaseModel, ConfigDict, validator

from typing import Optional, Annotated
from datetime import datetime, date
from decimal import Decimal


class MotoGpEvent(BaseModel):
    """Data schema for MotoGP events."""

    # do not allow other attributes
    model_config = ConfigDict(extra="forbid")

    id: str
    event_name: str
    sponsored_name: str
    circuit_name: str
    country_name: str
    country_iso: str
    place: str
    year: int = Field(ge=1949, le=2050)
    start_date: date
    end_date: Optional[date]
    test: bool
    status: str

    # validate date format
    @validator("start_date", "end_date", pre=True)
    def parse_date(cls, value: str) -> date:
        """Parse the date of the eventfrom string to datetime.date object

        Args:
            value (str): The date string

        Returns:
            date: Formatted date of birth
        """

        # if the date string value is NOT None
        if value:
            # reformat string date into YYYY-MM--DD format
            return datetime.strptime(value, "%Y-%m-%d").date()


class Rider(BaseModel):
    """Data schema for riders in the MotoGP championship."""

    id: str
    name: str
    nickname: str
    number: int
    team: str
    constructor: str
    category: str
    representing_country: str
    representing_country_iso: str = Field(max_length=2)
    birth_place: Optional[str]
    years_old: Optional[Annotated[Decimal, Field(max_digits=2)]]
    dob: Optional[date]

    # validate dob format
    @validator("dob", pre=True)
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
            return datetime.strptime(value, "%Y-%m-%d").date()


class Result(BaseModel):
    """Data schema for results from all classes in the MotoGP championship."""

    year: int
    event: str
    category: str
    session: str
    # results: dict
