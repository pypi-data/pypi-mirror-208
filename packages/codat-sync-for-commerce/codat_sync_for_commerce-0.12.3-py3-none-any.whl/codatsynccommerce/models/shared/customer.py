"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from ..shared import option as shared_option
from codatsynccommerce import utils
from dataclasses_json import Undefined, dataclass_json
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class Customer:
    
    customer_options: Optional[list[shared_option.Option]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('customerOptions'), 'exclude': lambda f: f is None }})
    r"""List of customer options from the list of customer records on the accounting software."""
    selected_customer_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('selectedCustomerId'), 'exclude': lambda f: f is None }})
    r"""Selected customer id from the list of customer records on the accounting software."""
    