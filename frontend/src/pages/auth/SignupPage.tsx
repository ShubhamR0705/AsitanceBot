import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { Bot } from "lucide-react";
import { roleHome, useAuth } from "../../contexts/AuthContext";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";

export function SignupPage() {
  const { user, signup } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  if (user) return <Navigate to={roleHome(user.role)} replace />;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      const createdUser = await signup({ email, full_name: fullName, password });
      navigate(roleHome(createdUser.role), { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign up");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-base px-4 py-8">
      <form onSubmit={submit} className="w-full max-w-md rounded-lg border border-line bg-surface p-6 shadow-soft">
        <div className="mb-8">
          <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-brand-600 text-white shadow-lift">
            <Bot className="h-5 w-5" />
          </div>
          <h1 className="text-2xl font-semibold text-ink">Create your account</h1>
          <p className="mt-2 text-sm leading-6 text-muted">New accounts start as users. Admins can promote technicians and admins.</p>
        </div>

        <div className="space-y-4">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-ink">Full name</span>
            <Input value={fullName} onChange={(event) => setFullName(event.target.value)} required />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-ink">Email</span>
            <Input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-ink">Password</span>
            <Input value={password} onChange={(event) => setPassword(event.target.value)} type="password" minLength={8} required />
          </label>
        </div>

        {error ? <p className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}

        <Button type="submit" className="mt-6 w-full" isLoading={isLoading}>
          Sign up
        </Button>

        <p className="mt-5 text-center text-sm text-muted">
          Already registered?{" "}
          <Link className="font-semibold text-brand-700 hover:text-brand-600" to="/login">
            Login
          </Link>
        </p>
      </form>
    </main>
  );
}
