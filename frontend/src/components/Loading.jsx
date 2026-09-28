import React from "react";

export default function Loading({ label = "Loading…" }) {
  return (
    <div className="flex items-center justify-center gap-3 py-16 text-gray-500" role="status" aria-live="polite">
      <span className="h-5 w-5 rounded-full border-2 border-gray-300 border-t-brand-600 animate-spin" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
