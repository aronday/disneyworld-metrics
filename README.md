# Disney World Wait Time Metrics

This Dockerized Python application is designed to fetch real-time wait times for attractions across Walt Disney World parks and submit this data to Datadog for analysis and monitoring. It supports tracking for Magic Kingdom, Epcot, Hollywood Studios, and Animal Kingdom, making it an invaluable tool for both personal trip planning and broader data analysis on Disney park trends.

## Features
- Real-time Data Fetching: Gathers current wait times for attractions directly from the official Walt Disney World API.
- Datadog Integration: Submits fetched data as custom metrics to Datadog, facilitating comprehensive monitoring and analysis.
- Support for Multiple Parks: Includes support for all four major Walt Disney World parks.
- Containerized Application: Packaged as a Docker container for ease of deployment and scalability.

## Getting Started
To use this container, you'll need Docker installed on your system:

- [Windows](https://docs.docker.com/windows/started)
- [OS X](https://docs.docker.com/mac/started/)
- [Linux](https://docs.docker.com/linux/started/)

### Usage

#### Running the Container

To run this container, you'll need to provide your Datadog API and APP keys as environment variables:

```shell
docker run -e DD_API_KEY='<Your_Datadog_API_Key>' -e DD_APP_KEY='<Your_Datadog_APP_Key>' dayaron/disneyworld-metrics-datadog:latest
```

#### Configuration

Environment Variables

* `DD_API_KEY` - Specifies your Datadog API key.
* `DD_APP_KEY` - Specifies your Datadog Application key.

## Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.


Please refer to the CONTRIBUTING.md for more information.

## Authors
Aron Day - Initial work
See also the list of contributors who participated in this project.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.