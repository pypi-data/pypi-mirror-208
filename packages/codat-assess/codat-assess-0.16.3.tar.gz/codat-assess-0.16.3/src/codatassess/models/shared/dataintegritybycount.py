"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from codatassess import utils
from dataclasses_json import Undefined, dataclass_json
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class DataIntegrityByCount:
    
    matched: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('matched'), 'exclude': lambda f: f is None }})
    r"""The number of records of the type specified in the route which do have a match."""
    match_percentage: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('matchPercentage'), 'exclude': lambda f: f is None }})
    r"""The percentage of records of the type specified in the route which have a match."""
    total: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('total'), 'exclude': lambda f: f is None }})
    r"""The total of unmatched and matched."""
    unmatched: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('unmatched'), 'exclude': lambda f: f is None }})
    r"""The number of records of the type specified in the route which don't have a match."""
    