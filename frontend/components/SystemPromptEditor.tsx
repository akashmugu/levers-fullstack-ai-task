"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchSystemPrompt, updateSystemPrompt } from "@/lib/api";

export function SystemPromptEditor() {
  const [isOpen, setIsOpen] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [savedPrompt, setSavedPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchSystemPrompt()
      .then((data) => {
        setPrompt(data.prompt);
        setSavedPrompt(data.prompt);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (isOpen) load();
  }, [isOpen, load]);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const data = await updateSystemPrompt(prompt);
      setSavedPrompt(data.prompt);
      setPrompt(data.prompt);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    } finally {
      setSaving(false);
    }
  };

  const isDirty = prompt !== savedPrompt;

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-sm transition-colors hover:bg-zinc-50 dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-100 dark:hover:bg-zinc-700"
        title="Edit system prompt"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className="h-4 w-4"
        >
          <path
            fillRule="evenodd"
            d="M4.5 2A2.5 2.5 0 002 4.5v11A2.5 2.5 0 004.5 18h11a2.5 2.5 0 002.5-2.5v-11A2.5 2.5 0 0015.5 2h-11zm5.75 5a.75.75 0 00-1.5 0v2.25H6.5a.75.75 0 000 1.5h2.25V13a.75.75 0 001.5 0v-2.25h2.25a.75.75 0 000-1.5h-2.25V7z"
            clipRule="evenodd"
          />
        </svg>
        Prompt
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-20">
          <div
            className="fixed inset-0 bg-black/30"
            onClick={() => setIsOpen(false)}
          />
          <div className="relative z-10 w-full max-w-xl rounded-2xl border border-zinc-200 bg-white p-6 shadow-xl dark:border-zinc-700 dark:bg-zinc-900">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                System Prompt
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

            <p className="mb-3 text-sm text-zinc-500 dark:text-zinc-400">
              This prompt is injected into every LLM call. Changes take effect
              on the next query.
            </p>

            {loading ? (
              <p className="py-8 text-center text-sm text-zinc-400">
                Loading...
              </p>
            ) : (
              <>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  rows={8}
                  className="w-full resize-y rounded-xl border border-zinc-300 bg-zinc-50 px-4 py-3 text-sm leading-relaxed outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-100"
                />

                {error && (
                  <p className="mt-2 text-sm text-red-500">{error}</p>
                )}

                <div className="mt-4 flex items-center justify-between">
                  <button
                    onClick={() => setPrompt(savedPrompt)}
                    disabled={!isDirty || saving}
                    className="rounded-lg px-3 py-1.5 text-sm text-zinc-500 transition-colors hover:text-zinc-700 disabled:opacity-40 dark:text-zinc-400 dark:hover:text-zinc-200"
                  >
                    Reset
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={!isDirty || saving}
                    className="rounded-lg bg-blue-600 px-4 py-1.5 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-40"
                  >
                    {saving ? "Saving..." : "Save"}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
