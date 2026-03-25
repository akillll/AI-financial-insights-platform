import { Card } from "../../base/Card";

export default function HouseholdCard({ data, onClick }) {
  return (
    <Card>
      <div
        className="cursor-pointer hover:bg-green-50 p-2 rounded"
        onClick={onClick}
      >
        <h3 className="font-semibold">{data.name}</h3>
        <p className="text-sm text-gray-500">ID: {data.id}</p>
      </div>
    </Card>
  );
}