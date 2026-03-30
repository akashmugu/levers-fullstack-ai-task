import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ChatMessage } from "@/components/ChatMessage";

describe("ChatMessage", () => {
  it("renders user message with correct text", () => {
    render(
      <ChatMessage message={{ id: "1", role: "user", content: "Hello" }} />,
    );
    expect(screen.getByText("Hello")).toBeInTheDocument();
  });

  it("renders assistant message with markdown", () => {
    render(
      <ChatMessage
        message={{ id: "2", role: "assistant", content: "**bold text**" }}
      />,
    );
    expect(screen.getByText("bold text")).toBeInTheDocument();
    expect(screen.getByText("bold text").tagName).toBe("STRONG");
  });

  it("shows loading dots when content is empty", () => {
    const { container } = render(
      <ChatMessage message={{ id: "3", role: "assistant", content: "" }} />,
    );
    const dots = container.querySelectorAll(".animate-bounce");
    expect(dots.length).toBe(3);
  });

  it("renders source pills when sources are present", () => {
    render(
      <ChatMessage
        message={{
          id: "4",
          role: "assistant",
          content: "Answer here",
          sources: ["fdcpa.md", "glossary.md"],
        }}
      />,
    );
    expect(screen.getByText("Sources:")).toBeInTheDocument();
    expect(screen.getByText("fdcpa.md")).toBeInTheDocument();
    expect(screen.getByText("glossary.md")).toBeInTheDocument();
  });

  it("does not render sources section when no sources prop", () => {
    render(
      <ChatMessage
        message={{ id: "5", role: "assistant", content: "No sources" }}
      />,
    );
    expect(screen.queryByText("Sources:")).not.toBeInTheDocument();
  });

  it("aligns user messages to the right", () => {
    const { container } = render(
      <ChatMessage message={{ id: "6", role: "user", content: "User msg" }} />,
    );
    const wrapper = container.firstElementChild;
    expect(wrapper?.className).toContain("justify-end");
  });

  it("aligns assistant messages to the left", () => {
    const { container } = render(
      <ChatMessage
        message={{ id: "7", role: "assistant", content: "Bot msg" }}
      />,
    );
    const wrapper = container.firstElementChild;
    expect(wrapper?.className).toContain("justify-start");
  });
});
