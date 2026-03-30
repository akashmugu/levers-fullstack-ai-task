"use client";

import { useEffect, useState } from "react";
import type { ModelInfo } from "@/types";
import { fetchModels } from "@/lib/api";

export function useModels() {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchModels()
      .then((data) => {
        setModels(data.models);
        setSelectedModel(data.default);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load models");
      })
      .finally(() => setLoading(false));
  }, []);

  return { models, selectedModel, setSelectedModel, loading, error };
}
