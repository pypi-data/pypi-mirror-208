"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ..shared import pushoperation as shared_pushoperation
from typing import Optional


@dataclasses.dataclass
class GetPushOperationRequest:
    
    company_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'companyId', 'style': 'simple', 'explode': False }})
    push_operation_key: str = dataclasses.field(metadata={'path_param': { 'field_name': 'pushOperationKey', 'style': 'simple', 'explode': False }})
    r"""Push operation key."""
    

@dataclasses.dataclass
class GetPushOperationResponse:
    
    content_type: str = dataclasses.field()
    status_code: int = dataclasses.field()
    push_operation: Optional[shared_pushoperation.PushOperation] = dataclasses.field(default=None)
    r"""OK"""
    raw_response: Optional[requests_http.Response] = dataclasses.field(default=None)
    