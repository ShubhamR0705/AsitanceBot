import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { roleHome, useAuth } from "./contexts/AuthContext";
import { LoginPage } from "./pages/auth/LoginPage";
import { SignupPage } from "./pages/auth/SignupPage";
import { AdminDashboardPage } from "./pages/admin/AdminDashboardPage";
import { AdminTicketDetailPage } from "./pages/admin/AdminTicketDetailPage";
import { AnalyticsPage } from "./pages/admin/AnalyticsPage";
import { KnowledgeBasePage } from "./pages/admin/KnowledgeBasePage";
import { TicketOverviewPage } from "./pages/admin/TicketOverviewPage";
import { UserManagementPage } from "./pages/admin/UserManagementPage";
import { TechnicianDashboardPage } from "./pages/technician/TechnicianDashboardPage";
import { TechnicianTicketDetailPage } from "./pages/technician/TechnicianTicketDetailPage";
import { TicketQueuePage } from "./pages/technician/TicketQueuePage";
import { MyTicketsPage } from "./pages/user/MyTicketsPage";
import { ProfilePage } from "./pages/user/ProfilePage";
import { SupportChatPage } from "./pages/user/SupportChatPage";
import { TicketDetailPage } from "./pages/user/TicketDetailPage";
import { UserDashboardPage } from "./pages/user/UserDashboardPage";

function RootRedirect() {
  const { user, isBootstrapping } = useAuth();
  if (isBootstrapping) return null;
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={roleHome(user.role)} replace />;
}

export function App() {
  return (
    <Routes>
      <Route path="/" element={<RootRedirect />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />

      <Route element={<ProtectedRoute roles={["USER"]} />}>
        <Route element={<AppShell />}>
          <Route path="/user" element={<UserDashboardPage />} />
          <Route path="/user/chat" element={<SupportChatPage />} />
          <Route path="/user/tickets" element={<MyTicketsPage />} />
          <Route path="/user/tickets/:ticketId" element={<TicketDetailPage />} />
          <Route path="/user/profile" element={<ProfilePage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute roles={["TECHNICIAN"]} />}>
        <Route element={<AppShell />}>
          <Route path="/technician" element={<TechnicianDashboardPage />} />
          <Route path="/technician/tickets" element={<TicketQueuePage />} />
          <Route path="/technician/tickets/:ticketId" element={<TechnicianTicketDetailPage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute roles={["ADMIN"]} />}>
        <Route element={<AppShell />}>
          <Route path="/admin" element={<AdminDashboardPage />} />
          <Route path="/admin/users" element={<UserManagementPage />} />
          <Route path="/admin/tickets" element={<TicketOverviewPage />} />
          <Route path="/admin/tickets/:ticketId" element={<AdminTicketDetailPage />} />
          <Route path="/admin/analytics" element={<AnalyticsPage />} />
          <Route path="/admin/knowledge-base" element={<KnowledgeBasePage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

