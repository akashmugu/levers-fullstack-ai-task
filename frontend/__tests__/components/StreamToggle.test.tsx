import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { StreamToggle } from "@/components/StreamToggle";

describe("StreamToggle", () => {
  it("shows 'Stream' when streaming is enabled", () => {
    render(<StreamToggle streaming={true} onToggle={() => {}} />);
    expect(screen.getByText("Stream")).toBeInTheDocument();
  });

  it("shows 'Batch' when streaming is disabled", () => {
    render(<StreamToggle streaming={false} onToggle={() => {}} />);
    expect(screen.getByText("Batch")).toBeInTheDocument();
  });

  it("calls onToggle with opposite value when clicked", async () => {
    const user = userEvent.setup();
    const onToggle = vi.fn();
    render(<StreamToggle streaming={true} onToggle={onToggle} />);
    await user.click(screen.getByRole("button"));
    expect(onToggle).toHaveBeenCalledWith(false);
  });

  it("is disabled when disabled prop is true", () => {
    render(<StreamToggle streaming={true} onToggle={() => {}} disabled />);
    expect(screen.getByRole("button")).toBeDisabled();
  });
});
