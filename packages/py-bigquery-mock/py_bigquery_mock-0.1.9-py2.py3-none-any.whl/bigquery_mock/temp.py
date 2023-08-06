from google.cloud import bigquery

schema = [
    bigquery.SchemaField("full_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("age", "INTEGER", mode="REQUIRED"),
]
table_id = 'sbgtv-data-platform-dev.stage.test_create'
project = 'sbgtv-data-platform-dev'
client = bigquery.Client(project = project )
#client.delete_table(table_id, not_found_ok=True)  # Make an API request.
#print("Deleted table '{}'.".format(table_id))

table = bigquery.Table(table_id, schema=schema)
print(type(table))
table = client.create_table(table)  # Make an API request.
print(type(table))
print(
    "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
)
