import { useAuth } from "../../contexts/AuthContext";
import { PageTransition } from "../../components/ui/PageTransition";
import { Badge } from "../../components/ui/Badge";

export function ProfilePage() {
  const { user } = useAuth();

  return (
    <PageTransition>
      <section className="max-w-2xl rounded-lg border border-line bg-surface p-6 shadow-soft">
        <h2 className="text-2xl font-semibold text-ink">Profile</h2>
        <p className="mt-2 text-sm text-muted">Account details and access level.</p>
        <dl className="mt-6 grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg border border-line bg-elevated p-4">
            <dt className="text-xs font-semibold uppercase text-muted">Name</dt>
            <dd className="mt-2 text-sm font-semibold text-ink">{user?.full_name}</dd>
          </div>
          <div className="rounded-lg border border-line bg-elevated p-4">
            <dt className="text-xs font-semibold uppercase text-muted">Email</dt>
            <dd className="mt-2 text-sm font-semibold text-ink">{user?.email}</dd>
          </div>
          <div className="rounded-lg border border-line bg-elevated p-4">
            <dt className="text-xs font-semibold uppercase text-muted">Role</dt>
            <dd className="mt-2">
              <Badge tone="brand">{user?.role}</Badge>
            </dd>
          </div>
        </dl>
      </section>
    </PageTransition>
  );
}
