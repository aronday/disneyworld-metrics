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
import logging
from logging.config import dictConfig
from pythonjsonlogger import jsonlogger

# Setup JSON logging
dictConfig({
    'version': 1,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'fmt': '%(asctime)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        }
    },
    'loggers': {
        'RideLogger': {
            'handlers': ['console'],
            'level': logging.INFO,
        }
    }
})

logger = logging.getLogger('RideLogger')

# Keep track of the last status to identify changes
ride_previous_status = {}

def fetch_and_submit(park_name, metric_type):
    urls = {
        "MagicKingdom": "https://api.themeparks.wiki/preview/parks/WaltDisneyWorldMagicKingdom/waittime",
        "Epcot": "https://api.themeparks.wiki/preview/parks/WaltDisneyWorldEpcot/waittime",
        "HollywoodStudios": "https://api.themeparks.wiki/preview/parks/WaltDisneyWorldHollywoodStudios/waittime",
        "AnimalKingdom": "https://api.themeparks.wiki/preview/parks/WaltDisneyWorldAnimalKingdom/waittime"
    }
    
    url = urls.get(park_name, None)
    if url:
        logger.info({
            'message': f"Attempting to fetch data for {park_name} ({metric_type})",
            'park_name': park_name,
            'metric_type': metric_type,
            'action': 'fetch_attempt'
        })
        
        response = requests.get(url)
        
        if response.status_code == 200:
            logger.info({
                'message': f"Successfully fetched data for {park_name} ({metric_type})",
                'park_name': park_name,
                'metric_type': metric_type,
                'action': 'fetch_success',
                'response_status': response.status_code
            })
            attractions = response.json()
            if metric_type == 'wait_times':
                submit_wait_times_to_datadog(attractions, park_name)
            elif metric_type == 'status':
                submit_status_to_datadog(attractions, park_name)
        else:
            logger.error({
                'message': f"Failed to fetch data for {park_name} ({metric_type})",
                'park_name': park_name,
                'metric_type': metric_type,
                'action': 'fetch_failure',
                'response_status': response.status_code
            })

def submit_wait_times_to_datadog(attractions, park_name):
    submit_to_datadog(attractions, park_name, metric_type='wait_times')

def submit_status_to_datadog(attractions, park_name):
    submit_to_datadog(attractions, park_name, metric_type='status')

def submit_to_datadog(attractions, park_name, metric_type):
    series = []
    for attraction in attractions:
        attraction_id = attraction.get('id', attraction['name'])  # Unique identifier for each attraction
        attraction_type = attraction['meta']['type'] if 'meta' in attraction and 'type' in attraction['meta'] else 'unknown'
        if metric_type == 'wait_times' and attraction['waitTime'] is not None:
            metric_name = "attraction.wait_time"
            value = attraction['waitTime']
        elif metric_type == 'status':
            metric_name = "attraction.status"
            value = 1 if attraction['status'] == "Operating" else 0
            
            # Additional logic for logging status changes
            current_status = attraction['status']
            previous_info = ride_previous_status.get(attraction_id, {})
            previous_status = previous_info.get('status')
            last_change = previous_info.get('last_change', datetime.now())
            
            if current_status != previous_status:
                duration_since_last_change = datetime.now() - last_change
                logger.info({
                    'ride_id': attraction_id,
                    'park_name': park_name,
                    'attraction_name': attraction['name'],
                    'previous_status': previous_status,
                    'current_status': current_status,
                    'attraction_type': attraction_type,
                    'duration_since_last_change_seconds': duration_since_last_change.total_seconds(),
                    'message': f"Status changed for {attraction['name']} ({attraction_type}) in {park_name}: {previous_status} -> {current_status}"
                })
                
                # Update the last change time and status
                ride_previous_status[attraction_id] = {
                    'status': current_status, 
                    'last_change': datetime.now(),
                    'type': attraction_type
                }
        else:
            continue

        tags = [
            f"name:{attraction['name']}",
            f"status:{attraction['status']}",
            f"type:{attraction_type}",
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
