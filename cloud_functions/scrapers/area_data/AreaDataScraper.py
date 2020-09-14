import json
from google.cloud import storage
from google.cloud import bigquery
from google.api_core import retry

from area_data.utilities.tepco.TepcoAreaScraper import TepcoAreaScraper
from area_data.utilities.kepco.KepcoAreaScraper import KepcoAreaScraper


def selectUtility(utility):
    utilities = {
        "tepco": TepcoAreaScraper(),
        "kepco": KepcoAreaScraper()
    }
    return utilities.get(utility, None)


class AreaDataScraper:
    def __init__(self, utility):
        self.utility = utility
        self.scraper = selectUtility(utility)

    def scrape(self):
        print("Scraping AreaData for {}:".format(self.utility))
        df = self.scraper.get_dataframe()
        print(" - Got Data")
        print("Converting:")

        print("Sending:")
        self._upload_blob_to_storage(df)
        print(" - Sent to Cloud Storage")

        self._insert_into_bigquery(df)
        print(" - Sent to BigQuery")
        return f'Success!'

    def _upload_blob_to_storage(self, df):
        CS = storage.Client()
        BUCKET_NAME = 'scraper_data'
        BLOB_NAME = '{utility}_historical_data.csv'.format(
            utility=self.utility)

        """Uploads a file to the bucket."""
        bucket = CS.get_bucket(BUCKET_NAME)
        blob = bucket.blob(BLOB_NAME)

        blob.upload_from_string(self.scraper.convert_df_to_csv(df))

        print('Scraped Data Uploaded to {}.'.format(BLOB_NAME))

    def _insert_into_bigquery(self, df):
        BQ_DATASET = self.utility
        BQ_TABLE = 'historical_data_by_generation_type'

        table_id = BQ_DATASET + "." + BQ_TABLE

        df.to_gbq(table_id, if_exists="replace")


class BigQueryError(Exception):
    '''Exception raised whenever a BigQuery error happened'''

    def __init__(self, errors):
        super().__init__(self._format(errors))
        self.errors = errors

    def _format(self, errors):
        err = []
        for error in errors:
            err.extend(error['errors'])
        return json.dumps(err)
