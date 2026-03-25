export default function Loader({ text = "Processing your file..." }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      
      {/* Card */}
      <div className="bg-white rounded-2xl shadow-xl px-8 py-10 flex flex-col items-center gap-5 w-[320px]">
        
        {/* Logo */}
        <div className="text-center">
          <h1 className="text-xl font-semibold tracking-tight">
            <span className="text-green-500">Fast</span>Trackr
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            AI-powered data processing
          </p>
        </div>

        {/* Spinner */}
        <div className="relative">
          <div className="h-12 w-12 rounded-full border-4 border-gray-200"></div>
          <div className="absolute inset-0 h-12 w-12 rounded-full border-4 border-green-500 border-t-transparent animate-spin"></div>
        </div>

        {/* Text */}
        <p className="text-sm text-gray-600 text-center">
          {text}
        </p>
      </div>
    </div>
  );
}