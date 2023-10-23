from airflow.decorators import dag, task
from datetime import datetime

# run data pipeline the day after every race weekend


# create the dag object
@dag(
    start_date=datetime(2023, 10, 30),
    schedule="@weekly",
    description="Scrape MotoGP webpages to update MySQL table.",
    tags=["motogp"],
)
def my_dag():
    pass
