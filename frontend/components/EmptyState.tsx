"use client";

const SUGGESTIONS = [
  "What are the permitted calling hours?",
  "What script do I use for voicemail?",
  "What is the status of account ACC-007?",
  "What does CEASE_DESIST mean?",
];

interface EmptyStateProps {
  onSuggestion: (query: string) => void;
  hasDocuments: boolean;
}

export function EmptyState({ onSuggestion, hasDocuments }: EmptyStateProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 px-4 py-2">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-zinc-800 dark:text-zinc-200">
          Debt Collection Compliance Assistant
        </h2>
        <p className="mt-2 max-w-md text-sm text-zinc-500 dark:text-zinc-400">
          Ask about FDCPA rules, call scripts, account statuses, or compliance
          terminology.
        </p>
        {!hasDocuments && (
          <p className="mt-2 text-sm font-medium text-amber-600 dark:text-amber-400">
            No documents ingested yet. Upload reference documents to enable
            RAG-powered answers.
          </p>
        )}
      </div>
      <div className="grid w-full max-w-lg grid-cols-1 gap-2 sm:grid-cols-2">
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onSuggestion(suggestion)}
            className="rounded-xl border border-zinc-200 bg-white px-4 py-3 text-left text-sm text-zinc-600 transition-colors hover:border-blue-300 hover:bg-blue-50 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:border-blue-600 dark:hover:bg-blue-900/20"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
