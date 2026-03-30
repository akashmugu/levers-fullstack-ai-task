"use client";

import type { ChatMessage as ChatMessageType } from "@/types";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100"
        }`}
      >
        <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">
          {message.content || (
            <span className="inline-flex items-center gap-1 text-zinc-400">
              <span className="animate-pulse">Thinking...</span>
            </span>
          )}
        </div>
        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 border-t border-zinc-200 pt-2 dark:border-zinc-700">
            <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
              Sources:
            </p>
            <div className="mt-1 flex flex-wrap gap-1">
              {message.sources.map((source) => (
                <span
                  key={source}
                  className="inline-block rounded-full bg-zinc-200 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-700 dark:text-zinc-300"
                >
                  {source}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
