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

def fetch_and_submit():
    urls = [
        "https://api.themeparks.wiki/preview/parks/WaltDisneyWorldMagicKingdom/waittime",
        "https://api.themeparks.wiki/preview/parks/WaltDisneyWorldEpcot/waittime",
        "https://api.themeparks.wiki/preview/parks/WaltDisneyWorldHollywoodStudios/waittime",
        "https://api.themeparks.wiki/preview/parks/WaltDisneyWorldAnimalKingdom/waittime"
    ]

    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            attractions = response.json()
            park_name = urlparse(url).path.split("/")[-2].replace("WaltDisneyWorld", "")
            submit_to_datadog(attractions, park_name)

def submit_to_datadog(attractions, park_name):
    series = []
    for attraction in attractions:
        # Skip the attraction if waitTime is None
        if attraction['waitTime'] is None:
            continue
        
        metric_name = "attraction.wait_time"
        tags = [
            f"name:{attraction['name']}",
            f"status:{attraction['status']}",
            f"type:{attraction['meta']['type']}",
            f"active:{'yes' if attraction['active'] else 'no'}",
            f"park:{park_name}"
        ]
        
        series.append(MetricSeries(
            metric=metric_name,
            type=MetricIntakeType.GAUGE,
            points=[MetricPoint(
                timestamp=int(datetime.now().timestamp()),
                value=attraction['waitTime'],
            )],
            tags=tags
        ))
    
    if series:
        body = MetricPayload(series=series)
        configuration = Configuration()
        with ApiClient(configuration) as api_client:
            api_instance = MetricsApi(api_client)
            response = api_instance.submit_metrics(body=body)
            print(f"Data submitted for {park_name}: {response}")

if __name__ == "__main__":
    schedule.every(1).minutes.do(fetch_and_submit)

    while True:
        schedule.run_pending()
        time.sleep(1)
