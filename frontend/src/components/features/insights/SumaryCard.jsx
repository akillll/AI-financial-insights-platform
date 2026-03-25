import { Card } from "../../base/Card";

export default function SummaryCards({ summary }) {
  return (
    <div className="grid grid-cols-3 gap-4">
      {Object.entries(summary).map(([key, value]) => (
        <Card key={key}>
          <p className="text-xs text-gray-500">{key}</p>
          <p className="font-semibold">{value}</p>
        </Card>
      ))}
    </div>
  );
}