import math
import logging
import pandas as pd
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.models.household import Household
from app.models.member import Member
from app.models.account import Account
from app.models.bank_account import BankAccount
from app.models.beneficiary import Beneficiary
from app.models.investment_profile import InvestmentProfile
from app.models.investment_experience import InvestmentExperience

from app.utils.column_mapper import apply_column_mapping

logger = logging.getLogger(__name__)


def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Replace every NaN/NaT/NA with None at the DataFrame level."""
    return df.where(pd.notnull(df), other=None).replace({float('nan'): None})


def clean(v):
    """Universal sanitizer — handles every pandas dirty value."""
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    return v


def safe_float(v) -> float | None:
    """Convert to float, strip commas/$ signs, return None on failure."""
    v = clean(v)
    if v is None:
        return None
    try:
        result = float(str(v).replace(",", "").replace("$", "").strip())
        return None if math.isnan(result) else result
    except Exception:
        return None


def safe_int(v) -> int | None:
    f = safe_float(v)
    return int(f) if f is not None else None


def normalize_date(v) -> date | None:
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass

    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v

    if isinstance(v, (int, float)):
        s = str(int(v))
        if len(s) == 8:
            try:
                return datetime.strptime(s, "%m%d%Y").date()
            except ValueError:
                pass
            try:
                return datetime.strptime(s, "%Y%m%d").date()
            except ValueError:
                pass
        return None

    s = str(v).strip()
    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y", "%B %d, %Y"]:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue

    try:
        from dateutil import parser as dp
        return dp.parse(s).date()
    except Exception:
        return None


def normalize_phone(v) -> str | None:
    v = clean(v)
    if v is None:
        return None
    return str(int(float(v))) if isinstance(v, (int, float)) else str(v).strip()


def normalize_tax_bracket(v) -> str | None:
    v = clean(v)
    if v is None:
        return None
    if isinstance(v, str):
        return v.strip()
    f = safe_float(v)
    if f is None:
        return None
    if 0 < f < 1:
        return f"{int(round(f * 100))}%"
    return f"{int(f)}%"


def normalize_account_number(v) -> str | None:
    v = clean(v)
    if v is None:
        return None
    if isinstance(v, float):
        return str(int(v))
    return str(v).strip()


def set_if_present(obj, field, value):
    if value is not None:
        setattr(obj, field, value)


EXPERIENCE_COLUMNS = {
    "years_of_experience_bonds":        "Bonds",
    "years_of_experience_stocks":       "Stocks",
    "years_of_experience_alternatives": "Alternatives",
    "years_of_experience_vas":          "VAs",
    "years_of_experience_mutual_funds": "Mutual Funds",
    "years_of_experience_options":      "Options",
    "years_of_experience_partnerships": "Partnerships",
}


def get_or_create_household(db: Session, name: str) -> Household:
    obj = db.query(Household).filter_by(name=name).first()
    if obj:
        return obj
    obj = Household(name=name)
    db.add(obj)
    db.flush()
    return obj


def update_household(household: Household, row: dict):
    set_if_present(household, "annual_income",   safe_float(row.get("annual_income")))
    set_if_present(household, "total_net_worth",  safe_float(row.get("total_net_worth")))
    set_if_present(household, "liquid_net_worth", safe_float(row.get("liquid_net_worth")))
    set_if_present(household, "expense_range",    clean(row.get("expense_range")))
    set_if_present(household, "tax_bracket",      normalize_tax_bracket(row.get("tax_bracket")))
    set_if_present(household, "risk_tolerance",   clean(row.get("risk_tolerance")))
    set_if_present(household, "time_horizon",     clean(row.get("time_horizon")))


def upsert_member(db: Session, household_id: int, row: dict) -> Member | None:
    first = clean(row.get("first_name"))
    last  = clean(row.get("last_name"))

    if not first and not last:
        return None

    obj = db.query(Member).filter_by(
        household_id=household_id,
        first_name=first,
        last_name=last
    ).first()

    if not obj:
        obj = Member(household_id=household_id, first_name=first, last_name=last)
        db.add(obj)
        db.flush()

    dob_raw = row.get("date_of_birth") or row.get("dob")
    set_if_present(obj, "dob", normalize_date(dob_raw))
    set_if_present(obj, "phone",          normalize_phone(row.get("phone")))
    set_if_present(obj, "email",          clean(row.get("email")))
    set_if_present(obj, "occupation",     clean(row.get("occupation")))
    set_if_present(obj, "employer",       clean(row.get("employer")))
    set_if_present(obj, "marital_status", clean(row.get("marital_status")))
    set_if_present(obj, "address",        clean(row.get("address")))
    set_if_present(obj, "city",           clean(row.get("city")))
    set_if_present(obj, "state",          clean(row.get("state")))
    set_if_present(obj, "country",        clean(row.get("country")))
    set_if_present(obj, "relationship",   clean(row.get("relationship")))

    return obj


def upsert_investment_experience(db: Session, member: Member | None, row: dict):
    if not member:
        logger.debug("[InvestmentExperience] Skipped — no member")
        return

    for col_key, asset_type in EXPERIENCE_COLUMNS.items():
        raw = row.get(col_key)
        years = safe_int(raw)
        logger.debug(f"[InvestmentExperience] member={member.id} col={col_key} raw={raw} years={years}")

        if years is None:
            continue

        existing = db.query(InvestmentExperience).filter_by(
            member_id=member.id,
            asset_type=asset_type
        ).first()

        if existing:
            existing.years = years
        else:
            db.add(InvestmentExperience(
                member_id=member.id,
                asset_type=asset_type,
                years=years
            ))


def upsert_account(db: Session, household_id: int, row: dict) -> Account | None:
    account_type   = clean(row.get("account_type"))
    custodian      = clean(row.get("custodian"))
    account_number = normalize_account_number(row.get("account_number"))

    if not account_type and not custodian:
        return None

    # Try account_number first as the most stable unique key
    obj = None
    if account_number:
        obj = db.query(Account).filter_by(
            household_id=household_id,
            account_number=account_number
        ).first()

    # Fall back to type + custodian
    if not obj:
        obj = db.query(Account).filter_by(
            household_id=household_id,
            account_type=account_type,
            custodian=custodian
        ).first()

    if not obj:
        obj = Account(
            household_id=household_id,
            account_number=account_number,
            account_type=account_type,
            custodian=custodian,
        )
        db.add(obj)
        db.flush()
    else:
        # Update these even on existing record
        set_if_present(obj, "account_number", account_number)
        set_if_present(obj, "account_type",   account_type)
        set_if_present(obj, "custodian",      custodian)

    set_if_present(obj, "account_value",        safe_float(row.get("account_value")))
    set_if_present(obj, "ownership",            clean(row.get("ownership")))
    set_if_present(obj, "ownership_percentage", safe_float(row.get("ownership_percentage")))
    set_if_present(obj, "decision_making",      clean(row.get("decision_making")))
    set_if_present(obj, "source_of_funds",      clean(row.get("source_of_funds")))

    return obj


def upsert_investment_profile(db: Session, account: Account | None, row: dict):
    if not account:
        return

    has_data = any(clean(row.get(f)) for f in [
        "risk_tolerance", "time_horizon", "investment_objective", "liquidity_needs"
    ])
    if not has_data:
        return

    obj = db.query(InvestmentProfile).filter_by(account_id=account.id).first()
    if not obj:
        obj = InvestmentProfile(account_id=account.id)
        db.add(obj)

    set_if_present(obj, "risk_tolerance",  clean(row.get("risk_tolerance")))
    set_if_present(obj, "time_horizon",    clean(row.get("time_horizon")))
    set_if_present(obj, "liquidity_needs", clean(row.get("liquidity_needs")))
    if clean(row.get("investment_objective")):
        obj.objective = clean(row.get("investment_objective"))


def insert_bank(db: Session, household_id: int, row: dict):
    bank_name = clean(row.get("bank_name"))
    if not bank_name:
        return

    bank_account_number = normalize_account_number(row.get("bank_account_number"))

    if bank_account_number:
        existing = db.query(BankAccount).filter_by(
            household_id=household_id,
            bank_name=bank_name,
            account_number=bank_account_number
        ).first()
        if existing:
            return

    db.add(BankAccount(
        household_id=household_id,
        bank_name=bank_name,
        account_number=bank_account_number,
        account_type=clean(row.get("bank_account_type")),
        routing_number=clean(row.get("routing_number"))
    ))


def insert_beneficiaries(db: Session, account: Account | None, row: dict):
    account_id = account.id if account else None

    for n in ["1", "2"]:
        name         = clean(row.get(f"beneficiary_{n}_name"))
        percentage   = safe_float(row.get(f"beneficiary_{n}_percentage"))
        dob          = normalize_date(row.get(f"beneficiary_{n}_dob"))
        relationship = clean(row.get(f"beneficiary_{n}_relationship"))
        bene_type    = clean(row.get(f"beneficiary_{n}_type"))

        logger.debug(f"[Beneficiary] n={n} account_id={account_id} name={name} pct={percentage} dob={dob} rel={relationship} type={bene_type}")

        if not name:
            continue

        existing = db.query(Beneficiary).filter_by(
            account_id=account_id,
            name=name
        ).first()

        if existing:
            set_if_present(existing, "percentage",   percentage)
            set_if_present(existing, "dob",          dob)
            set_if_present(existing, "relationship", relationship)
            set_if_present(existing, "type",         bene_type)
            continue

        db.add(Beneficiary(
            account_id=account_id,
            name=name,
            percentage=percentage,
            dob=dob,
            relationship=relationship,
            type=bene_type,
        ))


def process_excel(file, db: Session) -> dict:
    dfs = pd.read_excel(file.file, sheet_name=None)

    rows = []
    for sheet_name, df in dfs.items():
        df, _ = apply_column_mapping(df)
        df = sanitize_dataframe(df)
        logger.info(f"[Sheet: {sheet_name}] Columns after mapping: {df.columns.tolist()}")
        rows.extend(df.to_dict("records"))

    grouped: dict[str, list[dict]] = {}
    for row in rows:
        name = clean(row.get("household_name"))
        if not name:
            continue
        grouped.setdefault(name, []).append(row)

    processed = []

    for name, items in grouped.items():
        household = get_or_create_household(db, name)

        for row in items:
            update_household(household, row)
            member  = upsert_member(db, household.id, row)
            upsert_investment_experience(db, member, row)
            account = upsert_account(db, household.id, row)
            upsert_investment_profile(db, account, row)
            insert_bank(db, household.id, row)
            insert_beneficiaries(db, account, row)

        processed.append(name)

    db.commit()
    return {"households_processed": processed}