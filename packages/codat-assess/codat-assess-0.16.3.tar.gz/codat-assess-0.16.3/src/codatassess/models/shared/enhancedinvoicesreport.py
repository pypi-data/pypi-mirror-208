"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from ..shared import enhancedinvoicereportitem as shared_enhancedinvoicereportitem
from ..shared import reportinfo as shared_reportinfo
from codatassess import utils
from dataclasses_json import Undefined, dataclass_json
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class EnhancedInvoicesReportReportItems:
    
    invoices: Optional[list[shared_enhancedinvoicereportitem.EnhancedInvoiceReportItem]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('invoices'), 'exclude': lambda f: f is None }})
    

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class EnhancedInvoicesReport:
    r"""The enhanced invoices report takes the key elements of the Invoices report verifying those marked as paid in the accounting platform have actually been paid by matching with the bank statement."""
    
    report_info: Optional[shared_reportinfo.ReportInfo] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('reportInfo'), 'exclude': lambda f: f is None }})
    r"""Report additional information, which is specific to Assess reports"""
    report_items: Optional[list[EnhancedInvoicesReportReportItems]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('reportItems'), 'exclude': lambda f: f is None }})
    