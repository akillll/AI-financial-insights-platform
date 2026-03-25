import { useEffect, useState, useRef } from "react";
import {
  extractAudio,
  confirmAudio,
  getHouseholds,
} from "../../../services/api";
import DynamicForm from "./DynamicForm";
import { Button, Input, Loader } from "../../base";
import { ChevronDown, ChevronUp } from "lucide-react";
import SuccessModal from "../../base/SuccessModal";

export default function AudioUpload() {
  const [file, setFile] = useState(null);
  const [householdId, setHouseholdId] = useState("");
  const [households, setHouseholds] = useState([]);
  const [originalData, setOriginalData] = useState(null)
  const [data, setData] = useState(null);
  const [transcript, setTranscript] = useState("");
  const [expanded, setExpanded] = useState(false);
  const fileInputRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    getHouseholds()
      .then(setHouseholds)
      .catch(() => setError("Failed to load households"));
  }, []);

  const handleExtract = async () => {
    if (!householdId) return setError("Please select a household");
    if (!file) return setError("Please upload an audio file");

    setError("");
    setLoading(true);

    try {
      const res = await extractAudio(file, householdId);
      setData(res);
      setOriginalData(res);
      setTranscript(res.transcript);
    } catch (e) {
      setError("Audio extraction failed");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!data || typeof data !== "object") {
      setError("Invalid data format");
      return;
    }

    setError("");
    setLoading(true);

    try {
      await confirmAudio(data, householdId);

      setSuccess(true);
    } catch (e) {
      setError("Save failed");
    } finally {
      setLoading(false);
    }
  };

  const resetAll = () => {
    setFile(null);
    setHouseholdId("");
    setData(null);
    setTranscript("");
    setExpanded(false);
    setError("");
    setSuccess(false);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const selectedHousehold = households.find(
    (h) => String(h.id) === String(householdId),
  );

  return (
    <div className="space-y-6">
      {/* Top Controls */}
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <label className="text-xs text-gray-500">Household</label>
          <select
            className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 outline-none"
            value={householdId}
            onChange={(e) => setHouseholdId(e.target.value)}
          >
            <option value="">Select Household</option>
            {households.map((h) => (
              <option key={h.id} value={h.id}>
                {h.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs text-gray-500">Audio File</label>
          <Input
            ref={fileInputRef}
            type="file"
            accept="audio/*"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>
      </div>

      {/* Action */}
      <div className="flex justify-end">
        <Button onClick={handleExtract} loading={loading}>
          Extract Data
        </Button>
      </div>

      {/* Error */}
      {error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">
          {error}
        </div>
      )}

      {/* Loader */}
      {loading && <Loader text="Processing audio..." />}

      {/* Transcript */}
      {transcript && (
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Transcript
            </p>

            <button
              onClick={() => setExpanded(!expanded)}
              className="text-xs flex items-center gap-1 text-gray-500 hover:text-gray-800"
            >
              {expanded ? "Show less" : "Show more"}
              {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
          </div>

          <div
            className={`text-xs text-gray-600 leading-relaxed ${
              expanded ? "max-h-none" : "max-h-24 overflow-hidden"
            }`}
          >
            {transcript}
          </div>
        </div>
      )}

      {/* Extracted Data */}
      {data && (
        <div className="space-y-4">
          <h2 className="text-md font-semibold text-gray-800">
            Extracted Data
          </h2>

          <div className="border border-gray-200 rounded-xl p-4 bg-white shadow-sm">
            <DynamicForm data={data} setData={setData} originalData={originalData} />
          </div>

          <div className="flex justify-end">
            <Button onClick={handleConfirm} loading={loading}>
              Confirm & Save
            </Button>
          </div>
        </div>
      )}

      {success && (
        <SuccessModal
          title="Saved Successfully"
          message={`Data saved for ${selectedHousehold?.name || "household"}`}
          data={[]}
          onClose={resetAll}
        />
      )}
    </div>
  );
}
