import React from "react";

export default function ErrorBanner({ message, onDismiss }) {
  if (!message) return null;
  return (
    <div role="alert" className="flex items-start gap-3 rounded-xl bg-red-50 border border-red-200 text-red-800 px-4 py-3 mb-4">
      <span aria-hidden="true" className="text-xl leading-none">⚠️</span>
      <p className="flex-1 text-sm">{message}</p>
      {onDismiss && (
        <button type="button" onClick={onDismiss} className="text-red-600 hover:text-red-800 font-bold" aria-label="Dismiss">
          ×
        </button>
      )}
    </div>
  );
}
