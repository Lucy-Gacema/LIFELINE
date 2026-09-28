import React from "react";


export default function ConfirmDialog({ open, title, description, confirmLabel = "Confirm", cancelLabel = "Cancel", danger = false, onConfirm, onCancel, children }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40 p-4" role="dialog" aria-modal="true" aria-labelledby="confirm-dialog-title">
      <div className="card w-full max-w-md p-6">
        <h2 id="confirm-dialog-title" className="text-xl font-bold mb-2">{title}</h2>
        {description && <p className="text-gray-600 mb-4">{description}</p>}
        {children}
        <div className="flex gap-3 mt-6">
          <button type="button" className="btn-secondary flex-1" onClick={onCancel} autoFocus>
            {cancelLabel}
          </button>
          <button type="button" className={danger ? "btn-danger flex-1" : "btn-primary flex-1"} onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
