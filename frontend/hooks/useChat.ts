"use client";

import { useCallback, useRef, useState } from "react";
import type { ChatMessage } from "@/types";
import { sendChat, streamChat } from "@/lib/api";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const send = useCallback(
    async (query: string, model: string, stream: boolean) => {
      const userMessage: ChatMessage = { role: "user", content: query };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      const history = messages.map(({ role, content }) => ({ role, content }));

      if (stream) {
        const placeholder: ChatMessage = {
          role: "assistant",
          content: "",
          sources: [],
        };
        setMessages((prev) => [...prev, placeholder]);

        abortRef.current = streamChat(
          { query, model, stream: true, history },
          (token) => {
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              updated[updated.length - 1] = {
                ...last,
                content: last.content + token,
              };
              return updated;
            });
          },
          (sources) => {
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              updated[updated.length - 1] = { ...last, sources };
              return updated;
            });
          },
          () => setIsLoading(false),
          (error) => {
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              updated[updated.length - 1] = {
                ...last,
                content: last.content || `Error: ${error}`,
              };
              return updated;
            });
            setIsLoading(false);
          },
        );
      } else {
        try {
          const data = await sendChat({ query, model, stream: false, history });
          const assistantMessage: ChatMessage = {
            role: "assistant",
            content: data.response,
            sources: data.sources,
          };
          setMessages((prev) => [...prev, assistantMessage]);
        } catch (err) {
          const errorMessage =
            err instanceof Error ? err.message : "Something went wrong";
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: `Error: ${errorMessage}` },
          ]);
        } finally {
          setIsLoading(false);
        }
      }
    },
    [messages],
  );

  const stop = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setIsLoading(false);
  }, []);

  const clear = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setMessages([]);
    setIsLoading(false);
  }, []);

  return { messages, isLoading, send, stop, clear };
}
