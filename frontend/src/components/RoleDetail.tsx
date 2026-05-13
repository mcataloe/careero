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

import type { Role, RoleStatus, RoleUpdatePayload } from "../types/roles";
import { ExpandableTextSection } from "./ExpandableTextSection";

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
}: {
  role: Role;
  onUpdate: (payload: RoleUpdatePayload) => Promise<void> | void;
  onArchive: () => Promise<void> | void;
  saving?: boolean;
  archiving?: boolean;
}) {
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

      <Paper withBorder radius="md" p="lg">
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

      <Paper withBorder radius="md" p="lg">
        <Stack>
          <Title order={3}>Description</Title>
          <ExpandableTextSection title="Raw description">
            {valueOrDash(role.raw_description)}
          </ExpandableTextSection>
          <Divider />
          <ExpandableTextSection title="Normalized description">
            {valueOrDash(role.normalized_description)}
          </ExpandableTextSection>
        </Stack>
      </Paper>

      <Paper withBorder radius="md" p="lg">
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
            <Title order={3}>Edit role</Title>
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
                  autosize
                  {...form.getInputProps("normalizedDescription")}
                />
              </Grid.Col>
            </Grid>
            <Group justify="space-between">
              <Button color="red" variant="light" loading={archiving} onClick={onArchive}>
                Archive role
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
