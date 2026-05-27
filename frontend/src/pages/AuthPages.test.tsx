import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "../App";
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
  email: "matthew@example.com",
  first_name: "Matthew",
  last_name: "Coleman",
  display_name: "Matthew Coleman",
  auth_method: "local_password",
  account_status: "active",
  created_at: "2026-05-26T00:00:00Z",
};

function renderAppAt(path: string) {
  render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

describe("auth pages", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders login with disabled SSO placeholders", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(jsonResponse({ detail: "Authentication required" }, 401)),
    );

    renderAppAt("/login");

    expect(await screen.findByRole("heading", { name: "Careero" })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password/i, { selector: "input" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /continue with google - coming soon/i }),
    ).toBeDisabled();
    expect(
      screen.getByRole("button", { name: /continue with linkedin - coming soon/i }),
    ).toBeDisabled();
  });

  it("renders register page", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(jsonResponse({ detail: "Authentication required" }, 401)),
    );

    renderAppAt("/register");

    expect(
      await screen.findByRole("heading", { name: "Create your Careero account" }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/^first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
  });

  it("login form calls the API and redirects on success", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ detail: "Authentication required" }, 401))
      .mockResolvedValueOnce(jsonResponse(authUser))
      .mockResolvedValue(jsonResponse({}));
    vi.stubGlobal("fetch", fetchMock);

    renderAppAt("/login");
    await userEvent.type(await screen.findByLabelText(/email/i), "matthew@example.com");
    await userEvent.type(
      screen.getByLabelText(/^password/i, { selector: "input" }),
      "secret password",
    );
    await userEvent.click(screen.getByRole("button", { name: /^log in$/i }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/auth/login",
        expect.objectContaining({ method: "POST" }),
      );
    });
  });

  it("register form validates password confirmation", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ detail: "Authentication required" }, 401));
    vi.stubGlobal("fetch", fetchMock);

    renderAppAt("/register");
    await userEvent.type(await screen.findByLabelText(/^first name/i), "matthew@example.com");
    await userEvent.type(screen.getByLabelText(/^email/i), "matthew@example.com");
    await userEvent.type(screen.getByLabelText(/last name/i), "Matthew");
    await userEvent.type(
      screen.getByLabelText(/^password/i, { selector: "input" }),
      "secret password",
    );
    await userEvent.type(
      screen.getByLabelText(/confirm password/i, { selector: "input" }),
      "different",
    );
    await userEvent.click(screen.getByRole("button", { name: /create account/i }));

    expect(await screen.findByText("Passwords do not match.")).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalledWith(
      "/api/auth/register",
      expect.any(Object),
    );
  });
});
