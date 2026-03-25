import { useState } from "react";
import MainLayout from "../components/layout/MainLayout";
import ExcelUpload from "../components/features/upload/ExcelUpload";
import AudioUpload from "../components/features/upload/AudioUpload";
import { FileSpreadsheet, Mic } from "lucide-react";

export default function UploadPage() {
  const [tab, setTab] = useState("excel");

  return (
    <MainLayout>
      <div className="max-w-5xl mx-auto py-6 px-4 space-y-6">
        
        {/* Header */}
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            Upload Data
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Upload your Excel sheets or audio files to process and extract structured data.
          </p>
        </div>

        {/* Tabs (Modern Pill Style) */}
        <div className="inline-flex bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setTab("excel")}
            className={`flex items-center gap-2 px-4 py-2 text-sm rounded-md transition-all
              ${
                tab === "excel"
                  ? "bg-white shadow-sm text-gray-900"
                  : "text-gray-500 hover:text-gray-800"
              }`}
          >
            <FileSpreadsheet size={16} />
            Excel
          </button>

          <button
            onClick={() => setTab("audio")}
            className={`flex items-center gap-2 px-4 py-2 text-sm rounded-md transition-all
              ${
                tab === "audio"
                  ? "bg-white shadow-sm text-gray-900"
                  : "text-gray-500 hover:text-gray-800"
              }`}
          >
            <Mic size={16} />
            Audio
          </button>
        </div>

        {/* Content Card */}
        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6">
          {tab === "excel" ? <ExcelUpload /> : <AudioUpload />}
        </div>
      </div>
    </MainLayout>
  );
}