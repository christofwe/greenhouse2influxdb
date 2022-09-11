import os
import json
import requests
from requests.auth import HTTPBasicAuth

import time
from datetime import datetime, timedelta
import pytz

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUXDB_URL = os.environ['INFLUXDB_URL']
INFLUXDB_TOKEN = os.environ['INFLUXDB_TOKEN']
INFLUXDB_ORG = os.environ['INFLUXDB_ORG']
INFLUXDB_BUCKET = os.environ['INFLUXDB_BUCKET']
GREENHOUSE_API_IP = os.environ['GREENHOUSE_API_IP']


tz = pytz.timezone(os.environ['TZ'])
local = tz.localize(datetime.now())
timestamp = local.strftime("%Y-%m-%dT%H:%M:%S%Z%z")

influx_client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL,token=INFLUXDB_TOKEN,org=INFLUXDB_ORG)
influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)

greenhouse_api_base_url = f"http://{GREENHOUSE_API_IP}/json"

try:
  greenhouse_response = requests.get(f"{greenhouse_api_base_url}")
  greenhouse_response.raise_for_status()
  greenhouse_metrics = json.loads(greenhouse_response.text)

  timestamp_status = tz.localize(datetime.fromisoformat(greenhouse_metrics['Timestamp']))

  p = influxdb_client.Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
  influx_write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=p)

except requests.exceptions.HTTPError as error:
  print(f"greenhouse_metrics error: {error}")
  print(f"greenhouse_metrics status_code: {greenhouse_metrics.status_code}")
