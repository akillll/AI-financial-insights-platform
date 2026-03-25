import { Loader2 } from "lucide-react";

export default function Button({
  children,
  variant = "primary",
  loading = false,
  disabled = false,
  className = "",
  ...props
}) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-xl text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2";

  const variants = {
    primary:
      "bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 shadow-sm",
    secondary:
      "bg-gray-100 text-gray-800 hover:bg-gray-200 focus:ring-gray-400",
    ghost:
      "bg-transparent text-gray-600 hover:bg-gray-100 focus:ring-gray-300",
    danger:
      "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
  };

  return (
    <button
      className={`${base} ${variants[variant]} px-4 py-2 ${
        disabled || loading ? "opacity-60 cursor-not-allowed" : ""
      } ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 className="animate-spin" size={16} />}
      {children}
    </button>
  );
}