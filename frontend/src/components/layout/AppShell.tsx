import { AnimatePresence, motion } from "framer-motion";
import {
  BarChart3,
  Bell,
  BookOpen,
  Bot,
  Home,
  LifeBuoy,
  LogOut,
  Menu,
  Settings,
  Ticket,
  Users,
  X
} from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { notificationsApi } from "../../api/client";
import { roleHome, useAuth } from "../../contexts/AuthContext";
import { cn } from "../../lib/cn";
import type { UserRole } from "../../types/api";
import { Button } from "../ui/Button";

interface NavItem {
  label: string;
  to: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navByRole: Record<UserRole, NavItem[]> = {
  USER: [
    { label: "Dashboard", to: "/user", icon: Home },
    { label: "Support Chat", to: "/user/chat", icon: Bot },
    { label: "My Tickets", to: "/user/tickets", icon: Ticket },
    { label: "Profile", to: "/user/profile", icon: Settings }
  ],
  TECHNICIAN: [
    { label: "Dashboard", to: "/technician", icon: Home },
    { label: "Ticket Queue", to: "/technician/tickets", icon: LifeBuoy }
  ],
  ADMIN: [
    { label: "Dashboard", to: "/admin", icon: Home },
    { label: "Users", to: "/admin/users", icon: Users },
    { label: "Tickets", to: "/admin/tickets", icon: Ticket },
    { label: "Analytics", to: "/admin/analytics", icon: BarChart3 },
    { label: "Knowledge Base", to: "/admin/knowledge-base", icon: BookOpen }
  ]
};

export function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const notifications = useQuery({ queryKey: ["notifications"], queryFn: notificationsApi.list, refetchInterval: 30000 });
  const markRead = useMutation({
    mutationFn: notificationsApi.markRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] })
  });

  if (!user) return null;

  const navItems = navByRole[user.role];
  const pageTitle = navItems.find((item) => location.pathname === item.to)?.label ?? "AssistIQ";

  const onLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-base text-ink">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-72 border-r border-line bg-surface/95 px-4 py-5 shadow-soft backdrop-blur md:block">
        <SidebarContent userRole={user.role} navItems={navItems} onLogout={onLogout} />
      </aside>

      <AnimatePresence>
        {isMobileOpen ? (
          <motion.div
            className="fixed inset-0 z-50 bg-ink/30 backdrop-blur-sm md:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.aside
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ duration: 0.2 }}
              className="h-full w-72 border-r border-line bg-surface px-4 py-5 shadow-soft"
            >
              <div className="mb-4 flex justify-end">
                <button className="rounded-lg p-2 text-muted hover:bg-elevated hover:text-ink" onClick={() => setIsMobileOpen(false)}>
                  <X className="h-5 w-5" />
                </button>
              </div>
              <SidebarContent userRole={user.role} navItems={navItems} onLogout={onLogout} onNavigate={() => setIsMobileOpen(false)} />
            </motion.aside>
          </motion.div>
        ) : null}
      </AnimatePresence>

      <div className="md:pl-72">
        <header className="sticky top-0 z-20 border-b border-line bg-base/88 px-4 py-3 backdrop-blur md:px-8">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <button className="rounded-lg p-2 text-muted hover:bg-elevated hover:text-ink md:hidden" onClick={() => setIsMobileOpen(true)}>
                <Menu className="h-5 w-5" />
              </button>
              <div>
                <p className="text-xs font-semibold uppercase text-brand-700">{user.role.replace("_", " ")}</p>
                <h1 className="text-lg font-semibold text-ink">{pageTitle}</h1>
              </div>
            </div>
            <div className="hidden items-center gap-3 sm:flex">
              <div className="relative">
                <button
                  className="relative rounded-lg border border-line bg-surface p-2 text-muted shadow-sm transition hover:bg-elevated hover:text-ink"
                  onClick={() => setNotificationsOpen((current) => !current)}
                >
                  <Bell className="h-5 w-5" />
                  {(notifications.data?.unread_count ?? 0) > 0 ? (
                    <span className="absolute -right-1 -top-1 rounded-full bg-red-600 px-1.5 py-0.5 text-[10px] font-bold text-white">
                      {notifications.data?.unread_count}
                    </span>
                  ) : null}
                </button>
                {notificationsOpen ? (
                  <div className="absolute right-0 mt-2 w-80 overflow-hidden rounded-lg border border-line bg-surface shadow-soft">
                    <div className="border-b border-line px-4 py-3">
                      <p className="text-sm font-semibold text-ink">Notifications</p>
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                      {notifications.data?.notifications.length ? (
                        notifications.data.notifications.slice(0, 8).map((item) => (
                          <button
                            key={item.id}
                            onClick={() => {
                              if (!item.is_read) markRead.mutate(item.id);
                              if (item.ticket_id) navigate(`${roleHome(user.role).replace(/$/, "")}/tickets/${item.ticket_id}`);
                              setNotificationsOpen(false);
                            }}
                            className={cn("block w-full border-b border-line px-4 py-3 text-left last:border-b-0 hover:bg-elevated", !item.is_read && "bg-brand-50/60")}
                          >
                            <p className="text-sm font-semibold text-ink">{item.title}</p>
                            <p className="mt-1 line-clamp-2 text-xs leading-5 text-muted">{item.body}</p>
                          </button>
                        ))
                      ) : (
                        <p className="px-4 py-8 text-center text-sm text-muted">No notifications yet.</p>
                      )}
                    </div>
                  </div>
                ) : null}
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-ink">{user.full_name}</p>
                <p className="text-xs text-muted">{user.email}</p>
              </div>
              <Button variant="ghost" onClick={onLogout}>
                <LogOut className="h-4 w-4" />
                Logout
              </Button>
            </div>
          </div>
        </header>
        <main className="px-4 py-6 md:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function SidebarContent({
  userRole,
  navItems,
  onLogout,
  onNavigate
}: {
  userRole: UserRole;
  navItems: NavItem[];
  onLogout: () => void;
  onNavigate?: () => void;
}) {
  return (
    <div className="flex h-full flex-col">
      <NavLink to={roleHome(userRole)} onClick={onNavigate} className="mb-8 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600 text-white shadow-lift">
          <Bot className="h-5 w-5" />
        </div>
        <div>
          <p className="text-base font-semibold text-ink">AssistIQ</p>
          <p className="text-xs text-muted">AI IT support</p>
        </div>
      </NavLink>

      <nav className="space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition",
                isActive ? "bg-brand-50 text-brand-700" : "text-muted hover:bg-elevated hover:text-ink"
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto rounded-lg border border-line bg-elevated p-4">
        <p className="text-sm font-semibold text-ink">Bounded AI workflow</p>
        <p className="mt-2 text-xs leading-5 text-muted">Classify, retrieve, suggest, retry once, then escalate with full context.</p>
        <Button variant="ghost" className="mt-4 w-full justify-start px-2" onClick={onLogout}>
          <LogOut className="h-4 w-4" />
          Logout
        </Button>
      </div>
    </div>
  );
}
