"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from ..shared import accountstatus_enum as shared_accountstatus_enum
from ..shared import accounttype_enum as shared_accounttype_enum
from ..shared import metadata as shared_metadata
from ..shared import validdatatypelinks as shared_validdatatypelinks
from codataccounting import utils
from dataclasses_json import Undefined, dataclass_json
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class Account:
    r"""> **Language tip:** Accounts are also referred to as **chart of accounts**, **nominal accounts**, and **general ledger**.
    
    View the coverage for accounts in the <a className=\"external\" href=\"https://knowledge.codat.io/supported-features/accounting?view=tab-by-data-type&dataType=chartOfAccounts\" target=\"_blank\">Data coverage explorer</a>.
    
    ## Overview
    
    Accounts are the categories a business uses to record accounting transactions. From the Accounts endpoints, you can retrieve a list of all accounts for a specified company. 
    
    The categories for an account include:
      * Asset
      * Expense
      * Income
      * Liability
      * Equity.
    
    > **Accounts with no category**
    > 
    > If an account is pulled from the chart of accounts and its nominal code does not lie within the category layout for the company's accounts, then the **type** is `Unknown`. The **fullyQualifiedCategory** and **fullyQualifiedName** fields return `null`.
    > 
    > This approach gives a true representation of the company's accounts whilst preventing distorting financials such as a company's profit and loss and balance sheet reports.
    """
    
    is_bank_account: bool = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('isBankAccount') }})
    r"""Confirms whether the account is a bank account or not."""
    status: shared_accountstatus_enum.AccountStatusEnum = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('status') }})
    r"""Status of the account"""
    type: shared_accounttype_enum.AccountTypeEnum = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('type') }})
    r"""Type of account"""
    currency: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('currency'), 'exclude': lambda f: f is None }})
    r"""The currency data type in Codat is the [ISO 4217](https://en.wikipedia.org/wiki/ISO_4217) currency code, e.g. _GBP_.
    
    ## Unknown currencies
    
    In line with the ISO 4217 specification, the code _XXX_ is used when the data source does not return a currency for a transaction. 
    
    There are only a very small number of edge cases where this currency code is returned by the Codat system.
    """
    current_balance: Optional[float] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('currentBalance'), 'exclude': lambda f: f is None }})
    r"""Current balance in the account."""
    description: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('description'), 'exclude': lambda f: f is None }})
    r"""Description for the account."""
    fully_qualified_category: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('fullyQualifiedCategory'), 'exclude': lambda f: f is None }})
    r"""Full category of the account. For example:
    Liability.Current or Income.Revenue. See example data.
    """
    fully_qualified_name: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('fullyQualifiedName'), 'exclude': lambda f: f is None }})
    r"""Full name of the account, for example:
    - `Liability.Current.VAT`
    - `Income.Revenue.Sales`
    """
    id: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('id'), 'exclude': lambda f: f is None }})
    r"""Identifier for the account, unique for the company."""
    metadata: Optional[shared_metadata.Metadata] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('metadata'), 'exclude': lambda f: f is None }})
    modified_date: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('modifiedDate'), 'exclude': lambda f: f is None }})
    name: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('name'), 'exclude': lambda f: f is None }})
    r"""Name of the account."""
    nominal_code: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('nominalCode'), 'exclude': lambda f: f is None }})
    r"""Reference given to each nominal account for a business. It ensures money is allocated to the correct account. This code isn't a unique identifier in the Codat system."""
    source_modified_date: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('sourceModifiedDate'), 'exclude': lambda f: f is None }})
    valid_datatype_links: Optional[list[shared_validdatatypelinks.ValidDataTypeLinks]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('validDatatypeLinks'), 'exclude': lambda f: f is None }})
    r"""The validDatatypeLinks can be used to determine whether an account can be correctly mapped to another object; for example, accounts with a `type` of `income` might only support being used on an Invoice and Direct Income. For more information, see [Valid Data Type Links](/accounting-api#/schemas/ValidDataTypeLinks)."""
    