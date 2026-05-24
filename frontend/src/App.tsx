import { Navigate, Route, Routes, useParams } from "react-router-dom";

import { AppShellLayout } from "./components/AppShellLayout";
import { ApplicationDetailPage } from "./pages/ApplicationDetailPage";
import { ApplicationsPage } from "./pages/ApplicationsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { RoleDetailPage } from "./pages/RoleDetailPage";
import { RoleNewPage } from "./pages/RoleNewPage";
import { RolesPage } from "./pages/RolesPage";
import { SettingsPage } from "./pages/SettingsPage";
import { StrategyPage } from "./pages/StrategyPage";

function App() {
  return (
    <AppShellLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/strategy" element={<StrategyPage />} />
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
    </AppShellLayout>
  );
}

function LegacyRoleDetailRedirect() {
  const { roleId } = useParams();
  return <Navigate to={`/opportunities/${roleId ?? ""}`} replace />;
}

export default App;
