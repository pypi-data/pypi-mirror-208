"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from ..shared import dataintegritybyamount as shared_dataintegritybyamount
from ..shared import dataintegritybycount as shared_dataintegritybycount
from codatassess import utils
from dataclasses_json import Undefined, dataclass_json
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class DataIntegritySummary:
    
    by_amount: Optional[shared_dataintegritybyamount.DataIntegrityByAmount] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('byAmount'), 'exclude': lambda f: f is None }})
    by_count: Optional[shared_dataintegritybycount.DataIntegrityByCount] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('byCount'), 'exclude': lambda f: f is None }})
    type: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('type'), 'exclude': lambda f: f is None }})
    r"""The data type which the data type in the URL has been matched against. For example, if you've matched accountTransactions and banking-transactions, and you call this endpoint with accountTransactions in the URL, this property would be banking-transactions."""
    