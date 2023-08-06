# bqhus
[![Maintainability](https://api.codeclimate.com/v1/badges/102f4aceaa6a1c544f52/maintainability)](https://codeclimate.com/github/yokoe/bqhus/maintainability)

BigQuery helper utils for Python

## How to use
### Select from table
```
import bqhus
bqhus.select("SELECT * FROM `foo.bar.purchases` LIMIT 20").as_dicts()
bqhus.select("SELECT * FROM `foo.bar.purchases` ORDER BY created_at LIMIT 1", client=bigquery.Client(project="foobar")).first_as_dict()
bqhus.select("SELECT * FROM `foo.bar.purchases` LIMIT 20").to_dataframe()
```

### Create table from query
```
bqhus.select("SELECT * FROM `some.source.table`").to_table("foo.bar.new_table")
```

### Create temp table from query
```
bqhus.select("SELECT * FROM `some.source.table`").to_table("foo.bar.new_table").expires_in(days=7)
```

### Export table to GCS as csv
```
bqhus.export_table("foo.bar.sample").as_csv(gzip=True).to_gcs("my-bucket", "exported-table.csv.gz")
```


### Generate random table name
```
bqhus.random_table_name("prefix-here")
```

## Development
### Run tests
```
docker compose run bqhus
```
