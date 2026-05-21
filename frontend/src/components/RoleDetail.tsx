import {
  Badge,
  Button,
  Divider,
  Grid,
  Group,
  Paper,
  Select,
  Stack,
  Text,
  Textarea,
  TextInput,
  Title,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import type { ReactNode } from "react";

import type {
  OpportunitySignal,
  Role,
  RoleStatus,
  RoleUpdatePayload,
} from "../types/roles";
import { ExpandableTextSection } from "./ExpandableTextSection";
import { MarkdownPreviewBlock } from "./MarkdownPreviewBlock";

const statusOptions: { label: string; value: RoleStatus }[] = [
  { label: "Found", value: "found" },
  { label: "Interested", value: "interested" },
  { label: "Applied", value: "applied" },
  { label: "Archived", value: "archived" },
];

function valueOrDash(value: string | null | undefined) {
  return value && value.trim() ? value : "-";
}

export function RoleDetail({
  role,
  onUpdate,
  onArchive,
  saving = false,
  archiving = false,
  sectionNav,
}: {
  role: Role;
  onUpdate: (payload: RoleUpdatePayload) => Promise<void> | void;
  onArchive: () => Promise<void> | void;
  saving?: boolean;
  archiving?: boolean;
  sectionNav?: ReactNode;
}) {
  const intelligence = role.parse_metadata.opportunityIntelligence;
  const form = useForm({
    initialValues: {
      status: role.status,
      remoteType: role.remote_type ?? "",
      normalizedDescription: role.normalized_description ?? "",
    },
  });

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="flex-start">
        <Stack gap={4}>
          <Title order={1}>{role.title}</Title>
          <Text c="dimmed">{role.company.name}</Text>
        </Stack>
        <Badge size="lg" variant="light">
          {role.status}
        </Badge>
      </Group>

      {sectionNav}

      <Paper id="role-overview" withBorder radius="md" p="lg">
        <Grid>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Text size="sm" c="dimmed">
              Source
            </Text>
            <Text>{role.source?.name ?? "Unknown"}</Text>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Text size="sm" c="dimmed">
              Location
            </Text>
            <Text>{valueOrDash(role.location)}</Text>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Text size="sm" c="dimmed">
              Remote type
            </Text>
            <Text>{valueOrDash(role.remote_type)}</Text>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Text size="sm" c="dimmed">
              Compensation
            </Text>
            <Text>
              {role.compensation_min || role.compensation_max
                ? `${role.compensation_min ?? "-"} - ${role.compensation_max ?? "-"} ${
                    role.compensation_currency ?? ""
                  }`
                : "-"}
            </Text>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Text size="sm" c="dimmed">
              Date found
            </Text>
            <Text>{role.date_found}</Text>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Text size="sm" c="dimmed">
              Date posted
            </Text>
            <Text>{valueOrDash(role.date_posted)}</Text>
          </Grid.Col>
          <Grid.Col span={12}>
            <Text size="sm" c="dimmed">
              Job URL
            </Text>
            <Text>{valueOrDash(role.job_url)}</Text>
          </Grid.Col>
        </Grid>
      </Paper>

      {intelligence ? (
        <Paper id="opportunity-intelligence" withBorder radius="md" p="lg">
          <Stack gap="md">
            <Group justify="space-between" align="flex-start">
              <div>
                <Title order={3}>Opportunity intelligence</Title>
                <Text c="dimmed" size="sm">
                  {intelligence.summary}
                </Text>
              </div>
              <Group gap="xs">
                {intelligence.categories.map((category) => (
                  <Badge key={category} variant="light">
                    {category}
                  </Badge>
                ))}
              </Group>
            </Group>
            {intelligence.signals.length > 0 ? (
              <Stack gap="sm">
                {intelligence.signals.map((signal) => (
                  <SignalSummary
                    key={`${signal.type}-${signal.reason}`}
                    signal={signal}
                  />
                ))}
              </Stack>
            ) : (
              <Text size="sm" c="dimmed">
                No deterministic caution signals were detected from the available fields.
              </Text>
            )}
          </Stack>
        </Paper>
      ) : null}

      <Paper withBorder radius="md" p="lg">
        <Stack>
          <Title order={3}>Description</Title>
          <div id="role-description">
            <ExpandableTextSection title="Raw description">
              <MarkdownPreviewBlock value={valueOrDash(role.raw_description)} />
            </ExpandableTextSection>
          </div>
          <Divider />
          <div id="role-normalized-description">
            <ExpandableTextSection title="Normalized description">
              <MarkdownPreviewBlock value={valueOrDash(role.normalized_description)} />
            </ExpandableTextSection>
          </div>
        </Stack>
      </Paper>

      <Paper id="role-edit" withBorder radius="md" p="lg">
        <form
          onSubmit={form.onSubmit((values) =>
            onUpdate({
              status: values.status,
              remote_type: values.remoteType.trim() || null,
              normalized_description: values.normalizedDescription.trim() || null,
            }),
          )}
        >
          <Stack>
            <Title order={3}>Edit opportunity</Title>
            <Grid>
              <Grid.Col span={{ base: 12, md: 6 }}>
                <Select
                  label="Status"
                  data={statusOptions}
                  allowDeselect={false}
                  {...form.getInputProps("status")}
                />
              </Grid.Col>
              <Grid.Col span={{ base: 12, md: 6 }}>
                <TextInput label="Remote type" {...form.getInputProps("remoteType")} />
              </Grid.Col>
              <Grid.Col span={12}>
                <Textarea
                  label="Normalized description"
                  minRows={4}
                  maxRows={10}
                  autosize
                  {...form.getInputProps("normalizedDescription")}
                />
              </Grid.Col>
            </Grid>
            <Group justify="space-between">
              <Button color="red" variant="light" loading={archiving} onClick={onArchive}>
                Archive opportunity
              </Button>
              <Button type="submit" loading={saving}>
                Save changes
              </Button>
            </Group>
          </Stack>
        </form>
      </Paper>
    </Stack>
  );
}

function SignalSummary({ signal }: { signal: OpportunitySignal }) {
  return (
    <div>
      <Group justify="space-between" align="flex-start">
        <div>
          <Text fw={600}>{signal.label}</Text>
          <Text size="sm" c="dimmed">
            {signal.reason}
          </Text>
        </div>
        <Badge color={signal.severity === "high" ? "red" : "yellow"} variant="light">
          {signal.confidence}
        </Badge>
      </Group>
      <Text size="xs" c="dimmed" mt="xs">
        {signal.basis}
      </Text>
      <Divider mt="sm" />
    </div>
  );
}
