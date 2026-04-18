import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusBadge } from "./StatusBadge";

describe("StatusBadge", () => {
  it("renders readable status text", () => {
    render(<StatusBadge status="WAITING_FOR_USER" />);
    expect(screen.getByText("WAITING FOR USER")).toBeInTheDocument();
  });
});

