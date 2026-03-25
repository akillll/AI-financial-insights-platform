import { Link, useLocation } from "react-router-dom";
import { Upload, Users, Smile } from "lucide-react";

export default function Sidebar() {
  const { pathname } = useLocation();

  const navItems = [
    { name: "Upload", path: "/", icon: Upload },
    { name: "Households", path: "/households", icon: Users },
  ];

  return (
    <div className="h-screen w-64 bg-[#0f172a] text-white flex flex-col border-r border-white/10">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-white/10 text-center">
        <h1 className="text-xl font-semibold tracking-tight">
          <span className="text-green-400">Fast</span>Trackr
        </h1>
        <p className="text-xs text-gray-400 mt-1">
          AI Processing Suite
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.path;

          return (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200
                ${
                  isActive
                    ? "bg-white/10 text-white"
                    : "text-gray-400 hover:bg-white/5 hover:text-white"
                }`}
            >
              <Icon size={18} />
              {item.name}
            </Link>
          );
        })}
      </nav>

  <div className="p-4 border-t border-white/10">
  <div className="flex items-center justify-between bg-white/5 rounded-lg p-3 text-sm text-gray-300 hover:bg-white/10 transition-all">
    
    {/* Left: Text */}
    <div>
      <p className="text-xs text-gray-400">Built by</p>
      <p className="text-white font-medium leading-tight">
        Akhil Mohandas
      </p>
    </div>

    {/* Right: Avatar */}
    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center shadow-md">
      <Smile size={18} className="text-black" />
    </div>

  </div>
  </div>
    </div>    
  );
}