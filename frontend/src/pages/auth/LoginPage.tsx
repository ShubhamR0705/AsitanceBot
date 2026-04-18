import { motion } from "framer-motion";
import { Bot, LockKeyhole, Mail } from "lucide-react";
import { FormEvent, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { roleHome, useAuth } from "../../contexts/AuthContext";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";

export function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("user@company.com");
  const [password, setPassword] = useState("UserPass123!");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  if (user) return <Navigate to={roleHome(user.role)} replace />;

  const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      const loggedInUser = await login(email, password);
      navigate(from ?? roleHome(loggedInUser.role), { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to login");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthFrame>
      <form onSubmit={submit} className="w-full max-w-md rounded-lg border border-line bg-surface p-6 shadow-soft">
        <div className="mb-8">
          <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-brand-600 text-white shadow-lift">
            <Bot className="h-5 w-5" />
          </div>
          <h1 className="text-2xl font-semibold text-ink">Welcome back</h1>
          <p className="mt-2 text-sm leading-6 text-muted">Sign in to continue your IT support workflow.</p>
        </div>

        <div className="space-y-4">
          <label className="block">
            <span className="mb-2 flex items-center gap-2 text-sm font-medium text-ink">
              <Mail className="h-4 w-4 text-muted" />
              Email
            </span>
            <Input value={email} onChange={(event) => setEmail(event.target.value)} type="email" autoComplete="email" required />
          </label>
          <label className="block">
            <span className="mb-2 flex items-center gap-2 text-sm font-medium text-ink">
              <LockKeyhole className="h-4 w-4 text-muted" />
              Password
            </span>
            <Input value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" required />
          </label>
        </div>

        {error ? <p className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}

        <Button type="submit" className="mt-6 w-full" isLoading={isLoading}>
          Login
        </Button>

        <p className="mt-5 text-center text-sm text-muted">
          New employee?{" "}
          <Link className="font-semibold text-brand-700 hover:text-brand-600" to="/signup">
            Create an account
          </Link>
        </p>

        <div className="mt-6 rounded-lg border border-line bg-elevated p-3 text-xs leading-5 text-muted">
          Demo access: user@company.com, tech@company.com, admin@company.com. Passwords are listed in the README.
        </div>
      </form>
    </AuthFrame>
  );
}

function AuthFrame({ children }: { children: React.ReactNode }) {
  return (
    <main className="grid min-h-screen bg-base px-4 py-8 md:grid-cols-[1fr_1.05fr]">
      <section className="hidden items-center justify-center border-r border-line px-10 md:flex">
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }} className="max-w-lg">
          <div className="mb-6 inline-flex rounded-lg border border-brand-100 bg-brand-50 px-3 py-1 text-sm font-semibold text-brand-700">
            AI support that knows when to hand off
          </div>
          <h2 className="text-4xl font-semibold leading-tight text-ink">Resolve common IT issues fast, escalate the rest with context.</h2>
          <p className="mt-5 text-base leading-7 text-muted">
            AssistIQ classifies issues, retrieves approved troubleshooting steps, tracks failed attempts, and creates technician-ready tickets.
          </p>
        </motion.div>
      </section>
      <section className="flex items-center justify-center">{children}</section>
    </main>
  );
}

