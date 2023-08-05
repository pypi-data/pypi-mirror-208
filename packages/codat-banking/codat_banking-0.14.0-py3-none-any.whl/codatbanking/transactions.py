"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

import requests as requests_http
from . import utils
from codatbanking.models import operations, shared
from typing import Optional

class Transactions:
    r"""An immutable source of up-to-date information on income and expenditure."""
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
        
    def get(self, request: operations.GetTransactionRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetTransactionResponse:
        r"""Get bank transaction
        Gets a specified bank transaction for a given company
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetTransactionRequest, base_url, '/companies/{companyId}/connections/{connectionId}/data/banking-transactions/{transactionId}', request)
        
        
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

        res = operations.GetTransactionResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Transaction])
                res.transaction = out

        return res

    def list(self, request: operations.ListTransactionsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.ListTransactionsResponse:
        r"""List transactions
        Gets a list of transactions incurred by a bank account.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.ListTransactionsRequest, base_url, '/companies/{companyId}/connections/{connectionId}/data/banking-transactions', request)
        
        query_params = utils.get_query_params(operations.ListTransactionsRequest, request)
        
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

        res = operations.ListTransactionsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Transactions])
                res.transactions = out

        return res

    