"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

import requests as requests_http
from . import utils
from codatbanking.models import operations, shared
from typing import Optional

class Accounts:
    r"""Where payments are made or received, and bank transactions are recorded."""
    _client: requests_http.Session
    _security_client: requests_http.Session
    _server_url: str
    _language: str
    _sdk_version: str
    _gen_version: str

    def __init__(self, client: requests_http.Session, security_client: requests_http.Session, server_url: str, language: str, sdk_version: str, gen_version: str) -> None:
        self._client = client
        self._security_client = security_client
        self._server_url = server_url
        self._language = language
        self._sdk_version = sdk_version
        self._gen_version = gen_version
        
    def get(self, request: operations.GetAccountRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetAccountResponse:
        r"""Get account
        Gets a specified bank account for a given company
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetAccountRequest, base_url, '/companies/{companyId}/connections/{connectionId}/data/banking-accounts/{accountId}', request)
        
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetAccountResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Account])
                res.account = out

        return res

    def list(self, request: operations.ListAccountsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.ListAccountsResponse:
        r"""List accounts
        Gets a list of all bank accounts of the SMB, with rich data like balances, account numbers and institutions holdingthe accounts.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.ListAccountsRequest, base_url, '/companies/{companyId}/connections/{connectionId}/data/banking-accounts', request)
        
        query_params = utils.get_query_params(operations.ListAccountsRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.ListAccountsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Accounts])
                res.accounts = out

        return res

    