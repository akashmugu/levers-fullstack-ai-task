"use client";

interface StreamToggleProps {
  streaming: boolean;
  onToggle: (streaming: boolean) => void;
  disabled?: boolean;
}

export function StreamToggle({ streaming, onToggle, disabled }: StreamToggleProps) {
  return (
    <button
      onClick={() => onToggle(!streaming)}
      disabled={disabled}
      className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm transition-colors disabled:opacity-50 ${
        streaming
          ? "border-blue-300 bg-blue-50 text-blue-700 dark:border-blue-600 dark:bg-blue-900/30 dark:text-blue-300"
          : "border-zinc-300 bg-white text-zinc-600 dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"
      }`}
      title={streaming ? "Streaming enabled" : "Streaming disabled"}
    >
      <div
        className={`h-2 w-2 rounded-full ${
          streaming ? "animate-pulse bg-blue-500" : "bg-zinc-400"
        }`}
      />
      {streaming ? "Stream" : "Batch"}
    </button>
  );
}
