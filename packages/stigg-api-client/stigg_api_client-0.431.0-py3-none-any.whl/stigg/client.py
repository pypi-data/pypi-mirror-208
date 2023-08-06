from sgqlc.endpoint.requests import RequestsEndpoint
from sgqlc.operation import Operation

from stigg.generated.operations import Operations


class StiggClient:
    def __init__(self, endpoint: RequestsEndpoint):
        self._endpoint: RequestsEndpoint = endpoint

    def request(self, operation: Operation, variables: dict, raw_response=False):
        data = self._endpoint(operation, variables)
        if raw_response:
            return data

        # clean up data to so an exepction will be raised
        errors = data.get('errors')
        if errors:
            data.pop('data')

        # interpret results into native Python objects
        return operation + data


class Stigg(Operations):
    @staticmethod
    def create_client(api_key: str,
                      api_url: str = 'https://api.stigg.io/graphql',
                      request_timeout=30) -> StiggClient:
        headers = {'X-API-KEY': f'{api_key}'}
        endpoint = RequestsEndpoint(url=api_url,
                                    base_headers=headers,
                                    timeout=request_timeout)
        return StiggClient(endpoint)
