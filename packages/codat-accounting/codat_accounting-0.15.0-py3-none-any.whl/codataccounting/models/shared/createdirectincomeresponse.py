"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
from ..shared import datatype_enum as shared_datatype_enum
from ..shared import directincome as shared_directincome
from ..shared import pushoperationchange as shared_pushoperationchange
from ..shared import pushoperationstatus_enum as shared_pushoperationstatus_enum
from ..shared import validation as shared_validation
from codataccounting import utils
from dataclasses_json import Undefined, dataclass_json
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclasses.dataclass
class CreateDirectIncomeResponse:
    r"""Success"""
    
    company_id: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('companyId') }})
    r"""Unique identifier for your SMB in Codat."""
    data_connection_key: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('dataConnectionKey') }})
    r"""Unique identifier for a company's data connection."""
    push_operation_key: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('pushOperationKey') }})
    r"""A unique identifier generated by Codat to represent this single push operation. This identifier can be used to track the status of the push, and should be persisted."""
    requested_on_utc: str = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('requestedOnUtc') }})
    r"""In Codat's data model, dates and times are represented using the <a class=\\"external\\" href=\\"https://en.wikipedia.org/wiki/ISO_8601\\" target=\\"_blank\\">ISO 8601 standard</a>. Date and time fields are formatted as strings; for example:
    
    ```
    2020-10-08T22:40:50Z
    2021-01-01T00:00:00
    ```
    
    
    
    When syncing data that contains `DateTime` fields from Codat, make sure you support the following cases when reading time information:
    
    - Coordinated Universal Time (UTC): `2021-11-15T06:00:00Z`
    - Unqualified local time: `2021-11-15T01:00:00`
    - UTC time offsets: `2021-11-15T01:00:00-05:00`
    
    > Time zones
    > 
    > Not all dates from Codat will contain information about time zones.  
    > Where it is not available from the underlying platform, Codat will return these as times local to the business whose data has been synced.
    """
    status: shared_pushoperationstatus_enum.PushOperationStatusEnum = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('status') }})
    r"""The status of the push operation."""
    status_code: int = dataclasses.field(metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('statusCode') }})
    changes: Optional[list[shared_pushoperationchange.PushOperationChange]] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('changes'), 'exclude': lambda f: f is None }})
    completed_on_utc: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('completedOnUtc'), 'exclude': lambda f: f is None }})
    r"""In Codat's data model, dates and times are represented using the <a class=\\"external\\" href=\\"https://en.wikipedia.org/wiki/ISO_8601\\" target=\\"_blank\\">ISO 8601 standard</a>. Date and time fields are formatted as strings; for example:
    
    ```
    2020-10-08T22:40:50Z
    2021-01-01T00:00:00
    ```
    
    
    
    When syncing data that contains `DateTime` fields from Codat, make sure you support the following cases when reading time information:
    
    - Coordinated Universal Time (UTC): `2021-11-15T06:00:00Z`
    - Unqualified local time: `2021-11-15T01:00:00`
    - UTC time offsets: `2021-11-15T01:00:00-05:00`
    
    > Time zones
    > 
    > Not all dates from Codat will contain information about time zones.  
    > Where it is not available from the underlying platform, Codat will return these as times local to the business whose data has been synced.
    """
    data: Optional[shared_directincome.DirectIncome] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('data'), 'exclude': lambda f: f is None }})
    r"""> **Language tip:**  Direct incomes may also be referred to as **Receive transactions**, **Receive money transactions**, **Sales receipts**, or **Cash sales** in various accounting platforms.
    
    > View the coverage for direct incomes in the <a className=\"external\" href=\"https://knowledge.codat.io/supported-features/accounting?view=tab-by-data-type&dataType=directIncomes\" target=\"_blank\">Data coverage explorer</a>.
    
    ## Overview
    
    Direct incomes include: 
    
    - Selling an item directly to a contact, and receiving payment at the point of the sale.
    - Refunding an item in cash to a contact.
    - Depositing money into a bank account.
    
    Direct incomes is a child data type of [account transactions](https://docs.codat.io/accounting-api#/schemas/AccountTransaction).
    """
    data_type: Optional[shared_datatype_enum.DataTypeEnum] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('dataType'), 'exclude': lambda f: f is None }})
    r"""Available Data types"""
    error_message: Optional[str] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('errorMessage'), 'exclude': lambda f: f is None }})
    timeout_in_minutes: Optional[int] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('timeoutInMinutes'), 'exclude': lambda f: f is None }})
    timeout_in_seconds: Optional[int] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('timeoutInSeconds'), 'exclude': lambda f: f is None }})
    validation: Optional[shared_validation.Validation] = dataclasses.field(default=None, metadata={'dataclasses_json': { 'letter_case': utils.get_field_name('validation'), 'exclude': lambda f: f is None }})
    r"""A human-readable object describing validation decisions Codat has made when pushing data into the platform. If a push has failed because of validation errors, they will be detailed here."""
    