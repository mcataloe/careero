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
          Application workflow tracking is available through saved roles. A full
          workflow dashboard will build on those records in a later UI layer.
        </Text>
      </Paper>
    </Stack>
  );
}
