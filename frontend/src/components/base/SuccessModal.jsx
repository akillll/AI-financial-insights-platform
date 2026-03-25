import { CheckCircle2, X } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Button from "./Button";

export default function SuccessModal({
  title = "Success",
  message = "",
  data = [],
  onClose,
  showRedirect = false,
}) {
  const navigate = useNavigate();

  if (!data) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      
      <div className="bg-white w-[440px] max-h-[80vh] rounded-2xl shadow-xl p-6 flex flex-col">
        
        {/* Header */}
        <div className="flex justify-between items-start">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="text-green-500" size={22} />
            <h2 className="text-lg font-semibold text-gray-900">
              {title}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-700"
          >
            <X size={18} />
          </button>
        </div>

        {/* Message */}
        <p className="text-sm text-gray-500 mt-2">
          {message}
        </p>

        {/* Data List */}
        {data.length > 0 && (
          <div className="mt-4 overflow-y-auto border border-gray-200 rounded-lg p-3 bg-gray-50 space-y-2">
            {data.map((item, i) => (
              <div
                key={i}
                className="text-sm text-gray-700 px-2 py-1 rounded hover:bg-gray-100"
              >
                {item}
              </div>
            ))}
          </div>
        )}

        {/* Footer */}
        <div className="mt-5 flex justify-between items-center gap-2">
          
          {showRedirect && (
            <Button
              variant="secondary"
              onClick={() => {
                onClose();
                navigate("/households");
              }}
            >
              Go to Households →
            </Button>
          )}

          <div className="ml-auto">
            <Button onClick={onClose}>
              Done
            </Button>
          </div>

        </div>
      </div>
    </div>
  );
}