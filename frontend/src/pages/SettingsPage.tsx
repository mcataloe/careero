import { List, Stack, Text, Title } from "@mantine/core";
import { Navigate, useParams } from "react-router-dom";

import { AccountLifecyclePanel } from "../components/AccountLifecyclePanel";
import { AIUsagePanel } from "../components/AIUsagePanel";
import { AutomationPreferencesPanel } from "../components/AutomationPreferencesPanel";
import { EntitlementsPanel } from "../components/EntitlementsPanel";
import { FeatureWorkspaceLayout } from "../components/FeatureWorkspaceLayout";
import { LocalDataExportPanel } from "../components/LocalDataExportPanel";
import { ProductReadinessPanel } from "../components/ProductReadinessPanel";
import { ResumeSourceSettings } from "../components/ResumeSourceSettings";

const settingsSections = [
  {
    id: "runtime",
    label: "Runtime",
    description: "Local backend and auth status",
  },
  {
    id: "readiness",
    label: "Product readiness",
    description: "Production gate status",
  },
  {
    id: "data-export",
    label: "Data export",
    description: "Download local records",
  },
  {
    id: "account-lifecycle",
    label: "Account lifecycle",
    description: "Local request records",
  },
  {
    id: "ai-usage",
    label: "AI usage",
    description: "Safe local usage metadata",
  },
  {
    id: "plan",
    label: "Plan",
    description: "Local entitlement boundary",
  },
  {
    id: "automation",
    label: "Automation",
    description: "Local suggestion guardrails",
  },
  {
    id: "resume-source",
    label: "Resume source",
    description: "Profile grounding source",
  },
] as const;

type SettingsSectionId = (typeof settingsSections)[number]["id"];

const settingsSectionIds = new Set<string>(
  settingsSections.map((section) => section.id),
);

export function SettingsPage() {
  const { section } = useParams();
  const activeSection = isSettingsSectionId(section) ? section : null;

  if (!activeSection) {
    return <Navigate to="/settings/runtime" replace />;
  }

  return (
    <Stack gap="lg">
      <div>
        <Title order={1}>Settings</Title>
        <Text c="dimmed">Local runtime, account, and workspace defaults.</Text>
      </div>
      <FeatureWorkspaceLayout
        navLabel="Settings sections"
        items={settingsSections.map((item) => ({
          ...item,
          to: `/settings/${item.id}`,
        }))}
        activeId={activeSection}
        withDetailPanel={activeSection === "runtime"}
      >
        <SettingsSectionContent activeSection={activeSection} />
      </FeatureWorkspaceLayout>
    </Stack>
  );
}

function SettingsSectionContent({
  activeSection,
}: {
  activeSection: SettingsSectionId;
}) {
  switch (activeSection) {
    case "readiness":
      return <ProductReadinessPanel />;
    case "data-export":
      return <LocalDataExportPanel />;
    case "account-lifecycle":
      return <AccountLifecyclePanel />;
    case "ai-usage":
      return <AIUsagePanel />;
    case "plan":
      return <EntitlementsPanel />;
    case "automation":
      return <AutomationPreferencesPanel />;
    case "resume-source":
      return <ResumeSourceSettings />;
    case "runtime":
    default:
      return <RuntimeSettingsSection />;
  }
}

function RuntimeSettingsSection() {
  return (
    <Stack gap="md">
      <Title order={2}>Runtime</Title>
      <List spacing="xs">
        <List.Item>Backend API is expected at http://127.0.0.1:8000.</List.Item>
        <List.Item>Vite proxies frontend `/api` requests to the backend.</List.Item>
        <List.Item>First-party email/password login is enabled locally.</List.Item>
        <List.Item>Google and LinkedIn SSO are visible placeholders and are not active.</List.Item>
        <List.Item>Workspace switching and hosted account recovery remain future work.</List.Item>
      </List>
    </Stack>
  );
}

function isSettingsSectionId(value: string | undefined): value is SettingsSectionId {
  return typeof value === "string" && settingsSectionIds.has(value);
}
