"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ..shared import taxrate as shared_taxrate
from typing import Optional


@dataclasses.dataclass
class GetTaxRateRequest:
    
    company_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'companyId', 'style': 'simple', 'explode': False }})
    tax_rate_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'taxRateId', 'style': 'simple', 'explode': False }})
    

@dataclasses.dataclass
class GetTaxRateResponse:
    
    content_type: str = dataclasses.field()
    status_code: int = dataclasses.field()
    raw_response: Optional[requests_http.Response] = dataclasses.field(default=None)
    tax_rate: Optional[shared_taxrate.TaxRate] = dataclasses.field(default=None)
    r"""Success"""
    