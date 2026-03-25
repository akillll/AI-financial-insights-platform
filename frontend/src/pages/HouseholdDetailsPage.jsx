import MainLayout from "../components/layout/MainLayout";
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getHousehold } from "../services/api";
import Loader from "../components/base/Loader";
import { ArrowLeft } from "lucide-react";

export default function HouseholdDetailsPage() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const nav = useNavigate();

  useEffect(() => {
    getHousehold(id).then(setData);
  }, [id]);

  if (!data) {
    return (
      <MainLayout>
        <div className="flex justify-center py-20">
          <Loader text="Loading household..." />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Back */}
        <button
          onClick={() => nav("/households")}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-900"
        >
          <ArrowLeft size={16} />
          Back to Households
        </button>

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">
              {data.name}
            </h1>
            <p className="text-sm text-gray-500">
              Household Overview & Financial Summary
            </p>
          </div>

          <button
            onClick={() => nav(`/insights/${id}`)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 transition"
          >
            View Insights →
          </button>
        </div>

        {/* Summary Cards */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card title="Members" value={data.summary.members_count} />
          <Card title="Accounts" value={data.summary.accounts_count} />
          <Card title="Banks" value={data.summary.banks_count} />
          <Card
            title="Total Value"
            value={`₹${data.summary.total_account_value || 0}`}
          />
        </div>

        {/* Members */}
        <Section title="Members">
          {data.members.map((m) => (
            <div
              key={m.id}
              className="border rounded-lg p-3 flex justify-between"
            >
              <div>
                <p className="text-sm font-medium">{m.name}</p>
                <p className="text-xs text-gray-500">{m.relationship}</p>
              </div>
              <div className="text-xs text-gray-400">{m.city}</div>
            </div>
          ))}
        </Section>

        {/* Accounts */}
        <Section title="Accounts">
          {data.accounts.map((a) => (
            <div
              key={a.id}
              className="border rounded-lg p-3 flex justify-between"
            >
              <div>
                <p className="text-sm font-medium">{a.type}</p>
                <p className="text-xs text-gray-500">{a.custodian}</p>
              </div>
              <div className="text-sm font-semibold">
                ₹{a.value || 0}
              </div>
            </div>
          ))}
        </Section>

        {/* Banks */}
        <Section title="Bank Accounts">
          {data.banks.map((b) => (
            <div
              key={b.id}
              className="border rounded-lg p-3 flex justify-between"
            >
              <p className="text-sm font-medium">{b.bank_name}</p>
              <p className="text-xs text-gray-400">
                ****{b.account_number?.slice(-4)}
              </p>
            </div>
          ))}
        </Section>
      </div>
    </MainLayout>
  );
}

/* Reusable Components */

function Card({ title, value }) {
  return (
    <div className="bg-white border rounded-xl p-4 shadow-sm">
      <p className="text-xs text-gray-500">{title}</p>
      <p className="text-lg font-semibold text-gray-900 mt-1">{value}</p>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="bg-white border rounded-xl p-4 shadow-sm space-y-3">
      <h2 className="text-sm font-semibold text-gray-800">{title}</h2>
      {children}
    </div>
  );
}