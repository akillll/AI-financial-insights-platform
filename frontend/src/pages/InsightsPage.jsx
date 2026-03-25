import MainLayout from "../components/layout/MainLayout";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getInsights } from "../services/api";
import Charts from "../components/features/insights/Charts";
import { BarChart3 } from "lucide-react";
import Loader from "../components/base/Loader";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export default function InsightsPage() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const nav = useNavigate();

  useEffect(() => {
    getInsights(id).then(setData);
  }, [id]);

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto space-y-6">
        <button
          onClick={() => nav("/households")}
          className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-900 transition"
        >
          <ArrowLeft size={16} />
          Back to Households
        </button>

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
              <BarChart3 size={22} />
              Insights Dashboard
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              Household analytics and financial insights
            </p>
          </div>

          <div className="text-xs text-gray-400">ID: {id}</div>
        </div>

        {/* Loading State */}
        {!data && (
          <div className="flex items-center justify-center py-20">
            <Loader text="Loading insights..." />
          </div>
        )}

        {/* Content */}
        {data && (
          <div className="space-y-6">
            {/* Charts Card */}
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
              <h2 className="text-sm font-semibold text-gray-800 mb-4">
                Analytics Overview
              </h2>

              <Charts charts={data.charts} />
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
