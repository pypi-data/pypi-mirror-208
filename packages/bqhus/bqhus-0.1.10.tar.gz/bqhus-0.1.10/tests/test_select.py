import unittest
import bqhus
from dotenv import load_dotenv

load_dotenv()


class TestSelect(unittest.TestCase):
    def test_select_with_no_params(self):
        query = "SELECT 1"
        task = bqhus.select(query)
        self.assertEqual(query, task.query)

    def test_select(self):
        query = "SELECT word FROM `bigquery-public-data.samples.shakespeare` order by rand() limit 5"
        words = bqhus.select(query).as_dicts()
        self.assertEqual(len(words), 5)

    def test_select_with_template(self):
        words = (
            bqhus.select_with_template("./tests/templates", "shakespeare.j2")
            .int64_param("max_count", 3)
            .as_dicts()
        )
        self.assertEqual(len(words), 3)

    def test_select_to_dataframe(self):
        query = "SELECT word FROM `bigquery-public-data.samples.shakespeare` order by rand() limit 5"
        df = bqhus.select(query).to_dataframe()
        self.assertEqual(len(df.index), 5)

    def test_select_int64_param(self):
        query = "SELECT word FROM `bigquery-public-data.samples.shakespeare` order by rand() limit @max_count"
        select_task = bqhus.select(query)
        self.assertEqual(len(select_task.query_parameters), 0)
        select_task.int64_param("max_count", 5)
        self.assertEqual(len(select_task.query_parameters), 1)

    def test_select_params(self):
        query = "SELECT word FROM `bigquery-public-data.samples.shakespeare` order by rand() limit @max_count"
        task1 = bqhus.select(query).int64_param("max_count", 1)
        self.assertEqual(len(task1.query_parameters), 1)

        task2 = bqhus.select(query).int64_param("max_count", 2)
        self.assertEqual(len(task2.query_parameters), 1)




if __name__ == "__main__":
    unittest.main()
