import {
  PieChart, Pie, Tooltip, Cell,
  BarChart, Bar, XAxis, YAxis,
  RadarChart, PolarGrid, PolarAngleAxis, Radar,
  ResponsiveContainer,
} from "recharts";

const COLORS = ["#22c55e", "#16a34a", "#4ade80", "#86efac", "#bbf7d0"];

function ChartCard({ title, children }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-gray-800 mb-3">
        {title}
      </h3>
      <div className="h-[280px]">{children}</div>
    </div>
  );
}

// ---------- GENERIC CHART RENDERERS ---------- //

const PieBlock = ({ data }) => (
  <ResponsiveContainer width="100%" height="100%">
    <PieChart>
      <Pie
        data={data}
        dataKey="value"
        nameKey="name"
        innerRadius={60}
        outerRadius={90}
        paddingAngle={3}
      >
        {data.map((_, i) => (
          <Cell key={i} fill={COLORS[i % COLORS.length]} />
        ))}
      </Pie>
      <Tooltip />
    </PieChart>
  </ResponsiveContainer>
);

const BarBlock = ({ data }) => (
  <ResponsiveContainer width="100%" height="100%">
    <BarChart data={data}>
      <XAxis dataKey="name" stroke="#9ca3af" />
      <YAxis stroke="#9ca3af" />
      <Tooltip />
      <Bar dataKey="value" fill="#22c55e" radius={[6, 6, 0, 0]} />
    </BarChart>
  </ResponsiveContainer>
);

const RadarBlock = ({ data }) => (
  <ResponsiveContainer width="100%" height="100%">
    <RadarChart data={data}>
      <PolarGrid stroke="#e5e7eb" />
      <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10 }} />
      <Radar
        dataKey="years"
        stroke="#16a34a"
        fill="#22c55e"
        fillOpacity={0.5}
      />
    </RadarChart>
  </ResponsiveContainer>
);

// ---------- MAIN ---------- //

export default function Charts({ charts }) {
  if (!charts) return null;

  const chartConfig = [
    {
      key: "net_worth_breakdown",
      title: "Net Worth Breakdown",
      type: "pie",
    },
    {
      key: "income_vs_networth",
      title: "Income vs Net Worth",
      type: "bar",
    },
    {
      key: "account_value_by_type",
      title: "Account Value by Type",
      type: "pie",
    },
    {
      key: "account_type_distribution",
      title: "Account Type Distribution",
      type: "bar",
    },
    {
      key: "custodian_distribution",
      title: "Custodian Distribution",
      type: "pie",
    },
    {
      key: "ownership_distribution",
      title: "Ownership Distribution",
      type: "pie",
    },
    {
      key: "beneficiary_allocation",
      title: "Beneficiary Allocation (%)",
      type: "bar",
      dataKey: "percentage", // special case
    },
    {
      key: "investment_experience_radar",
      title: "Investment Experience",
      type: "radar",
    },
  ];

  return (
    <div className="grid md:grid-cols-2 gap-6">
      {chartConfig.map((cfg) => {
        const data = charts[cfg.key];

        if (!data || data.length === 0) return null;

        // handle special dataKey (beneficiary chart)
        const normalizedData =
          cfg.dataKey === "percentage"
            ? data.map((d) => ({
                name: d.name,
                value: d.percentage,
              }))
            : data;

        return (
          <ChartCard key={cfg.key} title={cfg.title}>
            {cfg.type === "pie" && <PieBlock data={normalizedData} />}
            {cfg.type === "bar" && <BarBlock data={normalizedData} />}
            {cfg.type === "radar" && <RadarBlock data={normalizedData} />}
          </ChartCard>
        );
      })}
    </div>
  );
}