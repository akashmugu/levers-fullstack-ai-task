import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  deleteDocument,
  fetchDocuments,
  fetchModels,
  sendChat,
} from "@/lib/api";

let mockFetch: ReturnType<typeof vi.fn>;

beforeEach(() => {
  mockFetch = vi.fn();
  vi.stubGlobal("fetch", mockFetch);
});

afterEach(() => {
  vi.restoreAllMocks();
});

function jsonResponse(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("sendChat", () => {
  it("sends a POST request and returns the response", async () => {
    const chatResponse = {
      response: "Hello!",
      sources: ["test.md"],
      model: "model-a",
    };
    mockFetch.mockResolvedValue(jsonResponse(chatResponse));

    const result = await sendChat({
      query: "Hi",
      model: "model-a",
      stream: false,
      history: [],
    });

    expect(result).toEqual(chatResponse);
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/chat"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("always sends stream: false", async () => {
    mockFetch.mockResolvedValue(
      jsonResponse({ response: "", sources: [], model: "" }),
    );

    await sendChat({ query: "Hi", model: "m", stream: true, history: [] });

    const body = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(body.stream).toBe(false);
  });

  it("throws on non-ok response with detail", async () => {
    mockFetch.mockResolvedValue(jsonResponse({ detail: "LLM failed" }, 502));

    await expect(
      sendChat({ query: "Hi", model: "m", stream: false, history: [] }),
    ).rejects.toThrow("LLM failed");
  });
});

describe("fetchDocuments", () => {
  it("returns the document list", async () => {
    const docs = { unstructured: ["a.md"], structured: ["b.csv"] };
    mockFetch.mockResolvedValue(jsonResponse(docs));

    const result = await fetchDocuments();
    expect(result).toEqual(docs);
  });
});

describe("deleteDocument", () => {
  it("encodes the filename in the URL", async () => {
    mockFetch.mockResolvedValue(jsonResponse({ detail: "deleted" }));

    await deleteDocument("file with spaces.md");
    expect(mockFetch.mock.calls[0][0]).toContain(
      "/api/documents/file%20with%20spaces.md",
    );
  });
});

describe("fetchModels", () => {
  it("returns models and default", async () => {
    const data = {
      models: [{ id: "m1", label: "M1", type: "thinking" }],
      default: "m1",
    };
    mockFetch.mockResolvedValue(jsonResponse(data));

    const result = await fetchModels();
    expect(result.models).toHaveLength(1);
    expect(result.default).toBe("m1");
  });
});
