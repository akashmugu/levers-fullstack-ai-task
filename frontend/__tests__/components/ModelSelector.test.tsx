import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ModelSelector } from "@/components/ModelSelector";
import type { ModelInfo } from "@/types";

const models: ModelInfo[] = [
  { id: "model-a", label: "Model A (Thinking)", type: "thinking" },
  { id: "model-b", label: "Model B (Standard)", type: "standard" },
];

describe("ModelSelector", () => {
  it("renders all model options", () => {
    render(
      <ModelSelector
        models={models}
        selectedModel="model-a"
        onSelect={() => {}}
      />,
    );
    const options = screen.getAllByRole("option");
    expect(options).toHaveLength(2);
    expect(options[0]).toHaveTextContent("Model A (Thinking)");
    expect(options[1]).toHaveTextContent("Model B (Standard)");
  });

  it("reflects the selected model", () => {
    render(
      <ModelSelector
        models={models}
        selectedModel="model-b"
        onSelect={() => {}}
      />,
    );
    const select = screen.getByRole("combobox") as HTMLSelectElement;
    expect(select.value).toBe("model-b");
  });

  it("calls onSelect when a new model is chosen", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(
      <ModelSelector
        models={models}
        selectedModel="model-a"
        onSelect={onSelect}
      />,
    );
    await user.selectOptions(screen.getByRole("combobox"), "model-b");
    expect(onSelect).toHaveBeenCalledWith("model-b");
  });

  it("is disabled when disabled prop is true", () => {
    render(
      <ModelSelector
        models={models}
        selectedModel="model-a"
        onSelect={() => {}}
        disabled
      />,
    );
    const select = screen.getByRole("combobox") as HTMLSelectElement;
    expect(select.disabled).toBe(true);
  });
});
