from google.cloud import bigquery
from google.cloud.bigquery import retry as r
from google.cloud.bigquery import enums
from google.api_core.exceptions import AlreadyExists, Conflict

from .constants import FileFormat
from datetime import datetime, timedelta
from . import _functions as fn
import hashlib
import logging as log


class Client(bigquery.Client):
    __PROJECT = 'pfsdb3'
    __CACHE_DATASET = 'cached'
    __BUCKET_NAME = 'bigquery_1'
    __CACHE_TABLE = 'system.gcs_cache'

    def __init__(self):
        super(Client, self).__init__()

    def query(self,
              query: str,
              job_config=None,
              job_id: str = None,
              job_id_prefix: str = None,
              location: str = None,
              project: str = None,
              retry=r.DEFAULT_RETRY,
              timeout=r.DEFAULT_TIMEOUT,
              job_retry=r.DEFAULT_JOB_RETRY,
              api_method=enums.QueryApiMethod.QUERY) -> bigquery.QueryJob:

        dry_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        dry_run = super(Client, self).query(query, dry_config, job_id, job_id_prefix, location, project, retry, timeout, job_retry, api_method)
        vol = int(dry_run.total_bytes_processed)
        # if vol > self.single_query_limit:
        #     raise exceptions.VolumeLimitException()
        self.__write_usage_log(vol)
        return super(Client, self).query(query, job_config, job_id, job_id_prefix, location, project, retry, timeout, job_retry, api_method)

    def fetch(self, query, job_config=None, job_id=None, job_id_prefix=None, location=None, project=None, retry=r.DEFAULT_RETRY, timeout=r.DEFAULT_TIMEOUT, job_retry=r.DEFAULT_JOB_RETRY, api_method=enums.QueryApiMethod.QUERY):
        return self.query(query, job_config, job_id, job_id_prefix, location, project, retry, timeout, job_retry, api_method).result().to_dataframe()

    def build_temp_table(self):
        """
        making a table in the cached dataset
        :return: table
        """
        random_string = fn.get_random_string(8)
        ok = False
        table = None
        while not ok:
            try:
                table = self.create_table(f'{self.__PROJECT}.{self.__CACHE_DATASET}.{random_string}')
                ok = True
            except Conflict:
                random_string += fn.get_random_string(1)
        return table

    def query_to_cached_dataset(self, query: str, destination: bigquery.Table):

        config = bigquery.QueryJobConfig(allow_large_results=True)
        config.destination = destination
        config.write_disposition = bigquery.WriteDisposition().WRITE_TRUNCATE

        query_result = self.query(query, job_config=config, api_method=enums.QueryApiMethod.INSERT)
        return query_result.result()

    def export_to_gcs(self, table: bigquery.Table, name: str, destination_format=FileFormat.CSV):
        try:
            destination_uri = f"gs://{self.__BUCKET_NAME}/{table.table_id}/{name}_*.{FileFormat.to_extension(destination_format)}"
        except KeyError:
            destination_uri = f"gs://{self.__BUCKET_NAME}/{table.table_id}/{name}_*"
        dataset_ref = bigquery.DatasetReference(self.__PROJECT, self.__CACHE_DATASET)
        table_ref = dataset_ref.table(table.table_id)
        try:
            job_config = bigquery.job.ExtractJobConfig()
            job_config.destination_format = FileFormat.to_format(destination_format)
        except KeyError:
            raise TypeError('The destination format is not supported')
        extract_job = self.extract_table(
            table_ref,
            destination_uri,
            job_config=job_config
            # Location must match that of the source table.
            # location="US",
        )  # API request
        res = extract_job.result()  # Waits for job to complete.
        return res

    def cache_query(self,
                    query: str,
                    name: str = None,
                    destination_format: str or FileFormat = FileFormat.CSV,
                    days: int = 7,
                    ignore_hit: bool = False):
        """
            Cache a query result in Google Cloud Storage (GCS)
            :param query: query to run on bigquery and cache in GCS
            :param name: name of the file to store in GCS
            :param destination_format: format of the file to store in GCS
            :param days: days to keep the file in GCS
            :param ignore_hit: ignore cache hit and run the query again
        """
        if name is None:
            name = fn.get_random_string(10)

        query = query.replace('\n', ' ')
        query = query.strip()
        hashed_query = hashlib.sha1(query.encode('utf-8')).hexdigest()
        if days <= 0:
            days = 365

        # check for the hit
        row = None
        if not ignore_hit:
            cached = self.query('SELECT * from `pfsdb3.system.gcs_cache` WHERE status_code != -1').result().to_dataframe()
            if len(cached) > 0:
                cached = cached.where(cached['hash'] == hashed_query).dropna().sort_values(by=['created_at'],
                                                                                           ascending=False)
                if len(cached) > 0:
                    row = cached.iloc[0].to_dict()
        if row is not None:
            # Hit happened
            row['hit'] = True
            return row

        # Miss happened
        table = self.build_temp_table()
        log.debug(f'Created table {table.table_id} in {self.__CACHE_DATASET}')

        qresult = self.query_to_cached_dataset(query=query, destination=table)
        log.debug(f'Insert query {query} to {table.table_id}')

        destination_format = destination_format.upper()
        try:
            destination_format = FileFormat.to_format(destination_format)
        except KeyError:
            raise TypeError('The destination format is not supported')

        res = self.export_to_gcs(table, name, destination_format)
        log.debug(f'Export {table.table_id} to GCS(/{table.table_id}/{name}_*.{destination_format})')

        try:
            row = {
                'name': name,
                'folder': table.table_id,
                'uri': res.destination_uris[0],
                'length': res.destination_uri_file_counts[0],
                'created_at': datetime.now().isoformat(),
                'expired_at': (datetime.now() + timedelta(days=days)).isoformat(),
                'query': query,
                'hash': hashed_query,
                'total_rows': qresult.total_rows,
                'status_code': 1
            }
            info = self.insert_rows_json(self.__CACHE_TABLE, [row])
            if len(info) > 0 and len(info[0]['errors']) != 0:
                log.error(info[0]['errors'])
        except Exception as e:
            log.error(e)

        self.delete_table(table)
        log.debug(f'Deleted table {table.table_id} from {self.__CACHE_DATASET}')

        row['hit'] = False
        return row

    def __write_usage_log(self, vol):
        try:
            with open(self.__usage_log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now()}: {vol} bytes\n")
                return True
        except Exception as e:
            return False

    @property
    def __usage_log_file(self):
        return '.usage_log'

    @property
    def single_query_limit(self):
        return 3 * 10 ** 12