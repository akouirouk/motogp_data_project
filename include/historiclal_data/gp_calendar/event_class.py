from pydantic import Field, BaseModel, validator

from datetime import datetime, date
from typing import Optional


class MotoGpEvent(BaseModel):
    """Pydantic Base Model for GP Riders."""

    gp: str
    track: str
    event_type: str
    start_date: date
    end_date: Optional[date]
    completed: int = Field(ge=0, le=1)

    # validate dob format
    @validator("start_date", "end_date", pre=True)
    def parse_dob(cls, value: str) -> date:
        """Parse the date of the eventfrom string to datetime.date object

        Args:
            value (str): The date string

        Returns:
            date: Formatted date of birth
        """

        # if the dob string value is NOT None
        if value:
            # reformat string date into YYYY-MM--DD format
            return datetime.strptime(value, "%d/%m/%Y").date()
