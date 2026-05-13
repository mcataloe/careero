import { Grid, Paper, Stack, Text, Title } from "@mantine/core";

export function DashboardPage() {
  return (
    <Stack gap="lg">
      <div>
        <Title order={1}>Dashboard</Title>
        <Text c="dimmed">
          A local control center for job search operations. Start by adding roles manually.
        </Text>
      </div>

      <Grid>
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Paper withBorder radius="md" p="lg">
            <Title order={3}>Manual intake</Title>
            <Text c="dimmed" mt="xs">
              Paste roles from LinkedIn or company job boards into Careero.
            </Text>
          </Paper>
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Paper withBorder radius="md" p="lg">
            <Title order={3}>Local-first</Title>
            <Text c="dimmed" mt="xs">
              Your backend and PostgreSQL database run on this machine.
            </Text>
          </Paper>
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Paper withBorder radius="md" p="lg">
            <Title order={3}>STRIDE later</Title>
            <Text c="dimmed" mt="xs">
              Roles captured here will be ready for later evaluation workflows.
            </Text>
          </Paper>
        </Grid.Col>
      </Grid>
    </Stack>
  );
}
