import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ChatActionButtons, getChatActions } from "./ChatActionButtons";
import type { Message } from "../../types/api";

const baseMessage: Message = {
  id: 1,
  conversation_id: 1,
  sender: "ASSISTANT",
  content: "Try this action.",
  created_at: new Date().toISOString()
};

describe("ChatActionButtons", () => {
  it("renders safe link and internal route actions", () => {
    render(
      <MemoryRouter>
        <ChatActionButtons
          message={{
            ...baseMessage,
            actions: [
              { label: "Reset Password", type: "link", url: "https://company.com/reset-password" },
              { label: "Connect to Technician", type: "internal_route", route: "/user/tickets/42" }
            ]
          }}
        />
      </MemoryRouter>
    );

    expect(screen.getByRole("link", { name: /reset password/i })).toHaveAttribute("href", "https://company.com/reset-password");
    expect(screen.getByRole("link", { name: /connect to technician/i })).toHaveAttribute("href", "/user/tickets/42");
  });

  it("ignores untrusted links", () => {
    const actions = getChatActions({
      ...baseMessage,
      meta: {
        actions: [
          { label: "Bad Link", type: "link", url: "https://evil.example/phish" },
          { label: "Open Webmail", type: "link", url: "https://mail.company.com" }
        ]
      }
    });

    expect(actions).toEqual([{ label: "Open Webmail", type: "link", url: "https://mail.company.com" }]);
  });
});
