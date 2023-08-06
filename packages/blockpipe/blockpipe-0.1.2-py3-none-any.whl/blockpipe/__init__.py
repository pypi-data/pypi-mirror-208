import requests


BASE_URL = 'https://app.blockpipe.io/endpoint'


class Client:
    def __init__(self, project, environment='production', base_url=BASE_URL):
        self.project = project
        self.environment = environment
        self.base_url = base_url

    def get(self, endpoints):
        if isinstance(endpoints, str):
            endpoints = [endpoints]

        results = []
        for endpoint in endpoints:
            url = f'{self.base_url}/{self.project}/{self.environment}{endpoint}'
            response = requests.get(url)
            response.raise_for_status()
            results.append(response.json())

        if len(results) == 1:
            return results[0]
        return results


__all__ = ['Client']
