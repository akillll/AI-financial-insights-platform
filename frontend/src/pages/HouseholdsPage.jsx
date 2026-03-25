import MainLayout from "../components/layout/MainLayout";
import { useEffect, useState } from "react";
import { getHouseholds } from "../services/api";
import { useNavigate } from "react-router-dom";
import { Users } from "lucide-react";

export default function HouseholdsPage() {
  const [data, setData] = useState([]);
  const nav = useNavigate();

  useEffect(() => {
    getHouseholds().then(setData);
  }, []);

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Households</h1>
            <p className="text-sm text-gray-500 mt-1">
              View and manage all processed households
            </p>
          </div>

          <div className="text-sm text-gray-400">{data.length} total</div>
        </div>

        {/* Empty State */}
        {data.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <Users className="text-gray-300 mb-3" size={40} />
            <p className="text-gray-600 text-sm">No households found</p>
            <p className="text-gray-400 text-xs mt-1">
              Upload an Excel file to get started
            </p>
          </div>
        )}

        {/* Grid */}
        {data.length > 0 && (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.map((h) => (
              <div
                key={h.id}
                onClick={() => nav(`/household/${h.id}`)}
                className="cursor-pointer border border-gray-200 rounded-xl p-4 bg-white shadow-sm 
  hover:shadow-md hover:border-green-500 hover:-translate-y-0.5 transition-all group"
              >
                <div className="flex items-center justify-between">
                  {/* Left */}
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-green-100 text-green-700 flex items-center justify-center font-semibold text-sm">
                      {h.name?.[0] || "H"}
                    </div>

                    <div>
                      <p className="text-sm font-medium text-gray-900 group-hover:text-green-600 transition">
                        {h.name}
                      </p>
                      <p className="text-xs text-gray-400">ID: {h.id}</p>
                    </div>
                  </div>

                  {/* Right CTA */}
                  <div className="flex items-center gap-1 text-xs text-gray-400 opacity-0 group-hover:opacity-100 transition">
                    View Details
                    <span className="translate-x-0 group-hover:translate-x-1 transition">
                      →
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
