import { List, Paper, Stack, Text, Title } from "@mantine/core";

import { AccountLifecyclePanel } from "../components/AccountLifecyclePanel";
import { AIUsagePanel } from "../components/AIUsagePanel";
import { AutomationPreferencesPanel } from "../components/AutomationPreferencesPanel";
import { LocalDataExportPanel } from "../components/LocalDataExportPanel";
import { ProductReadinessPanel } from "../components/ProductReadinessPanel";
import { ResumeSourceSettings } from "../components/ResumeSourceSettings";

export function SettingsPage() {
  return (
    <Stack gap="lg">
      <div>
        <Title order={1}>Settings</Title>
        <Text c="dimmed">Local runtime details for this phase.</Text>
      </div>
      <Paper withBorder radius="md" p="lg">
        <List spacing="xs">
          <List.Item>Backend API is expected at http://127.0.0.1:8000.</List.Item>
          <List.Item>Vite proxies frontend `/api` requests to the backend.</List.Item>
          <List.Item>Authentication and workspace switching are intentionally absent.</List.Item>
        </List>
      </Paper>
      <ProductReadinessPanel />
      <LocalDataExportPanel />
      <AccountLifecyclePanel />
      <AIUsagePanel />
      <AutomationPreferencesPanel />
      <ResumeSourceSettings />
    </Stack>
  );
}
