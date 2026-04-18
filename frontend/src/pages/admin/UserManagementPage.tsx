import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "../../api/client";
import { Badge } from "../../components/ui/Badge";
import { EmptyState } from "../../components/ui/EmptyState";
import { PageTransition } from "../../components/ui/PageTransition";
import { Skeleton } from "../../components/ui/Skeleton";
import type { UserRole } from "../../types/api";

const roles: UserRole[] = ["USER", "TECHNICIAN", "ADMIN"];

export function UserManagementPage() {
  const queryClient = useQueryClient();
  const users = useQuery({ queryKey: ["admin-users"], queryFn: adminApi.users });
  const updateRole = useMutation({
    mutationFn: ({ userId, role }: { userId: number; role: UserRole }) => adminApi.updateRole(userId, role),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-users"] })
  });

  return (
    <PageTransition>
      <div className="space-y-5">
        <div>
          <h2 className="text-2xl font-semibold text-ink">User management</h2>
          <p className="mt-2 text-sm text-muted">Assign exactly one platform role to each account.</p>
        </div>
        {users.isLoading ? (
          <Skeleton className="h-96" />
        ) : users.data?.length ? (
          <div className="overflow-hidden rounded-lg border border-line bg-surface shadow-soft">
            <div className="grid grid-cols-12 border-b border-line bg-elevated px-4 py-3 text-xs font-semibold uppercase text-muted">
              <span className="col-span-5">User</span>
              <span className="col-span-3">Current role</span>
              <span className="col-span-4">Manage</span>
            </div>
            {users.data.map((user) => (
              <div key={user.id} className="grid grid-cols-12 items-center gap-3 border-b border-line px-4 py-4 last:border-b-0">
                <div className="col-span-5 min-w-0">
                  <p className="truncate text-sm font-semibold text-ink">{user.full_name}</p>
                  <p className="truncate text-xs text-muted">{user.email}</p>
                </div>
                <div className="col-span-3">
                  <Badge tone="brand">{user.role}</Badge>
                </div>
                <div className="col-span-4">
                  <select
                    value={user.role}
                    onChange={(event) => updateRole.mutate({ userId: user.id, role: event.target.value as UserRole })}
                    className="h-10 w-full rounded-lg border border-line bg-white px-3 text-sm shadow-sm focus:focus-ring"
                  >
                    {roles.map((role) => (
                      <option key={role} value={role}>
                        {role}
                      </option>
                    ))}
                  </select>
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

