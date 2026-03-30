"use client";

import type { ModelInfo } from "@/types";

interface ModelSelectorProps {
  models: ModelInfo[];
  selectedModel: string;
  onSelect: (modelId: string) => void;
  disabled?: boolean;
}

export function ModelSelector({
  models,
  selectedModel,
  onSelect,
  disabled,
}: ModelSelectorProps) {
  return (
    <select
      value={selectedModel}
      onChange={(e) => onSelect(e.target.value)}
      disabled={disabled}
      className="rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-sm outline-none transition-colors focus:border-blue-500 disabled:opacity-50 dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-100"
    >
      {models.map((model) => (
        <option key={model.id} value={model.id}>
          {model.label}
        </option>
      ))}
    </select>
  );
}
