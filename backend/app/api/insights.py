from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from app.db.session import SessionLocal

from app.models.household import Household
from app.models.member import Member
from app.models.account import Account
from app.models.bank_account import BankAccount
from app.models.beneficiary import Beneficiary
from app.models.investment_profile import InvestmentProfile
from app.models.investment_experience import InvestmentExperience

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _safe_float(val, default=0.0):
    """Return float or default if None."""
    try:
        return float(val) if val is not None else default
    except (TypeError, ValueError):
        return default


def _calc_age(dob) -> int | None:
    """Return age in years from a date/string DOB."""
    if not dob:
        return None
    try:
        if isinstance(dob, str):
            from dateutil import parser as dp
            dob = dp.parse(dob).date()
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except Exception:
        return None


@router.get("/insights/{household_id}")
def get_insights(household_id: int, db: Session = Depends(get_db)):

    household = db.query(Household).filter_by(id=household_id).first()
    if not household:
        return {"error": "Household not found"}

    members   = db.query(Member).filter_by(household_id=household_id).all()
    accounts  = db.query(Account).filter_by(household_id=household_id).all()
    banks     = db.query(BankAccount).filter_by(household_id=household_id).all()

    account_ids = [a.id for a in accounts]

    beneficiaries = (
        db.query(Beneficiary).filter(Beneficiary.account_id.in_(account_ids)).all()
        if account_ids else []
    )
    profiles = (
        db.query(InvestmentProfile).filter(InvestmentProfile.account_id.in_(account_ids)).all()
        if account_ids else []
    )
    member_ids = [m.id for m in members]
    experiences = (
        db.query(InvestmentExperience).filter(InvestmentExperience.member_id.in_(member_ids)).all()
        if member_ids else []
    )

    annual_income    = _safe_float(household.annual_income)
    total_net_worth  = _safe_float(household.total_net_worth)
    liquid_net_worth = _safe_float(household.liquid_net_worth)
    total_account_value = sum(_safe_float(a.account_value) for a in accounts)

    # ── 1. SUMMARY ───────────────────────────────────────────────────────────
    illiquid_net_worth = max(total_net_worth - liquid_net_worth, 0)
    liquid_ratio = round((liquid_net_worth / total_net_worth * 100), 1) if total_net_worth else 0

    summary = {
        "household_name":       household.name,
        "annual_income":        annual_income,
        "total_net_worth":      total_net_worth,
        "liquid_net_worth":     liquid_net_worth,
        "illiquid_net_worth":   illiquid_net_worth,
        "liquid_ratio_pct":     liquid_ratio,
        "total_account_value":  total_account_value,
        "risk_tolerance":       household.risk_tolerance or "N/A",
        "time_horizon":         household.time_horizon or "N/A",
        "tax_bracket":          household.tax_bracket or "N/A",
        "expense_range":        household.expense_range or "N/A",
        "members_count":        len(members),
        "accounts_count":       len(accounts),
        "banks_count":          len(banks),
        "beneficiaries_count":  len(beneficiaries),
    }

    # ── 2. NET WORTH BREAKDOWN ────────────────────────────────────────────────
    # Liquid vs Illiquid vs Account Assets
    net_worth_breakdown = []
    if liquid_net_worth:
        net_worth_breakdown.append({"name": "Liquid Net Worth",   "value": liquid_net_worth})
    if illiquid_net_worth:
        net_worth_breakdown.append({"name": "Illiquid Net Worth", "value": illiquid_net_worth})
    if not net_worth_breakdown and total_net_worth:
        net_worth_breakdown.append({"name": "Net Worth", "value": total_net_worth})

    # ── 3. INCOME vs EXPENSES vs NET WORTH ───────────────────────────────────
    income_vs_networth = [
        {"name": "Annual Income",   "value": annual_income},
        {"name": "Total Net Worth", "value": total_net_worth},
        {"name": "Liquid Assets",   "value": liquid_net_worth},
    ]
    # strip zeros so bar chart doesn't show empty bars
    income_vs_networth = [x for x in income_vs_networth if x["value"] > 0]

    # ── 4. ACCOUNT VALUE BY TYPE ──────────────────────────────────────────────
    account_value_by_type: dict[str, float] = {}
    for acc in accounts:
        key = acc.account_type or "Unknown"
        account_value_by_type[key] = account_value_by_type.get(key, 0) + _safe_float(acc.account_value)

    account_value_chart = [
        {"name": k, "value": round(v, 2)}
        for k, v in account_value_by_type.items()
        if v > 0
    ]

    # ── 5. ACCOUNT COUNT BY TYPE ──────────────────────────────────────────────
    account_type_dist: dict[str, int] = {}
    for acc in accounts:
        key = acc.account_type or "Unknown"
        account_type_dist[key] = account_type_dist.get(key, 0) + 1

    account_type_chart = [{"name": k, "value": v} for k, v in account_type_dist.items()]

    # ── 6. CUSTODIAN DISTRIBUTION (by value) ─────────────────────────────────
    custodian_value: dict[str, float] = {}
    for acc in accounts:
        key = acc.custodian or "Unknown"
        custodian_value[key] = custodian_value.get(key, 0) + _safe_float(acc.account_value)

    custodian_chart = [
        {"name": k, "value": round(v, 2)}
        for k, v in custodian_value.items()
        if v > 0
    ]
    # fallback to count if no values available
    if not custodian_chart:
        custodian_count: dict[str, int] = {}
        for acc in accounts:
            key = acc.custodian or "Unknown"
            custodian_count[key] = custodian_count.get(key, 0) + 1
        custodian_chart = [{"name": k, "value": v} for k, v in custodian_count.items()]

    # ── 7. OWNERSHIP DISTRIBUTION ─────────────────────────────────────────────
    ownership_dist: dict[str, float] = {}
    for acc in accounts:
        key = acc.ownership or "Unknown"
        ownership_dist[key] = ownership_dist.get(key, 0) + _safe_float(acc.account_value)

    ownership_chart = [
        {"name": k, "value": round(v, 2)}
        for k, v in ownership_dist.items()
        if v > 0
    ]

    # ── 8. BENEFICIARY ALLOCATION ─────────────────────────────────────────────
    # Shows how each beneficiary is allocated across accounts
    beneficiary_chart = []
    for b in beneficiaries:
        if b.name and b.percentage:
            beneficiary_chart.append({
                "name":         b.name,
                "percentage":   _safe_float(b.percentage),
                "type":         b.type or "Unknown",
                "relationship": b.relationship or "Unknown"
            })

    # ── 9. INVESTMENT EXPERIENCE RADAR ────────────────────────────────────────
    # Aggregate max years across all members per asset type
    exp_map: dict[str, int] = {}
    for exp in experiences:
        asset = exp.asset_type or "Unknown"
        exp_map[asset] = max(exp_map.get(asset, 0), exp.years or 0)

    experience_radar = [
        {"subject": k, "years": v}
        for k, v in exp_map.items()
        if v > 0
    ]

    # ── 10. MEMBER PROFILES ───────────────────────────────────────────────────
    members_list = []
    for m in members:
        age = _calc_age(m.dob)
        members_list.append({
            "name":           f"{m.first_name or ''} {m.last_name or ''}".strip(),
            "relationship":   m.relationship_type or "N/A",
            "age":            age,
            "dob":            str(m.dob) if m.dob else None,
            "email":          m.email,
            "phone":          m.phone,
            "occupation":     m.occupation or "N/A",
            "employer":       m.employer or "N/A",
            "marital_status": m.marital_status or "N/A",
            "city":           m.city,
            "state":          m.state,
        })

    # ── 11. INVESTMENT PROFILES PER ACCOUNT ───────────────────────────────────
    profile_map = {p.account_id: p for p in profiles}
    accounts_detail = []
    for acc in accounts:
        profile = profile_map.get(acc.id)
        accounts_detail.append({
            "account_type":       acc.account_type or "Unknown",
            "custodian":          acc.custodian or "Unknown",
            "account_value":      _safe_float(acc.account_value),
            "ownership":          acc.ownership or "N/A",
            "source_of_funds":    acc.source_of_funds or "N/A",
            "investment_objective": profile.objective if profile else "N/A",
            "risk_tolerance":     profile.risk_tolerance if profile else "N/A",
            "time_horizon":       profile.time_horizon if profile else "N/A",
            "liquidity_needs":    profile.liquidity_needs if profile else "N/A",
        })

    return {
        "summary":  summary,
        "charts": {
            "net_worth_breakdown":        net_worth_breakdown,
            "income_vs_networth":         income_vs_networth,
            "account_value_by_type":      account_value_chart,
            "account_type_distribution":  account_type_chart,
            "custodian_distribution":     custodian_chart,
            "ownership_distribution":     ownership_chart,
            "beneficiary_allocation":     beneficiary_chart,
            "investment_experience_radar": experience_radar,
        },
        "members":          members_list,
        "accounts_detail":  accounts_detail,
    }