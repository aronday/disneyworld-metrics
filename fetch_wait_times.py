import requests
import schedule
import time
from datetime import datetime
from urllib.parse import urlparse
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_series import MetricSeries

def fetch_and_submit(park_name, metric_type):
    urls = {
        "MagicKingdom": "https://api.themeparks.wiki/preview/parks/WaltDisneyWorldMagicKingdom/waittime",
        "Epcot": "https://api.themeparks.wiki/preview/parks/WaltDisneyWorldEpcot/waittime",
        "HollywoodStudios": "https://api.themeparks.wiki/preview/parks/WaltDisneyWorldHollywoodStudios/waittime",
        "AnimalKingdom": "https://api.themeparks.wiki/preview/parks/WaltDisneyWorldAnimalKingdom/waittime"
    }
    
    url = urls.get(park_name, None)
    if url:
        response = requests.get(url)
        if response.status_code == 200:
            attractions = response.json()
            if metric_type == 'wait_times':
                submit_wait_times_to_datadog(attractions, park_name)
            elif metric_type == 'status':
                submit_status_to_datadog(attractions, park_name)

def submit_wait_times_to_datadog(attractions, park_name):
    submit_to_datadog(attractions, park_name, metric_type='wait_times')

def submit_status_to_datadog(attractions, park_name):
    submit_to_datadog(attractions, park_name, metric_type='status')

def submit_to_datadog(attractions, park_name, metric_type):
    series = []
    for attraction in attractions:
        if metric_type == 'wait_times' and attraction['waitTime'] is not None:
            metric_name = "attraction.wait_time"
            value = attraction['waitTime']
        elif metric_type == 'status':
            metric_name = "attraction.status"
            value = 1 if attraction['status'] == "Operating" else 0
        else:
            continue

        tags = [
            f"name:{attraction['name']}",
            f"status:{attraction['status']}",
            f"type:{attraction['meta']['type']}",
            f"active:{'yes' if attraction['active'] else 'no'}",
            f"park:{park_name}"
        ]
        
        series.append(MetricSeries(
            metric=metric_name,
            type=MetricIntakeType.GAUGE if metric_type == 'status' else MetricIntakeType.COUNT,
            points=[MetricPoint(
                timestamp=int(datetime.now().timestamp()),
                value=value,
            )],
            tags=tags
        ))
    
    if series:
        body = MetricPayload(series=series)
        configuration = Configuration()
        with ApiClient(configuration) as api_client:
            api_instance = MetricsApi(api_client)
            response = api_instance.submit_metrics(body=body)
            print(f"Data submitted for {park_name} ({metric_type}): {response}")

def run_tasks():
    parks = ["MagicKingdom", "Epcot", "HollywoodStudios", "AnimalKingdom"]
    for park in parks:
        fetch_and_submit(park, 'wait_times')
        fetch_and_submit(park, 'status')

if __name__ == "__main__":
    schedule.every(1).minutes.do(run_tasks)

    while True:
        schedule.run_pending()
        time.sleep(1)
