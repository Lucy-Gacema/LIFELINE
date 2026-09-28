import React from "react";


export default function NumericKeypad({ onDigit, onBackspace, onClear, disabled }) {
  const keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "clear", "0", "back"];
  return (
    <div className="grid grid-cols-3 gap-3 w-full max-w-xs mx-auto">
      {keys.map((k) => {
        if (k === "clear") {
          return (
            <button key="clear" type="button" disabled={disabled} onClick={onClear} className="btn-secondary text-lg" aria-label="Clear">
              Clear
            </button>
          );
        }
        if (k === "back") {
          return (
            <button key="back" type="button" disabled={disabled} onClick={onBackspace} className="btn-secondary text-lg" aria-label="Backspace">
              ⌫
            </button>
          );
        }
        return (
          <button
            key={k}
            type="button"
            disabled={disabled}
            onClick={() => onDigit(k)}
            className="btn-secondary text-2xl font-bold aspect-square"
          >
            {k}
          </button>
        );
      })}
    </div>
  );
}
