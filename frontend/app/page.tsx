"use client";

import { useEffect, useRef, useState } from "react";
import { ChatMessage } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";
import { ModelSelector } from "@/components/ModelSelector";
import { StreamToggle } from "@/components/StreamToggle";
import { DocumentPanel } from "@/components/DocumentPanel";
import { EmptyState } from "@/components/EmptyState";
import { SystemPromptEditor } from "@/components/SystemPromptEditor";
import { useChat } from "@/hooks/useChat";
import { useModels } from "@/hooks/useModels";
import { useDocuments } from "@/hooks/useDocuments";

export default function Home() {
  const { messages, isLoading, send, stop, clear } = useChat();
  const { models, selectedModel, setSelectedModel, loading: modelsLoading, error: modelsError } = useModels();
  const {
    documents,
    totalCount,
    loading: docsLoading,
    uploading,
    error: docsError,
    upload,
    remove,
  } = useDocuments();
  const [streaming, setStreaming] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (query: string) => {
    send(query, selectedModel, streaming);
  };

  return (
    <div className="flex h-full flex-1 flex-col">
      {/* Header */}
      <header className="flex shrink-0 items-center justify-between border-b border-zinc-200 bg-white px-4 py-3 dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex items-center gap-3">
          <h1 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
            Compliance Assistant
          </h1>
          {messages.length > 0 && (
            <button
              onClick={clear}
              className="rounded-lg px-2 py-1 text-xs text-zinc-500 transition-colors hover:bg-zinc-100 hover:text-zinc-700 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-200"
            >
              New chat
            </button>
          )}
        </div>
        <div className="flex items-center gap-2">
          <SystemPromptEditor />
          <DocumentPanel
            documents={documents}
            totalCount={totalCount}
            loading={docsLoading}
            uploading={uploading}
            error={docsError}
            onUpload={upload}
            onDelete={remove}
          />
          <StreamToggle
            streaming={streaming}
            onToggle={setStreaming}
            disabled={isLoading}
          />
          {modelsLoading ? null : modelsError ? (
            <span className="text-sm text-red-500">Models unavailable</span>
          ) : (
            <ModelSelector
              models={models}
              selectedModel={selectedModel}
              onSelect={setSelectedModel}
              disabled={isLoading}
            />
          )}
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <EmptyState
            onSuggestion={handleSend}
            hasDocuments={totalCount > 0}
          />
        ) : (
          <div className="mx-auto max-w-3xl space-y-4 px-4 py-6">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="shrink-0 border-t border-zinc-200 bg-white px-4 py-3 dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mx-auto max-w-3xl">
          <ChatInput
            onSend={handleSend}
            onStop={stop}
            isLoading={isLoading}
            disabled={!!modelsError}
          />
        </div>
      </div>
    </div>
  );
}
