export default function Filters({ setFilter }) {
  return (
    <div className="flex gap-2">
      <button onClick={() => setFilter("all")}>All</button>
      <button onClick={() => setFilter("high_net")}>High Net Worth</button>
    </div>
  );
}