"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ..shared import configuration as shared_configuration
from typing import Optional


@dataclasses.dataclass
class SetConfigurationRequest:
    
    company_id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'companyId', 'style': 'simple', 'explode': False }})
    

@dataclasses.dataclass
class SetConfigurationResponse:
    
    content_type: str = dataclasses.field()
    status_code: int = dataclasses.field()
    configuration: Optional[shared_configuration.Configuration] = dataclasses.field(default=None)
    r"""Success"""
    raw_response: Optional[requests_http.Response] = dataclasses.field(default=None)
    