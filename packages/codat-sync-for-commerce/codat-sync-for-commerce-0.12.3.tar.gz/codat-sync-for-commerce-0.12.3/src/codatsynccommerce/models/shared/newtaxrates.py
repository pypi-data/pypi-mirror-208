"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from ..shared import option as shared_option
from ..shared import taxratemapping as shared_taxratemapping
from codatsynccommerce import utils
from dataclasses_json import Undefined, dataclass_json
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class NewTaxRates:
    
    accounting_tax_rate_options: Optional[list[shared_option.Option]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('accountingTaxRateOptions'), 'exclude': lambda f: f is None }})
    r"""Array of accounting tax rate options."""
    commerce_tax_rate_options: Optional[list[shared_option.Option]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('commerceTaxRateOptions'), 'exclude': lambda f: f is None }})
    r"""Array of tax component options."""
    default_zero_tax_rate_options: Optional[list[shared_option.Option]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('defaultZeroTaxRateOptions'), 'exclude': lambda f: f is None }})
    r"""Default zero tax rate selected for sync."""
    selected_default_zero_tax_rate_id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('selectedDefaultZeroTaxRateId'), 'exclude': lambda f: f is None }})
    r"""Default tax rate selected for sync."""
    tax_rate_mappings: Optional[list[shared_taxratemapping.TaxRateMapping]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('taxRateMappings'), 'exclude': lambda f: f is None }})
    r"""Array of tax component to rate mapppings."""
    