import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useMemo, useState } from "react";
import { adminApi } from "../../api/client";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { EmptyState } from "../../components/ui/EmptyState";
import { Input } from "../../components/ui/Input";
import { PageTransition } from "../../components/ui/PageTransition";
import { Skeleton } from "../../components/ui/Skeleton";
import type { UserRole } from "../../types/api";
import { useAuth } from "../../contexts/AuthContext";

const roles: UserRole[] = ["USER", "TECHNICIAN", "ADMIN"];

export function UserManagementPage() {
  const queryClient = useQueryClient();
  const { user: currentUser } = useAuth();
  const [roleFilter, setRoleFilter] = useState<UserRole | "ALL">("ALL");
  const [statusFilter, setStatusFilter] = useState<"ALL" | "ACTIVE" | "INACTIVE">("ALL");
  const [form, setForm] = useState({ full_name: "", email: "", password: "", role: "USER" as UserRole });
  const [editingUserId, setEditingUserId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({ full_name: "", email: "" });
  const [error, setError] = useState("");
  const users = useQuery({
    queryKey: ["admin-users", roleFilter, statusFilter],
    queryFn: () =>
      adminApi.users({
        role: roleFilter,
        is_active: statusFilter === "ALL" ? "ALL" : statusFilter === "ACTIVE"
      })
  });
  const filteredUsers = useMemo(() => users.data ?? [], [users.data]);

  const createUser = useMutation({
    mutationFn: () => adminApi.createUser({ ...form, is_active: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-users"] });
      setForm({ full_name: "", email: "", password: "", role: "USER" });
      setError("");
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Unable to create user")
  });

  const updateUser = useMutation({
    mutationFn: ({ userId, payload }: { userId: number; payload: { full_name?: string; email?: string; role?: UserRole; is_active?: boolean } }) => adminApi.updateUser(userId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-users"] });
      setEditingUserId(null);
      setEditForm({ full_name: "", email: "" });
    }
  });

  const deactivate = useMutation({
    mutationFn: adminApi.deactivateUser,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-users"] })
  });

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!form.full_name.trim() || !form.email.trim() || !form.password.trim()) {
      setError("Name, email, and password are required.");
      return;
    }
    createUser.mutate();
  };

  return (
    <PageTransition>
      <div className="space-y-5">
        <div>
          <h2 className="text-2xl font-semibold text-ink">User management</h2>
          <p className="mt-2 text-sm text-muted">Create users, update roles, and deactivate accounts without breaking historical tickets.</p>
        </div>
        <form onSubmit={submit} className="rounded-lg border border-line bg-surface p-5 shadow-soft">
          <div className="grid gap-3 md:grid-cols-[1fr_1fr_1fr_180px_auto]">
            <Input value={form.full_name} onChange={(event) => setForm((current) => ({ ...current, full_name: event.target.value }))} placeholder="Full name" />
            <Input value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} placeholder="Email" type="email" />
            <Input value={form.password} onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))} placeholder="Temporary password" type="password" />
            <select
              value={form.role}
              onChange={(event) => setForm((current) => ({ ...current, role: event.target.value as UserRole }))}
              className="h-11 rounded-lg border border-line bg-white px-3 text-sm text-ink shadow-sm focus:focus-ring"
            >
              {roles.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
            <Button type="submit" isLoading={createUser.isPending}>Add user</Button>
          </div>
          {error ? <p className="mt-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
        </form>
        <div className="flex flex-col gap-3 rounded-lg border border-line bg-surface p-4 shadow-soft sm:flex-row">
          <select value={roleFilter} onChange={(event) => setRoleFilter(event.target.value as UserRole | "ALL")} className="h-11 rounded-lg border border-line bg-white px-3 text-sm text-ink shadow-sm focus:focus-ring">
            <option value="ALL">All roles</option>
            {roles.map((role) => (
              <option key={role} value={role}>{role}</option>
            ))}
          </select>
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as "ALL" | "ACTIVE" | "INACTIVE")} className="h-11 rounded-lg border border-line bg-white px-3 text-sm text-ink shadow-sm focus:focus-ring">
            <option value="ALL">All statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
          </select>
        </div>
        {users.isLoading ? (
          <Skeleton className="h-96" />
        ) : filteredUsers.length ? (
          <div className="overflow-hidden rounded-lg border border-line bg-surface shadow-soft">
            <div className="grid grid-cols-12 border-b border-line bg-elevated px-4 py-3 text-xs font-semibold uppercase text-muted">
              <span className="col-span-4">User</span>
              <span className="col-span-2">Status</span>
              <span className="col-span-2">Role</span>
              <span className="col-span-4">Manage</span>
            </div>
            {filteredUsers.map((user) => (
              <div key={user.id} className="grid grid-cols-12 items-center gap-3 border-b border-line px-4 py-4 last:border-b-0">
                <div className="col-span-4 min-w-0">
                  {editingUserId === user.id ? (
                    <div className="space-y-2">
                      <Input value={editForm.full_name} onChange={(event) => setEditForm((current) => ({ ...current, full_name: event.target.value }))} />
                      <Input value={editForm.email} onChange={(event) => setEditForm((current) => ({ ...current, email: event.target.value }))} type="email" />
                    </div>
                  ) : (
                    <>
                      <p className="truncate text-sm font-semibold text-ink">{user.full_name}</p>
                      <p className="truncate text-xs text-muted">{user.email}</p>
                    </>
                  )}
                </div>
                <div className="col-span-2">
                  <Badge tone={user.is_active ? "success" : "neutral"}>{user.is_active ? "ACTIVE" : "INACTIVE"}</Badge>
                </div>
                <div className="col-span-2">
                  <Badge tone="brand">{user.role}</Badge>
                </div>
                <div className="col-span-4 flex flex-col gap-2 sm:flex-row sm:flex-wrap">
                  <select value={user.role} onChange={(event) => updateUser.mutate({ userId: user.id, payload: { role: event.target.value as UserRole } })} className="h-10 flex-1 rounded-lg border border-line bg-white px-3 text-sm shadow-sm focus:focus-ring">
                    {roles.map((role) => <option key={role} value={role}>{role}</option>)}
                  </select>
                  {editingUserId === user.id ? (
                    <>
                      <Button
                        type="button"
                        variant="secondary"
                        disabled={updateUser.isPending}
                        onClick={() => updateUser.mutate({ userId: user.id, payload: { full_name: editForm.full_name, email: editForm.email } })}
                      >
                        Save
                      </Button>
                      <Button type="button" variant="ghost" onClick={() => setEditingUserId(null)}>
                        Cancel
                      </Button>
                    </>
                  ) : (
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => {
                        setEditingUserId(user.id);
                        setEditForm({ full_name: user.full_name, email: user.email });
                      }}
                    >
                      Edit
                    </Button>
                  )}
                  <Button
                    type="button"
                    variant={user.is_active ? "danger" : "secondary"}
                    disabled={user.id === currentUser?.id || deactivate.isPending || updateUser.isPending}
                    onClick={() => {
                      if (user.is_active) {
                        if (window.confirm(`Deactivate ${user.email}?`)) deactivate.mutate(user.id);
                        return;
                      }
                      updateUser.mutate({ userId: user.id, payload: { is_active: true } });
                    }}
                  >
                    {user.is_active ? "Deactivate" : "Reactivate"}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState title="No users" description="Users appear here after signup or seeding." />
        )}
      </div>
    </PageTransition>
  );
}
