import {
  Button,
  Grid,
  Group,
  NumberInput,
  Select,
  Stack,
  Textarea,
  TextInput,
} from "@mantine/core";
import { useForm } from "@mantine/form";

import type { RoleCreatePayload, RoleStatus, SourceType } from "../types/roles";

const sourceOptions: { label: string; value: SourceType }[] = [
  { label: "Manual", value: "manual" },
  { label: "LinkedIn manual", value: "linkedin_manual" },
  { label: "Greenhouse", value: "greenhouse" },
  { label: "Lever", value: "lever" },
  { label: "Ashby", value: "ashby" },
  { label: "Workable", value: "workable" },
  { label: "Other", value: "other" },
];

const statusOptions: { label: string; value: RoleStatus }[] = [
  { label: "Found", value: "found" },
  { label: "Interested", value: "interested" },
  { label: "Applied", value: "applied" },
  { label: "Archived", value: "archived" },
];

function today() {
  return new Date().toISOString().slice(0, 10);
}

function optionalText(value: string) {
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}

export function RoleForm({
  onSubmit,
  submitting = false,
}: {
  onSubmit: (payload: RoleCreatePayload) => Promise<void> | void;
  submitting?: boolean;
}) {
  const form = useForm({
    initialValues: {
      title: "",
      companyName: "",
      companyWebsite: "",
      sourceType: "manual" as SourceType,
      jobUrl: "",
      location: "",
      remoteType: "",
      compensationMin: "",
      compensationMax: "",
      compensationCurrency: "USD",
      rawDescription: "",
      normalizedDescription: "",
      status: "found" as RoleStatus,
      dateFound: today(),
      datePosted: "",
    },
    validate: {
      title: (value) => (value.trim() ? null : "Title is required"),
      companyName: (value) => (value.trim() ? null : "Company is required"),
    },
  });

  return (
    <form
      noValidate
      onSubmit={form.onSubmit((values) =>
        onSubmit({
          title: values.title.trim(),
          company: {
            name: values.companyName.trim(),
            website_url: optionalText(values.companyWebsite),
          },
          source: { source_type: values.sourceType },
          job_url: optionalText(values.jobUrl),
          location: optionalText(values.location),
          remote_type: optionalText(values.remoteType),
          compensation_min: optionalText(values.compensationMin),
          compensation_max: optionalText(values.compensationMax),
          compensation_currency: optionalText(values.compensationCurrency),
          raw_description: optionalText(values.rawDescription),
          normalized_description: optionalText(values.normalizedDescription),
          status: values.status,
          date_found: optionalText(values.dateFound),
          date_posted: optionalText(values.datePosted),
        }),
      )}
    >
      <Stack gap="md">
        <Grid>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <TextInput
              label="Role title"
              placeholder="Senior Backend Engineer"
              required
              {...form.getInputProps("title")}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <TextInput
              label="Company"
              placeholder="Example Company"
              required
              {...form.getInputProps("companyName")}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <TextInput
              label="Company website"
              placeholder="https://example.com"
              {...form.getInputProps("companyWebsite")}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <Select
              label="Source"
              data={sourceOptions}
              allowDeselect={false}
              {...form.getInputProps("sourceType")}
            />
          </Grid.Col>
          <Grid.Col span={12}>
            <TextInput
              label="Job URL"
              placeholder="https://www.linkedin.com/jobs/view/example"
              {...form.getInputProps("jobUrl")}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <TextInput
              label="Location"
              placeholder="Chicago, IL"
              {...form.getInputProps("location")}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <TextInput
              label="Remote type"
              placeholder="remote, hybrid, onsite"
              {...form.getInputProps("remoteType")}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <NumberInput
              label="Compensation min"
              min={0}
              hideControls
              {...form.getInputProps("compensationMin")}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <NumberInput
              label="Compensation max"
              min={0}
              hideControls
              {...form.getInputProps("compensationMax")}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <TextInput
              label="Currency"
              maxLength={3}
              {...form.getInputProps("compensationCurrency")}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Select
              label="Status"
              data={statusOptions}
              allowDeselect={false}
              {...form.getInputProps("status")}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <TextInput type="date" label="Date found" {...form.getInputProps("dateFound")} />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <TextInput type="date" label="Date posted" {...form.getInputProps("datePosted")} />
          </Grid.Col>
          <Grid.Col span={12}>
            <Textarea
              label="Raw description"
              minRows={6}
              autosize
              placeholder="Paste the original job description."
              {...form.getInputProps("rawDescription")}
            />
          </Grid.Col>
          <Grid.Col span={12}>
            <Textarea
              label="Normalized description"
              minRows={4}
              autosize
              placeholder="Optional notes or cleaned-up description."
              {...form.getInputProps("normalizedDescription")}
            />
          </Grid.Col>
        </Grid>

        <Group justify="flex-end">
          <Button type="submit" loading={submitting}>
            Create role
          </Button>
        </Group>
      </Stack>
    </form>
  );
}
