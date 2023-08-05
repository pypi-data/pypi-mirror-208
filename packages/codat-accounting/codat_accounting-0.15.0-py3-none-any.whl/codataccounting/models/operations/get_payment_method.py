"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ..shared import paymentmethod as shared_paymentmethod
from typing import Optional


@dataclasses.dataclass
class GetPaymentMethodRequest:
    
    company_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'companyId', 'style': 'simple', 'explode': False }})
    payment_method_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'paymentMethodId', 'style': 'simple', 'explode': False }})
    

@dataclasses.dataclass
class GetPaymentMethodResponse:
    
    content_type: str = dataclasses.field()
    status_code: int = dataclasses.field()
    payment_method: Optional[shared_paymentmethod.PaymentMethod] = dataclasses.field(default=None)
    r"""Success"""
    raw_response: Optional[requests_http.Response] = dataclasses.field(default=None)
    