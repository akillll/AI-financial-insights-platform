from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.db.session import SessionLocal
from app.models.household import Household

router = APIRouter(prefix="/households", tags=["Households"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- CREATE HOUSEHOLD ---------- #

@router.post("/")
def create_household(name: str, db: Session = Depends(get_db)):
    existing = db.query(Household).filter_by(name=name).first()

    if existing:
        return {"id": existing.id, "name": existing.name}

    household = Household(name=name)
    db.add(household)
    db.commit()
    db.refresh(household)

    return {"id": household.id, "name": household.name}


# ---------- GET ALL HOUSEHOLDS ---------- #

@router.get("/")
def get_households(db: Session = Depends(get_db)):
    households = db.query(Household).all()
    return households


# ---------- GET SINGLE HOUSEHOLD ---------- #

@router.get("/{household_id}")
def get_household(household_id: int, db: Session = Depends(get_db)):
    household = db.query(Household).options(
        selectinload(Household.members),
        selectinload(Household.accounts),
        selectinload(Household.bank_accounts),
    ).filter_by(id=household_id).first()

    if not household:
        raise HTTPException(status_code=404, detail="Household not found")

    total_account_value = sum(
        float(a.account_value or 0) for a in household.accounts
    )

    return {
        "id": household.id,
        "name": household.name,
        "annual_income": household.annual_income,
        "total_net_worth": household.total_net_worth,
        "liquid_net_worth": household.liquid_net_worth,
        "risk_tolerance": household.risk_tolerance,

        "summary": {
            "members_count": len(household.members),
            "accounts_count": len(household.accounts),
            "banks_count": len(household.bank_accounts),
            "total_account_value": total_account_value,
        },

        "members": [
            {
                "id": m.id,
                "name": f"{m.first_name or ''} {m.last_name or ''}".strip(),
                "relationship": m.relationship_type,
                "email": m.email,
                "phone": m.phone,
                "city": m.city,
            }
            for m in household.members
        ],

        "accounts": [
            {
                "id": a.id,
                "type": a.account_type,
                "value": a.account_value,
                "custodian": a.custodian,
                "ownership": a.ownership,
            }
            for a in household.accounts
        ],

        "banks": [
            {
                "id": b.id,
                "bank_name": b.bank_name,
                "account_number": b.account_number,
            }
            for b in household.bank_accounts
        ],
    }

