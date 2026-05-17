import { Badge, Grid, Group, Paper, Stack, Text, Title } from "@mantine/core";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  listOverdueWorkspaceReminders,
  listUpcomingWorkspaceReminders,
} from "../api/applications";
import type { WorkspaceReminder } from "../types/applications";

const DEFAULT_WORKSPACE_ID = "00000000-0000-4000-8000-000000000101";

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

function ReminderSummary({
  title,
  reminders,
  tone,
}: {
  title: string;
  reminders: WorkspaceReminder[];
  tone: "red" | "blue";
}) {
  return (
    <Paper withBorder radius="md" p="lg">
      <Group justify="space-between" mb="xs">
        <Title order={3}>{title}</Title>
        <Badge color={tone}>{reminders.length}</Badge>
      </Group>
      {reminders.length === 0 ? (
        <Text c="dimmed" size="sm">
          No reminders to show.
        </Text>
      ) : (
        <Stack gap="xs">
          {reminders.slice(0, 5).map((reminder) => (
            <div key={reminder.id}>
              <Text
                component={Link}
                to={`/applications/${reminder.application_id}`}
                fw={600}
                size="sm"
              >
                {reminder.title}
              </Text>
              <Text c="dimmed" size="xs">
                {reminder.company_name} - {reminder.application_title} - Due{" "}
                {formatDateTime(reminder.due_at)}
              </Text>
            </div>
          ))}
        </Stack>
      )}
    </Paper>
  );
}

export function DashboardPage() {
  const [upcoming, setUpcoming] = useState<WorkspaceReminder[]>([]);
  const [overdue, setOverdue] = useState<WorkspaceReminder[]>([]);

  useEffect(() => {
    async function loadReminders() {
      try {
        const [nextUpcoming, nextOverdue] = await Promise.all([
          listUpcomingWorkspaceReminders(DEFAULT_WORKSPACE_ID, 5),
          listOverdueWorkspaceReminders(DEFAULT_WORKSPACE_ID, 5),
        ]);
        setUpcoming(nextUpcoming);
        setOverdue(nextOverdue);
      } catch {
        setUpcoming([]);
        setOverdue([]);
      }
    }
    void loadReminders();
  }, []);

  return (
    <Stack gap="lg">
      <div>
        <Title order={1}>Dashboard</Title>
        <Text c="dimmed">
          A local control center for job search operations. Start by adding roles manually.
        </Text>
      </div>

      <Grid>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <ReminderSummary title="Overdue reminders" reminders={overdue} tone="red" />
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <ReminderSummary title="Upcoming reminders" reminders={upcoming} tone="blue" />
        </Grid.Col>
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
            <Title order={3}>No external reminders</Title>
            <Text c="dimmed" mt="xs">
              Reminders are local workflow records only; calendar, email, and push
              integrations belong to future layers.
            </Text>
          </Paper>
        </Grid.Col>
      </Grid>
    </Stack>
  );
}
