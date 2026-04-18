import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { authApi, clearToken, getToken, setToken } from "../api/client";
import type { User, UserRole } from "../types/api";

interface AuthContextValue {
  user: User | null;
  isBootstrapping: boolean;
  login: (email: string, password: string) => Promise<User>;
  signup: (payload: { email: string; full_name: string; password: string }) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isBootstrapping, setIsBootstrapping] = useState(Boolean(getToken()));

  useEffect(() => {
    let mounted = true;
    if (!getToken()) {
      setIsBootstrapping(false);
      return;
    }
    authApi
      .me()
      .then((currentUser) => {
        if (mounted) setUser(currentUser);
      })
      .catch(() => {
        clearToken();
        if (mounted) setUser(null);
      })
      .finally(() => {
        if (mounted) setIsBootstrapping(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isBootstrapping,
      login: async (email: string, password: string) => {
        const response = await authApi.login({ email, password });
        setToken(response.access_token);
        setUser(response.user);
        return response.user;
      },
      signup: async (payload) => {
        const response = await authApi.signup(payload);
        setToken(response.access_token);
        setUser(response.user);
        return response.user;
      },
      logout: () => {
        clearToken();
        setUser(null);
      }
    }),
    [isBootstrapping, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

export function roleHome(role: UserRole) {
  if (role === "ADMIN") return "/admin";
  if (role === "TECHNICIAN") return "/technician";
  return "/user";
}

