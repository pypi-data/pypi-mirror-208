"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ..shared import transfer as shared_transfer
from typing import Optional


@dataclasses.dataclass
class GetTransferRequest:
    
    company_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'companyId', 'style': 'simple', 'explode': False }})
    connection_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'connectionId', 'style': 'simple', 'explode': False }})
    transfer_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'transferId', 'style': 'simple', 'explode': False }})
    

@dataclasses.dataclass
class GetTransferResponse:
    
    content_type: str = dataclasses.field()
    status_code: int = dataclasses.field()
    raw_response: Optional[requests_http.Response] = dataclasses.field(default=None)
    transfer: Optional[shared_transfer.Transfer] = dataclasses.field(default=None)
    r"""Success"""
    