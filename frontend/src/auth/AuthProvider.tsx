import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getCurrentUser,
  login as loginRequest,
  logout as logoutRequest,
  register as registerRequest,
} from "../api/auth";
import { ApiError } from "../api/client";
import type { AuthUser, LoginPayload, RegisterPayload } from "../types/auth";

interface AuthContextValue {
  currentUser: AuthUser | null;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<AuthUser>;
  register: (payload: RegisterPayload) => Promise<AuthUser>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;
    getCurrentUser()
      .then((user) => {
        if (active) {
          setCurrentUser(user);
        }
      })
      .catch((error) => {
        if (active && !(error instanceof ApiError && error.status === 401)) {
          setCurrentUser(null);
        }
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    const user = await loginRequest(payload);
    setCurrentUser(user);
    return user;
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    const user = await registerRequest(payload);
    setCurrentUser(user);
    return user;
  }, []);

  const logout = useCallback(async () => {
    await logoutRequest();
    setCurrentUser(null);
  }, []);

  const value = useMemo(
    () => ({ currentUser, isLoading, login, register, logout }),
    [currentUser, isLoading, login, logout, register],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
