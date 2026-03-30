"use client";

import { useCallback, useEffect, useState } from "react";
import type { DocumentList } from "@/types";
import {
  fetchDocuments,
  uploadDocument,
  deleteDocument,
} from "@/lib/api";

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentList>({
    unstructured: [],
    structured: [],
  });
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    setLoading(true);
    fetchDocuments()
      .then(setDocuments)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const upload = useCallback(
    async (file: File) => {
      setUploading(true);
      setError(null);
      try {
        await uploadDocument(file);
        refresh();
      } catch (err) {
        const message = err instanceof Error ? err.message : "Upload failed";
        setError(message);
        throw err;
      } finally {
        setUploading(false);
      }
    },
    [refresh],
  );

  const remove = useCallback(
    async (filename: string) => {
      setError(null);
      try {
        await deleteDocument(filename);
        refresh();
      } catch (err) {
        const message = err instanceof Error ? err.message : "Delete failed";
        setError(message);
      }
    },
    [refresh],
  );

  const totalCount =
    documents.unstructured.length + documents.structured.length;

  return { documents, totalCount, loading, uploading, error, upload, remove, refresh };
}
