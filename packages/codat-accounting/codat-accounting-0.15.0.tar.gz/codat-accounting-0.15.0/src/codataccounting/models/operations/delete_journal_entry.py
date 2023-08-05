"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ..shared import pushoperationsummary as shared_pushoperationsummary
from typing import Optional


@dataclasses.dataclass
class DeleteJournalEntryRequest:
    
    company_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'companyId', 'style': 'simple', 'explode': False }})
    connection_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'connectionId', 'style': 'simple', 'explode': False }})
    journal_entry_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'journalEntryId', 'style': 'simple', 'explode': False }})
    r"""Unique identifier for a journal entry"""
    

@dataclasses.dataclass
class DeleteJournalEntryResponse:
    
    content_type: str = dataclasses.field()
    status_code: int = dataclasses.field()
    push_operation_summary: Optional[shared_pushoperationsummary.PushOperationSummary] = dataclasses.field(default=None)
    r"""OK"""
    raw_response: Optional[requests_http.Response] = dataclasses.field(default=None)
    