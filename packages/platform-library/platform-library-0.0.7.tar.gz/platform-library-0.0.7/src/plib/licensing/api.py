from typing import Optional

import requests

from plib.auth.encrypt import Encryptor
from plib.auth.jwt import encode_payload

from .exceptions import LicenseLimitAttribute, LicenseServiceError, LicenseSignatureCorrupted


class License:
    def __init__(self,
                 url: str,
                 issuer: str,
                 jwt_key: str,
                 jwt_algorithm: str,
                 salt: str,
                 workspace_id: Optional[str] = None,
                 user_name: Optional[str] = None) -> None:
        '''
        Parameters:
            url: URL to the license service graphql API
            issuer: service name of the requester
            jwt_key: secret key for JWT encoding
            jwt_algorithm: JWT algorithm
            salt: secret key to validate response from license service
            workspace_id: unique workpsace's id of the requester
            user_name: unique user's name
        '''
        assert workspace_id or user_name, "Workspace ID or user's name must be passed."
        self.url = url
        self.jwt_payload = {
            'iss': issuer,
            'aud': ['license-svc']
        }
        if workspace_id:
            self.jwt_payload['workspace'] = workspace_id
        if user_name:
            self.jwt_payload['user'] = user_name
        self.headers = {
            'Authorization': f'Bearer {encode_payload(payload=self.jwt_payload, key=jwt_key, algorithm=jwt_algorithm)}'
        }
        self.__encryptor = Encryptor(salt)

    def _post(self, data: dict) -> dict:
        response = requests.post(self.url, json=data, headers=self.headers)
        res = response.json()
        if not res['data']:
            raise LicenseServiceError(res['errors'][0]['message'])
        return res['data']

    def _validate_signature(self, encrypted_signature: str):
        if not self.__encryptor.validate(encrypted_signature):
            raise LicenseSignatureCorrupted

    def update_resource(self, resource: str, quantity: int):
        query = '''
            mutation updateResource($quantity: Int!, $resource: String!, $signature: String!) {
                updateResource(quantity: $quantity, resource: $resource) {
                    __typename
                    ... on ResourceUpdateSuccess {
                        signature(key: $signature)
                    }
                    ... on ResourceLimitError {
                        signature(key: $signature)
                        limit
                    }
                }
            }
        '''

        variables = {
            'quantity': quantity,
            'resource': resource,
            'signature': self.__encryptor.signature
        }
        data = {
            'query': query,
            'variables': variables
        }

        res = self._post(data)
        res = res['updateResource']

        self._validate_signature(res['signature'])

        if res['__typename'] == 'ResourceLimitError':
            raise LicenseLimitAttribute(resource, res['limit'])

    def make_transaction(self, resource: str):
        query = '''
            mutation makeTransaction($resource: String!, $signature: String!) {
                makeTransaction(resource: $resource) {
                    __typename
                    ... on TransactionSuccess {
                        signature(key: $signature)
                    }
                    ... on TransactionLimitError {
                        signature(key: $signature)
                        limit
                    }
                }
            }
        '''

        variables = {
            'resource': resource,
            'signature': self.__encryptor.signature
        }
        data = {
            'query': query,
            'variables': variables
        }

        res = self._post(data)
        res = res['makeTransaction']

        self._validate_signature(res['signature'])

        if res['__typename'] == 'TransactionLimitError':
            raise LicenseLimitAttribute(resource, res['limit'])
