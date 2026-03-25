import { useState } from "react";
import { uploadExcel } from "../../../services/api";
import { Button } from "../../base";
import { UploadCloud, FileSpreadsheet, X } from "lucide-react";
import Loader from "../../base/Loader";
import SuccessModal from "../../base/SuccessModal";

export default function ExcelUpload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successData, setSuccessData] = useState(null);

  const validate = () => {
    if (!file) return "Upload an Excel file";
    if (!file.name.endsWith(".xlsx") && !file.name.endsWith(".xls")) {
      return "Only Excel files allowed";
    }
    return null;
  };

  const handleUpload = async () => {
    const err = validate();
    if (err) return setError(err);

    setError("");
    setLoading(true);

    try {
      const res = await uploadExcel(file);

      // 👇 capture households list from response
      setSuccessData(res.data.households_processed);

      setFile(null);
    } catch (e) {
      setError(e.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) setFile(droppedFile);
  };

  return (
    <div className="space-y-6">

      {/* Upload Area */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-green-500 transition-all bg-gray-50 cursor-pointer"
        onClick={() => document.getElementById("fileUpload").click()}
      >
        <UploadCloud className="mx-auto text-gray-400 mb-3" size={36} />

        <p className="text-sm text-gray-600">
          Drag & drop your Excel file here
        </p>
        <p className="text-xs text-gray-400 mt-1">
          or click to browse (.xlsx, .xls)
        </p>

        <input
          type="file"
          accept=".xlsx,.xls"
          onChange={(e) => setFile(e.target.files[0])}
          className="hidden"
          id="fileUpload"
        />
      </div>

      {/* File Preview */}
      {file && (
        <div className="flex items-center justify-between border border-gray-200 rounded-lg p-3 bg-white shadow-sm">
          <div className="flex items-center gap-3">
            <FileSpreadsheet className="text-green-600" />
            <div>
              <p className="text-sm font-medium text-gray-800">
                {file.name}
              </p>
              <p className="text-xs text-gray-400">
                {(file.size / 1024).toFixed(1)} KB
              </p>
            </div>
          </div>

          <button
            onClick={() => setFile(null)}
            className="text-gray-400 hover:text-red-500 transition"
          >
            <X size={18} />
          </button>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">
          {error}
        </div>
      )}

      {/* Action */}
      <div className="flex justify-end">
        <Button onClick={handleUpload} loading={loading}>
          Upload & Process
        </Button>
      </div>

      {/* Loader */}
      {loading && <Loader text="Processing Excel file..." />}

      {/* Success Modal */}
      {successData && (
        <SuccessModal
          title="Upload Successful"
          message="Excel processed successfully. The following households were created:"
          data={successData}
          onClose={() => setSuccessData(null)}
          showRedirect={true}
        />
      )}
    </div>
  );
}