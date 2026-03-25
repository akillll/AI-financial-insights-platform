from openai import OpenAI
import os
import json
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

COLUMN_MAPPING_CACHE = {}

STANDARD_FIELDS = [
    # ---------- HOUSEHOLD ----------
    "household_name",
    "annual_income",
    "total_net_worth",
    "liquid_net_worth",
    "expense_range",
    "tax_bracket",
    "risk_tolerance",
    "time_horizon",

    # ---------- MEMBER ----------
    "first_name",
    "last_name",
    "date_of_birth",
    "relationship",
    "email",
    "phone",
    "occupation",
    "employer",
    "marital_status",
    "address",
    "city",
    "state",
    "country",

    # ---------- INVESTMENT EXPERIENCE ----------
    "years_of_experience_bonds",
    "years_of_experience_stocks",
    "years_of_experience_alternatives",
    "years_of_experience_vas",
    "years_of_experience_mutual_funds",
    "years_of_experience_options",
    "years_of_experience_partnerships",

    # ---------- ACCOUNT ----------
    "account_number",
    "account_type",
    "custodian",
    "account_value",
    "ownership",
    "ownership_percentage",
    "decision_making",
    "source_of_funds",

    # ---------- BANK ----------
    "bank_name",
    "bank_account_number",
    "bank_account_type",
    "routing_number",

    # ---------- INVESTMENT PROFILE ----------
    "investment_objective",
    "liquidity_needs",

    # ---------- BENEFICIARY ----------
    "beneficiary_1_name",
    "beneficiary_1_relationship",
    "beneficiary_1_type",
    "beneficiary_1_percentage",
    "beneficiary_1_dob",
    "beneficiary_2_name",
    "beneficiary_2_relationship",
    "beneficiary_2_type",
    "beneficiary_2_percentage",
    "beneficiary_2_dob",

    "unknown"
]


def build_prompt(headers):
    return f"""
Map these Excel column headers to the closest standard schema field.

Headers:
{headers}

Allowed fields:
{STANDARD_FIELDS}

Rules:
- Return ONLY a flat JSON object
- One header maps to one field
- Use "unknown" if nothing fits
- Do not hallucinate field names outside the allowed list
- For numbered beneficiaries, map to beneficiary_1_* or beneficiary_2_* fields
- For investment experience, map years/experience columns to years_of_experience_* fields

Example:
{{
  "Client Name": "household_name",
  "DOB": "date_of_birth",
  "AUM": "account_value",
  "Beneficiary 1 Name": "beneficiary_1_name",
  "Years Exp Bonds": "years_of_experience_bonds"
}}
"""


def call_ai(prompt, retries=3):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                response_format={"type": "json_object"},  # FIX: guarantees valid JSON, no backtick stripping needed
                messages=[
                    {
                        "role": "system",
                        "content": "You map Excel column names to schema fields. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"Column mapping AI error (attempt {attempt + 1}):", e)
            time.sleep(1)

    print("Column mapping failed, using identity fallback")
    return None


def get_column_mapping(headers):
    key = tuple(sorted(headers))

    if key in COLUMN_MAPPING_CACHE:
        return COLUMN_MAPPING_CACHE[key]

    mapping = call_ai(build_prompt(headers))

    if not mapping:
        mapping = {h: h for h in headers}

    COLUMN_MAPPING_CACHE[key] = mapping
    return mapping


def apply_column_mapping(df):
    headers = list(df.columns)
    mapping = get_column_mapping(headers)

    rename_dict = {}
    for col in headers:
        mapped = mapping.get(col)
        if mapped and mapped != "unknown":
            rename_dict[col] = mapped

    df = df.rename(columns=rename_dict)
    return df, mapping