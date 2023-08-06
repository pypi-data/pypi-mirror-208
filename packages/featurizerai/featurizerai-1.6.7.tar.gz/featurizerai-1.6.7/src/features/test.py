import datetime

import features
import json
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer

from materialize import materialize
from custom_schema import custom_schema
from fastapi.middleware.cors import CORSMiddleware
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
import os
import sys
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ca = certifi.where()

featurizer_connection = {
    'uri': "mongodb+srv://admin:6lHqq9LqgwDlninK@cluster0.aqtcyq2.mongodb.net/?retryWrites=true&w=majority",
    'database': 'featurizer',
}

def fetch_data_sources(data_source_ids: list) -> dict:
    client = MongoClient(featurizer_connection['uri'], server_api=ServerApi('1'), tlsCAFile=ca)
    db = client[featurizer_connection['database']]
    collection = db['data_sources']

    data_sources = {}
    for data_source_id in data_source_ids:
        data_source = collection.find_one({"id": data_source_id})
        if data_source:
            data_sources[data_source_id] = data_source
        else:
            raise HTTPException(status_code=400, detail={"Result": f"No data source found for the ID {data_source_id}"})
    return data_sources

def fetch_feature_set(stream_id: str) -> dict:
    client = MongoClient(featurizer_connection['uri'], server_api=ServerApi('1'), tlsCAFile=ca)
    db = client[featurizer_connection['database']]
    collection = db['feature_sets']
    featureset = collection.find_one({"id": stream_id})

    if featureset:
        # Fetch data sources from MongoDB
        data_source_ids = [featureset["stream_data_source"], featureset["aggregated_data_source"]]
        data_sources = fetch_data_sources(data_source_ids)

        stream_data_source = data_sources[featureset["stream_data_source"]]['connection_string']
        aggregated_data_source = data_sources[featureset["aggregated_data_source"]]['connection_string']

        result = {
            "id": featureset["id"],
            "input_schema": featureset["input_schema"],
            "stream_data_source": stream_data_source,
            "aggregated_data_source": aggregated_data_source,
            "aggregation_key": featureset["aggregation_key"],
            "loopback_date": featureset["loopback_date"],
            "timestamp_field_name": featureset["timestamp_field_name"],
            "aggregation_days_and_hours": featureset["aggregation_days_and_hours"],
            "created_at": featureset["created_at"]
        }
        return result
    else:
        raise HTTPException(status_code=400, detail={"Result": "No feature-set found for the given stream_id"})

def generate_select_clause(json_object, aggregation_key, count_suffix):
    select_clause = []
    for column in json_object:
        if column.name != aggregation_key and column.name != "timestamp":
            aggregation = column.metadata.get("aggregation", None)
            if aggregation == "count":
                select_clause.append(f'COUNT({column.name}) AS {column.name}{count_suffix}')
            elif aggregation == "sum":
                select_clause.append(f'SUM({column.name}) AS {column.name}{count_suffix}')
            elif aggregation == "avg":
                select_clause.append(f'AVG({column.name}) AS {column.name}{count_suffix}')
            elif aggregation == "min":
                select_clause.append(f'MIN({column.name}) AS {column.name}{count_suffix}')
            elif aggregation == "max":
                select_clause.append(f'MAX({column.name}) AS {column.name}{count_suffix}')
            else:
                select_clause.append(f'{column.name}')
    return ', '.join(select_clause)

@app.post('/materialize/{stream_id}')
def aggregate(json_data: dict, stream_id: str, token: str = Depends(oauth2_scheme)):
    featureset = fetch_feature_set(stream_id)
    print(featureset)

    json_string_fixed = f'[{featureset["input_schema"]}]'
    json_string_fixed = json_string_fixed.replace('}{', '},{')
    json_object = json.loads(json_string_fixed)
    input_scheme = custom_schema(json_object)

    try:
        # Define the dynamic Spark SQL queries to be executed
        aggregation_days_and_hours = featureset["aggregation_days_and_hours"]

        sparksql = []
        aggregation_key = featureset["aggregation_key"]
        loopback_str = json_data.get('loopback')
        loopback_date = datetime.datetime.strptime(loopback_str,
                                                   "%Y-%m-%d %H:%M:%S")  # Assuming the format of loopback_str is YYYY-MM-DD HH:MM:SS
        loopback_timestamp = int(loopback_date.timestamp())
        aggregation_key_value = json_data.get('aggregation_key_value')

        for days_and_hours in aggregation_days_and_hours:
            duration, unit = days_and_hours[:-1], days_and_hours[-1]
            unit_in_seconds = 86400 if unit == "D" else 3600  # 86400 seconds in a day, 3600 seconds in an hour
            count_suffix = f"_last_{duration.lower()}_{unit.lower()}"

            # Generate the SELECT clause using input_schema columns
            select_clause = generate_select_clause(input_scheme.schema.fields, aggregation_key, count_suffix)

            sql = f"SELECT {select_clause}, {aggregation_key} FROM temp_table WHERE {aggregation_key}='{aggregation_key_value}' AND timestamp_unix > {loopback_timestamp} - {int(duration) * unit_in_seconds} and timestamp_unix < {loopback_timestamp} GROUP BY {aggregation_key}"
            print(sql)
            sparksql.append(sql)

        print(sparksql)
        print(featureset['aggregated_data_source'])
        materialize_instance = materialize(featureset['aggregated_data_source'], loopback_str, aggregation_key,
                                           aggregation_key_value, token, input_scheme.schema, sparksql,
                                           partition_column=aggregation_key)

        aggregated_data_str = materialize_instance.read_data_and_aggregate()
        aggregated_data = json.loads(aggregated_data_str)

        return aggregated_data

    except Exception as e:
        raise HTTPException(status_code=400, detail={"Result": "No data found", "error": str(e)})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)


