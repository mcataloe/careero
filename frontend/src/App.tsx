import { Navigate, Route, Routes } from "react-router-dom";

import { AppShellLayout } from "./components/AppShellLayout";
import { ApplicationDetailPage } from "./pages/ApplicationDetailPage";
import { ApplicationsPage } from "./pages/ApplicationsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { RoleDetailPage } from "./pages/RoleDetailPage";
import { RoleNewPage } from "./pages/RoleNewPage";
import { RolesPage } from "./pages/RolesPage";
import { SettingsPage } from "./pages/SettingsPage";

function App() {
  return (
    <AppShellLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/roles" element={<RolesPage />} />
        <Route path="/roles/new" element={<RoleNewPage />} />
        <Route path="/roles/:roleId" element={<RoleDetailPage />} />
        <Route path="/applications" element={<ApplicationsPage />} />
        <Route path="/applications/:applicationId" element={<ApplicationDetailPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AppShellLayout>
  );
}

export default App;
