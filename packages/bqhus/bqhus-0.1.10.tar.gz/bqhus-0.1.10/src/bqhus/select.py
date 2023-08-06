from google.cloud import bigquery
from jinja2 import Template, Environment, FileSystemLoader
from .create_table import create_table
import google.cloud.bigquery


class SelectTask:
    def __init__(self, client, query):
        self.client = client
        self.query = query
        self.query_parameters = []

    def params(self, params):
        self.query_parameters = params
        return self

    def int64_param(self, key: str, value: int):
        if self.query_parameters is None:
            self.query_parameters = []

        self.query_parameters.append(
            bigquery.ScalarQueryParameter(key, "INT64", value),
        )
        return self

    def str_param(self, key: str, value: str):
        if self.query_parameters is None:
            self.query_parameters = []

        self.query_parameters.append(
            bigquery.ScalarQueryParameter(key, "STRING", value),
        )
        return self

    def bq_client(self):
        return self.client if self.client is not None else bigquery.Client()

    def job(self):
        job_config = bigquery.QueryJobConfig(query_parameters=self.query_parameters)
        return self.bq_client().query(self.query, job_config=job_config)

    def as_dicts(self):
        query_job = self.job()
        return [dict(row) for row in query_job]

    def first_as_dict(self):
        return self.as_dicts()[0]

    def to_table(self, table_id, overwrite=False):
        return create_table(
            table_id,
            self.query,
            self.query_parameters,
            overwrite=overwrite,
            client=self.client,
        )

    def to_dataframe(self):
        return self.job().to_dataframe()


def select(
    query: str,
    query_parameters=None,
    client: google.cloud.bigquery.Client = None,
):
    return SelectTask(client=client, query=query).params([] if query_parameters is None else query_parameters)


def select_with_template(
    template_dir: str, template_name: str, template_parameters={}, client=None
):
    env = Environment(loader=FileSystemLoader(template_dir, encoding="utf8"))
    tmpl = env.get_template(template_name)
    query = tmpl.render(template_parameters)

    return select(query=query, query_parameters=[], client=client)
