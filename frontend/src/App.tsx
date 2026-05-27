import { Center, Loader } from "@mantine/core";
import { Navigate, Route, Routes, useLocation, useParams } from "react-router-dom";

import { AuthProvider, useAuth } from "./auth/AuthProvider";
import { AppShellLayout } from "./components/AppShellLayout";
import { ApplicationDetailPage } from "./pages/ApplicationDetailPage";
import { ApplicationsPage } from "./pages/ApplicationsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { RoleDetailPage } from "./pages/RoleDetailPage";
import { RoleNewPage } from "./pages/RoleNewPage";
import { RolesPage } from "./pages/RolesPage";
import { SettingsPage } from "./pages/SettingsPage";
import { StrategyPage } from "./pages/StrategyPage";

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/*"
          element={
            <ProtectedAppShell>
              <AppRoutes />
            </ProtectedAppShell>
          }
        />
      </Routes>
    </AuthProvider>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/strategy" element={<Navigate to="/strategy/overview" replace />} />
      <Route path="/strategy/:section" element={<StrategyPage />} />
      <Route
        path="/workspaces/:workspaceId/strategy"
        element={<WorkspaceStrategyRedirect />}
      />
      <Route
        path="/workspaces/:workspaceId/strategy/:section"
        element={<StrategyPage />}
      />
      <Route path="/opportunities" element={<RolesPage />} />
      <Route path="/opportunities/new" element={<RoleNewPage />} />
      <Route path="/opportunities/:opportunityId" element={<RoleDetailPage />} />
      <Route path="/roles" element={<Navigate to="/opportunities" replace />} />
      <Route path="/roles/new" element={<Navigate to="/opportunities/new" replace />} />
      <Route path="/roles/:roleId" element={<LegacyRoleDetailRedirect />} />
      <Route path="/applications" element={<ApplicationsPage />} />
      <Route path="/applications/:applicationId" element={<ApplicationDetailPage />} />
      <Route path="/settings" element={<SettingsPage />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function ProtectedAppShell({ children }: { children: React.ReactNode }) {
  const { currentUser, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <Center h="100vh">
        <Loader aria-label="Checking session" />
      </Center>
    );
  }

  if (!currentUser) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: `${location.pathname}${location.search}` }}
      />
    );
  }

  return <AppShellLayout>{children}</AppShellLayout>;
}

function LegacyRoleDetailRedirect() {
  const { roleId } = useParams();
  return <Navigate to={`/opportunities/${roleId ?? ""}`} replace />;
}

function WorkspaceStrategyRedirect() {
  const { workspaceId } = useParams();
  return <Navigate to={`/workspaces/${workspaceId ?? ""}/strategy/overview`} replace />;
}

export default App;
