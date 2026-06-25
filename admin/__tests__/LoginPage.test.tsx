import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import LoginPage from "../app/(auth)/login/page";

// Mock next/navigation
jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: jest.fn() }),
}));

// Mock api
jest.mock("../lib/api", () => ({
  api: {
    post: jest.fn(),
  },
}));

// Mock authStore
jest.mock("../features/auth/authStore", () => ({
  useAuthStore: (selector: any) =>
    selector({ accessToken: null, setAccessToken: jest.fn() }),
}));

import { api } from "../lib/api";

describe("LoginPage", () => {
  it("renders email and password fields", () => {
    render(<LoginPage />);
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
  });

  it("renders login button", () => {
    render(<LoginPage />);
    expect(screen.getByRole("button", { name: /login/i })).toBeInTheDocument();
  });

  it("shows error message on failed login", async () => {
    (api.post as jest.Mock).mockRejectedValueOnce({
      response: { data: { detail: "Invalid credentials" } },
    });

    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "admin@test.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "wrongpassword" },
    });
    fireEvent.click(screen.getByRole("button", { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Invalid credentials");
    });
  });
});
