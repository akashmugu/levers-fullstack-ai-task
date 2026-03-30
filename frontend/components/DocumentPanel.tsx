"use client";

import { useRef, useState } from "react";
import type { DocumentList } from "@/types";

interface DocumentPanelProps {
  documents: DocumentList;
  totalCount: number;
  loading: boolean;
  uploading: boolean;
  error: string | null;
  onUpload: (file: File) => Promise<void>;
  onDelete: (filename: string) => Promise<void>;
}

const ACCEPTED_EXTENSIONS = ".md,.csv,.txt";

export function DocumentPanel({
  documents,
  totalCount,
  loading,
  uploading,
  error,
  onUpload,
  onDelete,
}: DocumentPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files) return;
    for (const file of Array.from(files)) {
      await onUpload(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-sm transition-colors hover:bg-zinc-50 dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-100 dark:hover:bg-zinc-700"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className="h-4 w-4"
        >
          <path d="M3.75 3A1.75 1.75 0 002 4.75v3.26a3.235 3.235 0 011.75-.51h12.5c.644 0 1.245.188 1.75.51V6.75A1.75 1.75 0 0016.25 5h-4.836a.25.25 0 01-.177-.073L9.823 3.513A1.75 1.75 0 008.586 3H3.75zM3.75 9A1.75 1.75 0 002 10.75v4.5c0 .966.784 1.75 1.75 1.75h12.5A1.75 1.75 0 0018 15.25v-4.5A1.75 1.75 0 0016.25 9H3.75z" />
        </svg>
        Docs ({totalCount})
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-20">
          <div
            className="fixed inset-0 bg-black/30"
            onClick={() => setIsOpen(false)}
          />
          <div className="relative z-10 w-full max-w-lg rounded-2xl border border-zinc-200 bg-white p-6 shadow-xl dark:border-zinc-700 dark:bg-zinc-900">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                Documents
              </h2>
              <button
                onClick={() => setIsOpen(false)}
                className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  className="h-5 w-5"
                >
                  <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
                </svg>
              </button>
            </div>

            {/* Upload zone */}
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={() => setDragActive(false)}
              onClick={() => fileInputRef.current?.click()}
              className={`mb-4 cursor-pointer rounded-xl border-2 border-dashed p-6 text-center transition-colors ${
                dragActive
                  ? "border-blue-400 bg-blue-50 dark:border-blue-500 dark:bg-blue-900/20"
                  : "border-zinc-300 hover:border-zinc-400 dark:border-zinc-600 dark:hover:border-zinc-500"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept={ACCEPTED_EXTENSIONS}
                multiple
                onChange={(e) => handleFiles(e.target.files)}
                className="hidden"
              />
              {uploading ? (
                <p className="text-sm text-blue-600 dark:text-blue-400">
                  Uploading...
                </p>
              ) : (
                <>
                  <p className="text-sm text-zinc-600 dark:text-zinc-400">
                    Drop files here or click to upload
                  </p>
                  <p className="mt-1 text-xs text-zinc-400 dark:text-zinc-500">
                    Supports .md, .csv, .txt
                  </p>
                </>
              )}
            </div>

            {error && (
              <p className="mb-3 text-sm text-red-500">{error}</p>
            )}

            {/* Document list */}
            {loading ? (
              <p className="text-sm text-zinc-400">Loading documents...</p>
            ) : totalCount === 0 ? (
              <p className="text-sm text-zinc-400">
                No documents ingested yet. Upload files to enable RAG.
              </p>
            ) : (
              <div className="space-y-3">
                {documents.unstructured.length > 0 && (
                  <div>
                    <p className="mb-1 text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                      Unstructured
                    </p>
                    <ul className="space-y-1">
                      {documents.unstructured.map((name) => (
                        <DocumentItem
                          key={name}
                          name={name}
                          onDelete={onDelete}
                        />
                      ))}
                    </ul>
                  </div>
                )}
                {documents.structured.length > 0 && (
                  <div>
                    <p className="mb-1 text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                      Structured
                    </p>
                    <ul className="space-y-1">
                      {documents.structured.map((name) => (
                        <DocumentItem
                          key={name}
                          name={name}
                          onDelete={onDelete}
                        />
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

function DocumentItem({
  name,
  onDelete,
}: {
  name: string;
  onDelete: (name: string) => Promise<void>;
}) {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    await onDelete(name);
    setDeleting(false);
  };

  return (
    <li className="flex items-center justify-between rounded-lg bg-zinc-50 px-3 py-2 dark:bg-zinc-800">
      <span className="truncate text-sm text-zinc-700 dark:text-zinc-300">
        {name}
      </span>
      <button
        onClick={handleDelete}
        disabled={deleting}
        className="ml-2 shrink-0 text-zinc-400 transition-colors hover:text-red-500 disabled:opacity-50"
        aria-label={`Delete ${name}`}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className="h-4 w-4"
        >
          <path
            fillRule="evenodd"
            d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z"
            clipRule="evenodd"
          />
        </svg>
      </button>
    </li>
  );
}
