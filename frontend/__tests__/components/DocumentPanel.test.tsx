import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { DocumentPanel } from "@/components/DocumentPanel";

function renderPanel(overrides = {}) {
  const props = {
    documents: { unstructured: [], structured: [] },
    totalCount: 0,
    loading: false,
    uploading: false,
    error: null,
    onUpload: vi.fn(),
    onDelete: vi.fn(),
    ...overrides,
  };
  return render(<DocumentPanel {...props} />);
}

describe("DocumentPanel", () => {
  it("shows document count on the button", () => {
    renderPanel({ totalCount: 3 });
    expect(screen.getByRole("button", { name: /Docs/i })).toHaveTextContent(
      "Docs (3)",
    );
  });

  it("opens modal when button is clicked", async () => {
    const user = userEvent.setup();
    renderPanel();
    await user.click(screen.getByRole("button", { name: /Docs/i }));
    expect(screen.getByText("Documents")).toBeInTheDocument();
    expect(
      screen.getByText("Drop files here or click to upload"),
    ).toBeInTheDocument();
  });

  it("shows empty state when no documents", async () => {
    const user = userEvent.setup();
    renderPanel();
    await user.click(screen.getByRole("button", { name: /Docs/i }));
    expect(
      screen.getByText(
        "No documents ingested yet. Upload files to enable RAG.",
      ),
    ).toBeInTheDocument();
  });

  it("shows loading state", async () => {
    const user = userEvent.setup();
    renderPanel({ loading: true });
    await user.click(screen.getByRole("button", { name: /Docs/i }));
    expect(screen.getByText("Loading documents...")).toBeInTheDocument();
  });

  it("shows error message", async () => {
    const user = userEvent.setup();
    renderPanel({ error: "Upload failed" });
    await user.click(screen.getByRole("button", { name: /Docs/i }));
    expect(screen.getByText("Upload failed")).toBeInTheDocument();
  });

  it("lists unstructured and structured documents", async () => {
    const user = userEvent.setup();
    renderPanel({
      documents: {
        unstructured: ["fdcpa.md", "glossary.md"],
        structured: ["accounts.csv"],
      },
      totalCount: 3,
    });
    await user.click(screen.getByRole("button", { name: /Docs/i }));
    expect(screen.getByText("Unstructured")).toBeInTheDocument();
    expect(screen.getByText("Structured")).toBeInTheDocument();
    expect(screen.getByText("fdcpa.md")).toBeInTheDocument();
    expect(screen.getByText("glossary.md")).toBeInTheDocument();
    expect(screen.getByText("accounts.csv")).toBeInTheDocument();
  });

  it("calls onDelete when delete button is clicked", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn().mockResolvedValue(undefined);
    renderPanel({
      documents: { unstructured: ["test.md"], structured: [] },
      totalCount: 1,
      onDelete,
    });
    await user.click(screen.getByRole("button", { name: /Docs/i }));

    const modal = screen.getByText("Documents").closest("div")!.parentElement!;
    await user.click(within(modal).getByLabelText("Delete test.md"));
    expect(onDelete).toHaveBeenCalledWith("test.md");
  });

  it("shows uploading state in drop zone", async () => {
    const user = userEvent.setup();
    renderPanel({ uploading: true });
    await user.click(screen.getByRole("button", { name: /Docs/i }));
    expect(screen.getByText("Uploading...")).toBeInTheDocument();
  });
});
