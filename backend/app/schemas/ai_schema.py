from pydantic import BaseModel
from typing import List, Optional


class HouseholdSchema(BaseModel):
    name: Optional[str]
    annual_income: Optional[float]
    total_net_worth: Optional[float]
    tax_bracket: Optional[str]


class MemberSchema(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]


class AccountSchema(BaseModel):
    account_type: Optional[str]
    custodian: Optional[str]
    decision_making: Optional[str]
    source_of_funds: Optional[str]


class AIOutputSchema(BaseModel):
    household: HouseholdSchema
    members: List[MemberSchema]
    accounts: List[AccountSchema]