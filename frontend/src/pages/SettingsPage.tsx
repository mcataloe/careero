import { List, Paper, Stack, Text, Title } from "@mantine/core";

import { AutomationPreferencesPanel } from "../components/AutomationPreferencesPanel";
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
          <List.Item>First-party username/password login is enabled locally.</List.Item>
          <List.Item>Google and LinkedIn SSO are visible placeholders and are not active.</List.Item>
          <List.Item>Workspace switching and hosted account recovery remain future work.</List.Item>
        </List>
      </Paper>
      <ProductReadinessPanel />
      <AutomationPreferencesPanel />
      <ResumeSourceSettings />
    </Stack>
  );
}
