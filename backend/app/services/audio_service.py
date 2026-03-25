import os
import json
from fastapi import HTTPException

from openai import OpenAI
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from typing import Optional, List
from dateutil import parser as date_parser

from app.models.household import Household
from app.models.member import Member
from app.models.account import Account
from app.models.investment_profile import InvestmentProfile
from app.models.bank_account import BankAccount
from app.models.beneficiary import Beneficiary
from app.models.investment_experience import InvestmentExperience

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------- EXTRACTION SUB-MODELS ---------- #
# Used ONLY during the AI extraction phase.
# They carry no IDs — the DB has not been touched yet.

class BeneficiaryExtract(BaseModel):
    name:         Optional[str]   = None
    relationship: Optional[str]   = None
    type:         Optional[str]   = None  # "primary" or "contingent"
    percentage:   Optional[float] = None
    dob:          Optional[str]   = None

    @field_validator("dob")
    @classmethod
    def parse_dob(cls, v):
        if not v:
            return None
        try:
            return str(date_parser.parse(str(v)).date())
        except Exception:
            return None

    @field_validator("percentage")
    @classmethod
    def clamp_percentage(cls, v):
        if v is not None and not (0 <= v <= 100):
            return None
        return v


class AccountExtract(BaseModel):
    account_number:       Optional[str]   = None
    account_type:         Optional[str]   = None
    custodian:            Optional[str]   = None
    account_value:        Optional[float] = None
    ownership:            Optional[str]   = None
    ownership_percentage: Optional[float] = None
    decision_making:      Optional[str]   = None
    source_of_funds:      Optional[str]   = None
    investment_objective: Optional[str]   = None
    liquidity_needs:      Optional[str]   = None
    beneficiaries:        Optional[List[BeneficiaryExtract]] = None

    @field_validator("account_value")
    @classmethod
    def must_be_positive(cls, v):
        if v is not None and v < 0:
            return None
        return v

    @field_validator("ownership_percentage")
    @classmethod
    def clamp_percentage(cls, v):
        if v is not None and not (0 <= v <= 100):
            return None
        return v


class AudioExtract(BaseModel):
    # ── Household ──────────────────────────────────────────────
    annual_income:    Optional[float] = None
    total_net_worth:  Optional[float] = None
    liquid_net_worth: Optional[float] = None
    expense_range:    Optional[str]   = None
    tax_bracket:      Optional[str]   = None
    risk_tolerance:   Optional[str]   = None
    time_horizon:     Optional[str]   = None

    # ── Member ─────────────────────────────────────────────────
    first_name:     Optional[str] = None
    last_name:      Optional[str] = None
    legal_name:     Optional[str] = None
    relationship:   Optional[str] = None
    dob:            Optional[str] = None
    occupation:     Optional[str] = None
    employer:       Optional[str] = None
    marital_status: Optional[str] = None
    phone:          Optional[str] = None
    email:          Optional[str] = None
    address:        Optional[str] = None
    city:           Optional[str] = None
    state:          Optional[str] = None
    country:        Optional[str] = None

    # ── Investment Experience ──────────────────────────────────
    years_of_experience_bonds:        Optional[int] = None
    years_of_experience_stocks:       Optional[int] = None
    years_of_experience_alternatives: Optional[int] = None
    years_of_experience_vas:          Optional[int] = None
    years_of_experience_mutual_funds: Optional[int] = None
    years_of_experience_options:      Optional[int] = None
    years_of_experience_partnerships: Optional[int] = None

    # ── Accounts (beneficiaries nested) ───────────────────────
    accounts: Optional[List[AccountExtract]] = None

    # ── Bank ───────────────────────────────────────────────────
    bank_name:           Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_account_type:   Optional[str] = None
    routing_number:      Optional[str] = None

    @field_validator("annual_income", "total_net_worth", "liquid_net_worth")
    @classmethod
    def must_be_positive(cls, v):
        if v is not None and v < 0:
            return None
        return v

    @field_validator("risk_tolerance")
    @classmethod
    def normalize_risk(cls, v):
        if not v:
            return None
        v_lower = v.lower().strip()
        if "conservative" in v_lower and "moderate" in v_lower:
            return "conservative to moderate"
        for level in ["conservative", "aggressive", "moderate", "medium", "high", "low"]:
            if level in v_lower:
                return level
        return v

    @field_validator("dob")
    @classmethod
    def parse_dob(cls, v):
        if not v:
            return None
        try:
            return str(date_parser.parse(str(v)).date())
        except Exception:
            return None

    @field_validator(
        "years_of_experience_bonds", "years_of_experience_stocks",
        "years_of_experience_alternatives", "years_of_experience_vas",
        "years_of_experience_mutual_funds", "years_of_experience_options",
        "years_of_experience_partnerships"
    )
    @classmethod
    def must_be_positive_int(cls, v):
        if v is not None and v < 0:
            return None
        return v


# ---------- CONFIRM / UPDATE SCHEMAS ---------- #
# Used ONLY in the confirm step.
# Every entity carries the DB primary key (id).
# id=None  →  insert (advisor added something not in the extraction)
# id=<int> →  update that exact row — no field-based matching

class BeneficiaryConfirm(BaseModel):
    id:           Optional[int]   = None
    name:         Optional[str]   = None
    relationship: Optional[str]   = None
    type:         Optional[str]   = None
    percentage:   Optional[float] = None
    dob:          Optional[str]   = None

    @field_validator("dob")
    @classmethod
    def parse_dob(cls, v):
        if not v:
            return None
        try:
            return str(date_parser.parse(str(v)).date())
        except Exception:
            return None

    @field_validator("percentage")
    @classmethod
    def clamp_percentage(cls, v):
        if v is not None and not (0 <= v <= 100):
            return None
        return v


class AccountConfirm(BaseModel):
    id:                   Optional[int]   = None
    account_number:       Optional[str]   = None
    account_type:         Optional[str]   = None
    custodian:            Optional[str]   = None
    account_value:        Optional[float] = None
    ownership:            Optional[str]   = None
    ownership_percentage: Optional[float] = None
    decision_making:      Optional[str]   = None
    source_of_funds:      Optional[str]   = None
    investment_objective: Optional[str]   = None
    liquidity_needs:      Optional[str]   = None
    beneficiaries:        Optional[List[BeneficiaryConfirm]] = None

    @field_validator("account_value")
    @classmethod
    def must_be_positive(cls, v):
        if v is not None and v < 0:
            return None
        return v

    @field_validator("ownership_percentage")
    @classmethod
    def clamp_percentage(cls, v):
        if v is not None and not (0 <= v <= 100):
            return None
        return v


class InvestmentExperienceConfirm(BaseModel):
    id:         Optional[int] = None
    asset_type: str
    years:      int


class BankAccountConfirm(BaseModel):
    id:             Optional[int] = None
    bank_name:      Optional[str] = None
    account_number: Optional[str] = None
    account_type:   Optional[str] = None
    routing_number: Optional[str] = None


class AudioConfirmPayload(BaseModel):
    """
    Payload for PUT /confirm.

    The frontend echoes back the IDs received from /extract.
    id present  → UPDATE that row
    id absent   → INSERT (advisor added something brand-new)
    """
    # Household (keyed by URL param, no id needed here)
    annual_income:    Optional[float] = None
    total_net_worth:  Optional[float] = None
    liquid_net_worth: Optional[float] = None
    expense_range:    Optional[str]   = None
    tax_bracket:      Optional[str]   = None
    risk_tolerance:   Optional[str]   = None
    time_horizon:     Optional[str]   = None

    # Member
    member_id:      Optional[int] = None
    first_name:     Optional[str] = None
    last_name:      Optional[str] = None
    legal_name:     Optional[str] = None
    relationship:   Optional[str] = None
    dob:            Optional[str] = None
    occupation:     Optional[str] = None
    employer:       Optional[str] = None
    marital_status: Optional[str] = None
    phone:          Optional[str] = None
    email:          Optional[str] = None
    address:        Optional[str] = None
    city:           Optional[str] = None
    state:          Optional[str] = None
    country:        Optional[str] = None

    investment_experiences: Optional[List[InvestmentExperienceConfirm]] = None
    accounts:               Optional[List[AccountConfirm]]              = None
    bank_accounts:          Optional[List[BankAccountConfirm]]          = None

    @field_validator("dob")
    @classmethod
    def parse_dob(cls, v):
        if not v:
            return None
        try:
            return str(date_parser.parse(str(v)).date())
        except Exception:
            return None

    @field_validator("annual_income", "total_net_worth", "liquid_net_worth")
    @classmethod
    def must_be_positive(cls, v):
        if v is not None and v < 0:
            return None
        return v


# ---------- EXTRACT RESPONSE SCHEMAS ---------- #
# These mirror the DB state returned after extract-and-save.
# The frontend uses these IDs to build the confirm payload.

class BeneficiaryResponse(BaseModel):
    id:           int
    name:         Optional[str]   = None
    relationship: Optional[str]   = None
    type:         Optional[str]   = None
    percentage:   Optional[float] = None
    dob:          Optional[str]   = None

    class Config:
        from_attributes = True


class InvestmentProfileResponse(BaseModel):
    id:              int
    risk_tolerance:  Optional[str] = None
    time_horizon:    Optional[str] = None
    objective:       Optional[str] = None
    liquidity_needs: Optional[str] = None

    class Config:
        from_attributes = True


class AccountResponse(BaseModel):
    id:                   int
    account_number:       Optional[str]   = None
    account_type:         Optional[str]   = None
    custodian:            Optional[str]   = None
    account_value:        Optional[float] = None
    ownership:            Optional[str]   = None
    ownership_percentage: Optional[float] = None
    decision_making:      Optional[str]   = None
    source_of_funds:      Optional[str]   = None
    investment_profile:   Optional[InvestmentProfileResponse] = None
    beneficiaries:        List[BeneficiaryResponse]           = []

    class Config:
        from_attributes = True


class InvestmentExperienceResponse(BaseModel):
    id:         int
    asset_type: str
    years:      int

    class Config:
        from_attributes = True


class MemberResponse(BaseModel):
    id:             int
    first_name:     Optional[str] = None
    last_name:      Optional[str] = None
    legal_name:     Optional[str] = None
    relationship:   Optional[str] = None
    dob:            Optional[str] = None
    occupation:     Optional[str] = None
    employer:       Optional[str] = None
    marital_status: Optional[str] = None
    phone:          Optional[str] = None
    email:          Optional[str] = None
    address:        Optional[str] = None
    city:           Optional[str] = None
    state:          Optional[str] = None
    country:        Optional[str] = None
    investment_experiences: List[InvestmentExperienceResponse] = []

    class Config:
        from_attributes = True


class BankAccountResponse(BaseModel):
    id:             int
    bank_name:      Optional[str] = None
    account_number: Optional[str] = None
    account_type:   Optional[str] = None
    routing_number: Optional[str] = None

    class Config:
        from_attributes = True


class ExtractResponse(BaseModel):
    """
    Returned by POST /extract.

    Contains the full DB state with primary keys for every saved entity.
    The frontend renders this (not raw extraction JSON) so every record the
    advisor edits already has an id attached.
    """
    transcript:    str
    household_id:  int

    member:        Optional[MemberResponse]   = None
    accounts:      List[AccountResponse]      = []
    bank_accounts: List[BankAccountResponse]  = []

    # Household-level fields echoed back
    annual_income:    Optional[float] = None
    total_net_worth:  Optional[float] = None
    liquid_net_worth: Optional[float] = None
    expense_range:    Optional[str]   = None
    tax_bracket:      Optional[str]   = None
    risk_tolerance:   Optional[str]   = None
    time_horizon:     Optional[str]   = None


# ---------- TRANSCRIPTION ---------- #

def transcribe_audio(file) -> str:
    return client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=(file.filename, file.file, file.content_type),
    ).text


# ---------- EXTRACTION ---------- #

def extract_structured_data(transcript: str) -> AudioExtract:
    prompt = f"""
You are extracting structured financial data from a wealth manager and client conversation.

Transcript:
{transcript}

Return ONLY a valid JSON object with these exact keys (set to null if not mentioned):

{{
  "annual_income": null,
  "total_net_worth": null,
  "liquid_net_worth": null,
  "expense_range": null,
  "tax_bracket": null,
  "risk_tolerance": null,
  "time_horizon": null,
  "first_name": null,
  "last_name": null,
  "legal_name": null,
  "relationship": null,
  "dob": null,
  "occupation": null,
  "employer": null,
  "marital_status": null,
  "phone": null,
  "email": null,
  "address": null,
  "city": null,
  "state": null,
  "country": null,
  "years_of_experience_bonds": null,
  "years_of_experience_stocks": null,
  "years_of_experience_alternatives": null,
  "years_of_experience_vas": null,
  "years_of_experience_mutual_funds": null,
  "years_of_experience_options": null,
  "years_of_experience_partnerships": null,
  "accounts": [
    {{
      "account_number": null,
      "account_type": null,
      "custodian": null,
      "account_value": null,
      "ownership": null,
      "ownership_percentage": null,
      "decision_making": null,
      "source_of_funds": null,
      "investment_objective": null,
      "liquidity_needs": null,
      "beneficiaries": [
        {{
          "name": null,
          "relationship": null,
          "type": null,
          "percentage": null,
          "dob": null
        }}
      ]
    }}
  ],
  "bank_name": null,
  "bank_account_number": null,
  "bank_account_type": null,
  "routing_number": null
}}

Rules:
- Extract anything clearly stated OR directly implied by a specific figure or name in the transcript
- Concrete numbers mentioned conversationally are valid: "$2,400 monthly" → extract it
- Account types named without account numbers are still extractable (e.g. "401k", "stock portfolio", "real estate")
- If multiple accounts are mentioned, return each as a separate object in the "accounts" array
- If no accounts are mentioned, set "accounts" to null (not an empty array)
- Beneficiaries belong to the account they are mentioned in context of; nest them inside that account object
- If no beneficiaries are mentioned for an account, set "beneficiaries" to null for that account
- Convert spoken numbers to digits: "forty thousand" → 40000, "two lakh" → 200000
- Do NOT infer, guess, or fill in values with no basis in the transcript
- Set null for anything not clearly mentioned
- Return ONLY the JSON object, no explanation or markdown

Field-specific rules:
- first_name / last_name: use professional/preferred name, not legal name
- legal_name: capture full legal name only if different from preferred name
- email: personal or preferred email for communications
- time_horizon: convert retirement age to years remaining e.g. "targeting retirement at 62, currently age 51" → "11 years"; if a range is given use both e.g. "11 to 14 years"
- risk_tolerance: preserve compound values e.g. "conservative to moderate"
- tax_bracket: use percentage format e.g. "22%" or descriptive e.g. "Highest"
- beneficiary type: use "primary" or "contingent" if mentioned
- source_of_funds on accounts: note origin like "divorce settlement", "inheritance", "earned income" if mentioned
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a financial data extractor. Return only valid JSON matching the exact schema provided."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    raw = json.loads(response.choices[0].message.content)
    return AudioExtract(**raw)


# ---------- SAVE DRAFT ---------- #

def save_draft(data: AudioExtract, household_id: int, db: Session) -> ExtractResponse:
    """
    Persist all extracted data and return the DB state with primary keys.

    Fuzzy field-matching happens exactly once here.  Every subsequent
    operation (confirm step) will use the returned IDs instead.
    """
    household = db.query(Household).filter_by(id=household_id).first()
    if not household:
        raise HTTPException(status_code=404, detail=f"Household {household_id} not found")

    updates = data.model_dump(exclude_none=True)

    # ── Household ─────────────────────────────────────────────────────────────
    for field in {"annual_income", "total_net_worth", "liquid_net_worth",
                  "expense_range", "tax_bracket", "risk_tolerance", "time_horizon"}:
        if field in updates:
            setattr(household, field, updates[field])

    # ── Member ────────────────────────────────────────────────────────────────
    member = None
    if data.first_name:
        member = db.query(Member).filter_by(
            household_id=household.id,
            first_name=data.first_name,
            last_name=data.last_name
        ).first()
        if not member:
            member = Member(
                household_id=household.id,
                first_name=data.first_name,
                last_name=data.last_name
            )
            db.add(member)
            db.flush()

        for field in {"legal_name", "relationship_type", "dob", "occupation", "employer",
                      "marital_status", "phone", "email", "address", "city", "state", "country"}:
            if field in updates:
                setattr(member, field, updates[field])

    # ── Investment Experience ─────────────────────────────────────────────────
    experience_field_map = {
        "years_of_experience_bonds":        "Bonds",
        "years_of_experience_stocks":       "Stocks",
        "years_of_experience_alternatives": "Alternatives",
        "years_of_experience_vas":          "VAs",
        "years_of_experience_mutual_funds": "Mutual Funds",
        "years_of_experience_options":      "Options",
        "years_of_experience_partnerships": "Partnerships",
    }
    saved_experiences: List[InvestmentExperience] = []
    if member:
        for field, asset_type in experience_field_map.items():
            years = updates.get(field)
            if years is None:
                continue
            exp = db.query(InvestmentExperience).filter_by(
                member_id=member.id, asset_type=asset_type
            ).first()
            if exp:
                exp.years = years
            else:
                exp = InvestmentExperience(member_id=member.id, asset_type=asset_type, years=years)
                db.add(exp)
                db.flush()
            saved_experiences.append(exp)

    # ── Accounts + Beneficiaries ──────────────────────────────────────────────
    saved_accounts: List[Account] = []
    if data.accounts:
        for acct_data in data.accounts:
            acct_dump = acct_data.model_dump(exclude_none=True)
            if not acct_dump:
                continue

            account = None
            if acct_data.account_type or acct_data.custodian:
                account = db.query(Account).filter_by(
                    household_id=household.id,
                    account_type=acct_data.account_type,
                    custodian=acct_data.custodian
                ).first()
            if not account:
                account = Account(
                    household_id=household.id,
                    account_number=acct_data.account_number,
                    account_type=acct_data.account_type,
                    custodian=acct_data.custodian,
                )
                db.add(account)
                db.flush()

            for field in {"account_value", "ownership", "ownership_percentage",
                          "decision_making", "source_of_funds"}:
                if field in acct_dump:
                    setattr(account, field, acct_dump[field])

            # Investment Profile
            if acct_data.investment_objective or acct_data.liquidity_needs:
                profile = db.query(InvestmentProfile).filter_by(account_id=account.id).first()
                if not profile:
                    profile = InvestmentProfile(account_id=account.id)
                    db.add(profile)
                    db.flush()
                if data.risk_tolerance:
                    profile.risk_tolerance = data.risk_tolerance
                if data.time_horizon:
                    profile.time_horizon = data.time_horizon
                if acct_data.investment_objective:
                    profile.objective = acct_data.investment_objective
                if acct_data.liquidity_needs:
                    profile.liquidity_needs = acct_data.liquidity_needs

            # Beneficiaries
            if acct_data.beneficiaries:
                for bene in acct_data.beneficiaries:
                    if not bene.name:
                        continue
                    existing = db.query(Beneficiary).filter_by(
                        account_id=account.id, name=bene.name
                    ).first()
                    if existing:
                        if bene.percentage is not None:
                            existing.percentage = bene.percentage
                        if bene.dob is not None:
                            existing.dob = bene.dob
                        if bene.relationship is not None:
                            existing.relationship = bene.relationship
                        if bene.type is not None:
                            existing.type = bene.type
                    else:
                        existing = Beneficiary(
                            account_id=account.id,
                            name=bene.name,
                            relationship=bene.relationship,
                            type=bene.type,
                            percentage=bene.percentage,
                            dob=bene.dob
                        )
                        db.add(existing)
                        db.flush()

            saved_accounts.append(account)

    # ── Bank Account ──────────────────────────────────────────────────────────
    saved_banks: List[BankAccount] = []
    if data.bank_name:
        bank = db.query(BankAccount).filter_by(
            household_id=household.id,
            bank_name=data.bank_name,
            account_number=data.bank_account_number
        ).first()
        if not bank:
            bank = BankAccount(
                household_id=household.id,
                bank_name=data.bank_name,
                account_number=data.bank_account_number,
                account_type=data.bank_account_type,
                routing_number=data.routing_number
            )
            db.add(bank)
            db.flush()
        saved_banks.append(bank)

    db.commit()

    # Refresh to populate ORM relationships
    db.refresh(household)
    if member:
        db.refresh(member)
    for acct in saved_accounts:
        db.refresh(acct)

    # ── Build typed response with IDs ─────────────────────────────────────────
    member_response = None
    if member:
        member_response = MemberResponse(
            id=member.id,
            first_name=member.first_name,
            last_name=member.last_name,
            legal_name=member.legal_name,
            relationship=member.relationship_type,
            dob=str(member.dob) if member.dob else None,
            occupation=member.occupation,
            employer=member.employer,
            marital_status=member.marital_status,
            phone=member.phone,
            email=member.email,
            address=member.address,
            city=member.city,
            state=member.state,
            country=member.country,
            investment_experiences=[
                InvestmentExperienceResponse(id=e.id, asset_type=e.asset_type, years=e.years)
                for e in saved_experiences
            ]
        )

    account_responses = []
    for acct in saved_accounts:
        profile = db.query(InvestmentProfile).filter_by(account_id=acct.id).first()
        benes   = db.query(Beneficiary).filter_by(account_id=acct.id).all()
        account_responses.append(AccountResponse(
            id=acct.id,
            account_number=acct.account_number,
            account_type=acct.account_type,
            custodian=acct.custodian,
            account_value=acct.account_value,
            ownership=acct.ownership,
            ownership_percentage=acct.ownership_percentage,
            decision_making=acct.decision_making,
            source_of_funds=acct.source_of_funds,
            investment_profile=InvestmentProfileResponse(
                id=profile.id,
                risk_tolerance=profile.risk_tolerance,
                time_horizon=profile.time_horizon,
                objective=profile.objective,
                liquidity_needs=profile.liquidity_needs,
            ) if profile else None,
            beneficiaries=[
                BeneficiaryResponse(
                    id=b.id, name=b.name, relationship=b.relationship,
                    type=b.type, percentage=b.percentage,
                    dob=str(b.dob) if b.dob else None,
                )
                for b in benes
            ]
        ))

    return ExtractResponse(
        transcript="",          # caller fills this in
        household_id=household.id,
        member=member_response,
        accounts=account_responses,
        bank_accounts=[
            BankAccountResponse(
                id=b.id, bank_name=b.bank_name, account_number=b.account_number,
                account_type=b.account_type, routing_number=b.routing_number,
            )
            for b in saved_banks
        ],
        annual_income=household.annual_income,
        total_net_worth=household.total_net_worth,
        liquid_net_worth=household.liquid_net_worth,
        expense_range=household.expense_range,
        tax_bracket=household.tax_bracket,
        risk_tolerance=household.risk_tolerance,
        time_horizon=household.time_horizon,
    )


# ---------- CONFIRM / UPDATE BY ID ---------- #

def apply_confirmed_data(data: AudioConfirmPayload, household_id: int, db: Session) -> dict:
    """
    Update-only step.

    Every entity is looked up by its primary key.
    id present  → UPDATE that exact row (no field-based matching)
    id absent   → INSERT (advisor added something brand-new)
    """
    household = db.query(Household).filter_by(id=household_id).first()
    if not household:
        raise HTTPException(status_code=404, detail=f"Household {household_id} not found")

    updates = data.model_dump(exclude_none=True)

    # ── Household ─────────────────────────────────────────────────────────────
    for field in {"annual_income", "total_net_worth", "liquid_net_worth",
                  "expense_range", "tax_bracket", "risk_tolerance", "time_horizon"}:
        if field in updates:
            setattr(household, field, updates[field])

    # ── Member ────────────────────────────────────────────────────────────────
    if data.member_id is not None:
        member = db.query(Member).filter_by(id=data.member_id, household_id=household.id).first()
        if not member:
            raise HTTPException(
                status_code=404,
                detail=f"Member {data.member_id} not found in household {household_id}"
            )
        for field in {"first_name", "last_name", "legal_name", "relationship_type", "dob",
                      "occupation", "employer", "marital_status",
                      "phone", "email", "address", "city", "state", "country"}:
            if field in updates:
                setattr(member, field, updates[field])
    elif data.first_name:
        # Advisor added a brand-new member
        member = Member(household_id=household.id, first_name=data.first_name, last_name=data.last_name)
        db.add(member)
        db.flush()

    # ── Investment Experience ─────────────────────────────────────────────────
    if data.investment_experiences:
        for exp_data in data.investment_experiences:
            if exp_data.id is not None:
                exp = db.query(InvestmentExperience).filter_by(id=exp_data.id).first()
                if exp:
                    exp.years      = exp_data.years
                    exp.asset_type = exp_data.asset_type
            else:
                if data.member_id:
                    db.add(InvestmentExperience(
                        member_id=data.member_id,
                        asset_type=exp_data.asset_type,
                        years=exp_data.years
                    ))

    # ── Accounts ──────────────────────────────────────────────────────────────
    if data.accounts:
        for acct_data in data.accounts:
            if acct_data.id is not None:
                account = db.query(Account).filter_by(
                    id=acct_data.id, household_id=household.id
                ).first()
                if not account:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Account {acct_data.id} not found in household {household_id}"
                    )
            else:
                account = Account(household_id=household.id)
                db.add(account)
                db.flush()

            acct_dump = acct_data.model_dump(exclude_none=True)
            for field in {"account_number", "account_type", "custodian", "account_value",
                          "ownership", "ownership_percentage", "decision_making", "source_of_funds"}:
                if field in acct_dump:
                    setattr(account, field, acct_dump[field])

            # Investment Profile
            if acct_data.investment_objective or acct_data.liquidity_needs:
                profile = db.query(InvestmentProfile).filter_by(account_id=account.id).first()
                if not profile:
                    profile = InvestmentProfile(account_id=account.id)
                    db.add(profile)
                if acct_data.investment_objective:
                    profile.objective = acct_data.investment_objective
                if acct_data.liquidity_needs:
                    profile.liquidity_needs = acct_data.liquidity_needs
                if data.risk_tolerance:
                    profile.risk_tolerance = data.risk_tolerance
                if data.time_horizon:
                    profile.time_horizon = data.time_horizon

            # Beneficiaries
            if acct_data.beneficiaries:
                for bene_data in acct_data.beneficiaries:
                    if bene_data.id is not None:
                        bene = db.query(Beneficiary).filter_by(
                            id=bene_data.id, account_id=account.id
                        ).first()
                        if not bene:
                            raise HTTPException(
                                status_code=404,
                                detail=f"Beneficiary {bene_data.id} not found for account {account.id}"
                            )
                        if bene_data.name is not None:       bene.name         = bene_data.name
                        if bene_data.relationship is not None: bene.relationship = bene_data.relationship
                        if bene_data.type is not None:       bene.type         = bene_data.type
                        if bene_data.percentage is not None: bene.percentage   = bene_data.percentage
                        if bene_data.dob is not None:        bene.dob          = bene_data.dob
                    else:
                        if bene_data.name:
                            db.add(Beneficiary(
                                account_id=account.id,
                                name=bene_data.name,
                                relationship=bene_data.relationship,
                                type=bene_data.type,
                                percentage=bene_data.percentage,
                                dob=bene_data.dob
                            ))

    # ── Bank Accounts ─────────────────────────────────────────────────────────
    if data.bank_accounts:
        for bank_data in data.bank_accounts:
            if bank_data.id is not None:
                bank = db.query(BankAccount).filter_by(
                    id=bank_data.id, household_id=household.id
                ).first()
                if not bank:
                    raise HTTPException(
                        status_code=404,
                        detail=f"BankAccount {bank_data.id} not found in household {household_id}"
                    )
                if bank_data.bank_name is not None:      bank.bank_name      = bank_data.bank_name
                if bank_data.account_number is not None: bank.account_number = bank_data.account_number
                if bank_data.account_type is not None:   bank.account_type   = bank_data.account_type
                if bank_data.routing_number is not None: bank.routing_number = bank_data.routing_number
            else:
                if bank_data.bank_name:
                    db.add(BankAccount(
                        household_id=household.id,
                        bank_name=bank_data.bank_name,
                        account_number=bank_data.account_number,
                        account_type=bank_data.account_type,
                        routing_number=bank_data.routing_number
                    ))

    db.commit()
    return {"household_id": household.id}


# ---------- SERVICE ENTRY POINTS ---------- #

def extract_audio(file, household_id: int, db: Session) -> ExtractResponse:
    """
    Step 1 — Transcribe + extract + immediately save to DB.

    Returns ExtractResponse with primary keys for every saved entity.
    The frontend must render this response (not the raw extraction) so that
    every field the advisor edits already carries its DB id.
    """
    household = db.query(Household).filter_by(id=household_id).first()
    if not household:
        raise HTTPException(status_code=404, detail=f"Household {household_id} not found")

    transcript = transcribe_audio(file)
    extracted  = extract_structured_data(transcript)

    try:
        response = save_draft(extracted, household_id, db)
        response.transcript = transcript
        return response
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def confirm_audio(data: AudioConfirmPayload, household_id: int, db: Session) -> dict:
    """
    Step 2 — Advisor confirmed (and optionally edited) the data.

    Updates records by primary key only.  No fuzzy field-matching.
    New records (id=None) are created only if the advisor added something.
    """
    try:
        return apply_confirmed_data(data, household_id, db)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise