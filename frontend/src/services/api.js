// const BASE_URL = "http://localhost:8000";

const BASE_URL = "https://ai-financial-insights-platform.onrender.com";

export const uploadExcel = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/upload/excel`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("Excel upload failed");
  return res.json();
};

export const extractAudio = async (file, householdId) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/audio/${householdId}/extract`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("Audio extract failed");
  return res.json();
  // Response shape (ExtractResponse):
  // {
  //   transcript, household_id,
  //   annual_income, total_net_worth, liquid_net_worth,
  //   expense_range, tax_bracket, risk_tolerance, time_horizon,
  //   member: { id, first_name, last_name, ..., investment_experiences: [{ id, asset_type, years }] },
  //   accounts: [{ id, account_type, custodian, ..., investment_profile: {...}, beneficiaries: [{ id, ... }] }],
  //   bank_accounts: [{ id, bank_name, account_number, ... }]
  // }
};

/**
 * buildConfirmPayload
 *
 * Converts the ExtractResponse (as edited by the advisor in the UI) into the
 * AudioConfirmPayload shape the backend expects on PUT /confirm.
 *
 * Key rules:
 *  - Household fields are passed flat (no id needed — keyed by URL param)
 *  - member_id comes from data.member.id
 *  - Member fields are promoted to top level
 *  - investment_experiences, accounts, bank_accounts stay as arrays with their ids
 *  - Beneficiaries stay nested inside their account with their ids
 */
export const buildConfirmPayload = (data) => {
  const { member, accounts, bank_accounts, ...householdFields } = data;

  // Strip non-household keys that live in ExtractResponse but aren't payload fields
  const { transcript, household_id, ...householdOnly } = householdFields;

  return {
    // Household-level fields
    ...householdOnly,

    // Member — promoted to top level with member_id
    ...(member && {
      member_id:      member.id,
      first_name:     member.first_name,
      last_name:      member.last_name,
      legal_name:     member.legal_name,
      relationship:   member.relationship,
      dob:            member.dob,
      occupation:     member.occupation,
      employer:       member.employer,
      marital_status: member.marital_status,
      phone:          member.phone,
      email:          member.email,
      address:        member.address,
      city:           member.city,
      state:          member.state,
      country:        member.country,
      investment_experiences: member.investment_experiences?.map((exp) => ({
        id:         exp.id,   // present → UPDATE; absent → INSERT
        asset_type: exp.asset_type,
        years:      exp.years,
      })),
    }),

    // Accounts — each with id so backend does UPDATE, not INSERT
    accounts: accounts?.map((acct) => ({
      id:                   acct.id,
      account_number:       acct.account_number,
      account_type:         acct.account_type,
      custodian:            acct.custodian,
      account_value:        acct.account_value,
      ownership:            acct.ownership,
      ownership_percentage: acct.ownership_percentage,
      decision_making:      acct.decision_making,
      source_of_funds:      acct.source_of_funds,
      investment_objective: acct.investment_profile?.objective,
      liquidity_needs:      acct.investment_profile?.liquidity_needs,
      beneficiaries:        acct.beneficiaries?.map((b) => ({
        id:           b.id,
        name:         b.name,
        relationship: b.relationship,
        type:         b.type,
        percentage:   b.percentage,
        dob:          b.dob,
      })),
    })),

    // Bank accounts — each with id
    bank_accounts: bank_accounts?.map((b) => ({
      id:             b.id,
      bank_name:      b.bank_name,
      account_number: b.account_number,
      account_type:   b.account_type,
      routing_number: b.routing_number,
    })),
  };
};

export const confirmAudio = async (data, householdId) => {
  const payload = buildConfirmPayload(data);

  const res = await fetch(`${BASE_URL}/audio/${householdId}/confirm`, {
    method: "PUT",                                   
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error("Confirm failed");
  return res.json();
};

export const getHouseholds = async () => {
  const res = await fetch(`${BASE_URL}/households/`);
  if (!res.ok) throw new Error("Fetch households failed");
  return res.json();
};

export const getHousehold = async (id) => {
  const res = await fetch(`${BASE_URL}/households/${id}`);
  if (!res.ok) throw new Error("Fetch household failed");
  return res.json();
};

export const getInsights = async (id) => {
  const res = await fetch(`${BASE_URL}/insights/${id}`);
  if (!res.ok) throw new Error("Fetch insights failed");
  return res.json();
};