import Sidebar from "./Sidebar";

export default function MainLayout({ children }) {
  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <Sidebar />

      <div className="flex-1 overflow-y-auto">
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}