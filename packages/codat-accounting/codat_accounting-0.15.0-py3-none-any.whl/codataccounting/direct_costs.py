"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

import requests as requests_http
from . import utils
from codataccounting.models import operations, shared
from typing import Optional

class DirectCosts:
    r"""Direct costs"""
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
        
    def create(self, request: operations.CreateDirectCostRequest, retries: Optional[utils.RetryConfig] = None) -> operations.CreateDirectCostResponse:
        r"""Create direct cost
        Posts a new direct cost to the accounting package for a given company.
        
        Required data may vary by integration. To see what data to post, first call [Get create direct cost model](https://docs.codat.io/accounting-api#/operations/get-create-directCosts-model).
        
        > **Supported Integrations**
        > 
        > Check out our [Knowledge UI](https://knowledge.codat.io/supported-features/accounting?view=tab-by-data-type&dataType=directCosts) for integrations that support creating direct costs.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.CreateDirectCostRequest, base_url, '/companies/{companyId}/connections/{connectionId}/push/directCosts', request)
        
        headers = {}
        req_content_type, data, form = utils.serialize_request_body(request, "direct_cost", 'json')
        if req_content_type not in ('multipart/form-data', 'multipart/mixed'):
            headers['content-type'] = req_content_type
        query_params = utils.get_query_params(operations.CreateDirectCostRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('POST', url, params=query_params, data=data, files=form, headers=headers)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.CreateDirectCostResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.CreateDirectCostResponse])
                res.create_direct_cost_response = out

        return res

    def download_attachment(self, request: operations.DownloadDirectCostAttachmentRequest, retries: Optional[utils.RetryConfig] = None) -> operations.DownloadDirectCostAttachmentResponse:
        r"""Download direct cost attachment
        Downloads an attachment for the specified direct cost for a given company.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.DownloadDirectCostAttachmentRequest, base_url, '/companies/{companyId}/connections/{connectionId}/data/directCosts/{directCostId}/attachments/{attachmentId}/download', request)
        
        
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

        res = operations.DownloadDirectCostAttachmentResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/octet-stream'):
                res.data = http_res.content

        return res

    def get(self, request: operations.GetDirectCostRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetDirectCostResponse:
        r"""Get direct cost
        Gets the specified direct cost for a given company.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetDirectCostRequest, base_url, '/companies/{companyId}/connections/{connectionId}/data/directCosts/{directCostId}', request)
        
        
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

        res = operations.GetDirectCostResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.DirectCost])
                res.direct_cost = out

        return res

    def get_attachment(self, request: operations.GetDirectCostAttachmentRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetDirectCostAttachmentResponse:
        r"""Get direct cost attachment
        Gets the specified direct cost attachment for a given company.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetDirectCostAttachmentRequest, base_url, '/companies/{companyId}/connections/{connectionId}/data/directCosts/{directCostId}/attachments/{attachmentId}', request)
        
        
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

        res = operations.GetDirectCostAttachmentResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Attachment])
                res.attachment = out

        return res

    def get_create_model(self, request: operations.GetCreateDirectCostsModelRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetCreateDirectCostsModelResponse:
        r"""Get create direct cost model
        Get create direct cost model. Returns the expected data for the request payload.
        
        See the examples for integration-specific indicative models.
        
        > **Supported Integrations**
        > 
        > Check out our [Knowledge UI](https://knowledge.codat.io/supported-features/accounting?view=tab-by-data-type&dataType=directCosts) for integrations that support creating direct costs.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetCreateDirectCostsModelRequest, base_url, '/companies/{companyId}/connections/{connectionId}/options/directCosts', request)
        
        
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

        res = operations.GetCreateDirectCostsModelResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.PushOption])
                res.push_option = out

        return res

    def list(self, request: operations.ListDirectCostsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.ListDirectCostsResponse:
        r"""List direct costs
        Gets the direct costs for the company.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.ListDirectCostsRequest, base_url, '/companies/{companyId}/connections/{connectionId}/data/directCosts', request)
        
        query_params = utils.get_query_params(operations.ListDirectCostsRequest, request)
        
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

        res = operations.ListDirectCostsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.DirectCosts])
                res.direct_costs = out

        return res

    def list_attachments(self, request: operations.ListDirectCostAttachmentsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.ListDirectCostAttachmentsResponse:
        r"""List direct cost attachments
        Gets all attachments for the specified direct cost for a given company.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.ListDirectCostAttachmentsRequest, base_url, '/companies/{companyId}/connections/{connectionId}/data/directCosts/{directCostId}/attachments', request)
        
        
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

        res = operations.ListDirectCostAttachmentsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.AttachmentsDataset])
                res.attachments_dataset = out

        return res

    def upload_attachment(self, request: operations.UploadDirectCostAttachmentRequest, retries: Optional[utils.RetryConfig] = None) -> operations.UploadDirectCostAttachmentResponse:
        r"""Upload direct cost attachment
        Posts a new direct cost attachment for a given company.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.UploadDirectCostAttachmentRequest, base_url, '/companies/{companyId}/connections/{connectionId}/push/directCosts/{directCostId}/attachment', request)
        
        headers = {}
        req_content_type, data, form = utils.serialize_request_body(request, "request_body", 'multipart')
        if req_content_type not in ('multipart/form-data', 'multipart/mixed'):
            headers['content-type'] = req_content_type
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('POST', url, data=data, files=form, headers=headers)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.UploadDirectCostAttachmentResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        

        return res

    