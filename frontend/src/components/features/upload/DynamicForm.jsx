import React from "react";

const isObject = (val) =>
  typeof val === "object" && val !== null && !Array.isArray(val);

const formatLabel = (key) =>
  key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

export default function DynamicForm({ data, setData, originalData }) {
  if (!data) return null;

  const updateValue = (path, value) => {
    const keys = path.split(".");
    const newData = structuredClone(data);

    let curr = newData;

    for (let i = 0; i < keys.length - 1; i++) {
      curr = Array.isArray(curr)
        ? curr[parseInt(keys[i])]
        : curr[keys[i]];
    }

    const lastKey = keys[keys.length - 1];

    if (Array.isArray(curr)) {
      curr[parseInt(lastKey)] = value;
    } else {
      curr[lastKey] = value;
    }

    setData(newData);
  };

  const getValueFromPath = (obj, path) => {
    if (!obj) return undefined;

    return path.split(".").reduce((acc, key) => {
      if (!acc) return undefined;

      return Array.isArray(acc)
        ? acc[parseInt(key)]
        : acc[key];
    }, obj);
  };

  const renderField = (key, value, path) => {
    if (key === "id") return null;

    const originalValue = getValueFromPath(originalData, path);

    const isAIValue =
      originalValue !== undefined &&
      originalValue !== null &&
      originalValue !== "" &&
      value === originalValue;

    // ---------- PRIMITIVE ----------
    if (!isObject(value) && !Array.isArray(value)) {
      return (
        <div key={path} className="space-y-1">
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-gray-500">
              {formatLabel(key)}
            </label>

            {isAIValue && (
              <span className="text-[10px] bg-green-50 text-green-600 px-2 py-0.5 rounded-full border border-green-200">
                AI Extracted
              </span>
            )}
          </div>

          <input
            className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm 
            focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent
            transition-all"
            value={value || ""}
            onChange={(e) => updateValue(path, e.target.value)}
          />
        </div>
      );
    }

    // ---------- ARRAY ----------
    if (Array.isArray(value)) {
      if (value.length === 0) return null;

      return (
        <div key={path} className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-800">
              {formatLabel(key)}
            </h3>
            <span className="text-xs text-gray-400">
              {value.length} items
            </span>
          </div>

          <div className="space-y-3">
            {value.map((item, index) => (
              <div
                key={index}
                className="rounded-xl border border-gray-200 bg-gray-50 p-4 shadow-sm"
              >
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(item).map(([k, v]) =>
                    renderField(k, v, `${path}.${index}.${k}`)
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // ---------- OBJECT ----------
    return (
      <div key={path} className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">
            {formatLabel(key)}
          </h3>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(value).map(([k, v]) =>
              renderField(k, v, `${path}.${k}`)
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {Object.entries(data).map(([key, value]) =>
        renderField(key, value, key)
      )}
    </div>
  );
}