import { Paper, Stack, Text, Title } from "@mantine/core";

export function ApplicationsPage() {
  return (
    <Stack gap="lg">
      <div>
        <Title order={1}>Applications</Title>
        <Text c="dimmed">Application tracking will build on manually captured roles.</Text>
      </div>
      <Paper withBorder radius="md" p="lg">
        <Text c="dimmed">
          No application workflow is implemented yet. Use Roles to capture opportunities.
        </Text>
      </Paper>
    </Stack>
  );
}
