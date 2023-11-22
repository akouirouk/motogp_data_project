from pydantic import Field, BaseModel, ConfigDict, validator

from datetime import datetime, date
from typing import Optional


class MotoGpEvent(BaseModel):
    """Data schema for MotoGP events."""

    # do not allow other attributes
    model_config = ConfigDict(extra="forbid")

    event_id: str
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


class Riders(BaseModel):
    """Data schema for riders in the MotoGP championship."""

    # do not allow other attributes
    model_config = ConfigDict(extra="forbid")


class Result(BaseModel):
    """Data schema for results from all classes in the MotoGP championship."""

    year: int
    event: str
    category: str
    session: str
    # results: dict
