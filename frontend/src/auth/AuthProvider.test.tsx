import { Button, Text } from "@mantine/core";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AuthProvider, useAuth } from "./AuthProvider";
import { render, screen, userEvent, waitFor } from "../test-utils";

function jsonResponse(response: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: async () => response,
  };
}

const authUser = {
  id: "user-1",
  username: "matthew",
  email: "matthew@example.com",
  display_name: "Matthew",
  auth_method: "local_password",
  account_status: "active",
  created_at: "2026-05-26T00:00:00Z",
};

function AuthProbe() {
  const { currentUser, logout } = useAuth();
  return (
    <>
      <Text>{currentUser ? currentUser.display_name : "No user"}</Text>
      <Button onClick={() => void logout()}>Log out</Button>
    </>
  );
}

describe("AuthProvider", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("logout clears the current user", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse(authUser))
        .mockResolvedValueOnce({
          ok: true,
          status: 204,
          headers: new Headers(),
          text: async () => "",
        }),
    );

    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    );

    expect(await screen.findByText("Matthew")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /log out/i }));

    await waitFor(() => {
      expect(screen.getByText("No user")).toBeInTheDocument();
    });
  });
});
