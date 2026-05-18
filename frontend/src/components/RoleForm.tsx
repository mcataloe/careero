import {
  Alert,
  Badge,
  Button,
  Divider,
  Grid,
  Group,
  NumberInput,
  Select,
  Stack,
  Text,
  Textarea,
  TextInput,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useState } from "react";

import { parseRole } from "../api/roles";
import type {
  ParsedRole,
  RoleCreatePayload,
  RoleParseMetadata,
  RoleStatus,
  SourceType,
} from "../types/roles";

const sourceOptions: { label: string; value: SourceType }[] = [
  { label: "Manual", value: "manual" },
  { label: "LinkedIn manual", value: "linkedin_manual" },
  { label: "LinkedIn", value: "linkedin" },
  { label: "Recruiter", value: "recruiter" },
  { label: "Referral", value: "referral" },
  { label: "Company site", value: "company_site" },
  { label: "Job board", value: "job_board" },
  { label: "Networking", value: "networking" },
  { label: "Direct outreach", value: "direct_outreach" },
  { label: "Internal referral", value: "internal_referral" },
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

type ParseState = "idle" | "parsing" | "parsed" | "parse_failed";

function optionalText(value: string | number | null | undefined) {
  const trimmed = String(value ?? "").trim();
  return trimmed.length > 0 ? trimmed : null;
}

function confidencePercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function RoleForm({
  onSubmit,
  submitting = false,
}: {
  onSubmit: (payload: RoleCreatePayload) => Promise<void> | void;
  submitting?: boolean;
}) {
  const [parseState, setParseState] = useState<ParseState>("idle");
  const [parseError, setParseError] = useState<string | null>(null);
  const [parseWarnings, setParseWarnings] = useState<string[]>([]);
  const [parseConfidence, setParseConfidence] = useState<Record<string, number>>({});
  const [parseMetadata, setParseMetadata] = useState<RoleParseMetadata | null>(null);
  const [appliedParsedValues, setAppliedParsedValues] = useState<
    Partial<Record<string, string>>
  >({});
  const [parseInput, setParseInput] = useState({
    rawText: "",
    jobUrl: "",
    source: "manual" as SourceType,
  });

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

  function applyParsedValues(parsed: ParsedRole, rawText: string) {
    const candidateValues: Partial<typeof form.values> = {
      title: parsed.roleTitle ?? "",
      companyName: parsed.company ?? "",
      companyWebsite: parsed.companyWebsite ?? "",
      sourceType: parsed.source ?? parseInput.source,
      jobUrl: parsed.jobUrl ?? parseInput.jobUrl,
      location: parsed.location ?? "",
      remoteType: parsed.remoteType ?? "",
      compensationMin:
        parsed.compensationMin === null || parsed.compensationMin === undefined
          ? ""
          : String(parsed.compensationMin),
      compensationMax:
        parsed.compensationMax === null || parsed.compensationMax === undefined
          ? ""
          : String(parsed.compensationMax),
      compensationCurrency: parsed.currency ?? "",
      rawDescription: rawText,
      normalizedDescription: parsed.normalizedDescription ?? "",
      datePosted: parsed.datePosted ?? "",
    };
    const nextValues = { ...form.values };
    const nextAppliedValues: Partial<Record<string, string>> = {};

    for (const [fieldName, value] of Object.entries(candidateValues)) {
      if (value === undefined || value === null || String(value).trim() === "") {
        continue;
      }
      const currentValue = String(nextValues[fieldName as keyof typeof nextValues] ?? "");
      const shouldApply =
        currentValue.trim() === "" ||
        (fieldName === "sourceType" &&
          currentValue === "manual" &&
          String(value) !== "manual");
      if (shouldApply) {
        nextValues[fieldName as keyof typeof nextValues] = value as never;
        nextAppliedValues[fieldName] = String(value);
      }
    }

    form.setValues(nextValues);
    setAppliedParsedValues((current) => ({ ...current, ...nextAppliedValues }));
  }

  function editedFields() {
    return Object.entries(appliedParsedValues)
      .filter(([fieldName, parsedValue]) => {
        if (parsedValue === undefined) {
          return false;
        }
        const currentValue = String(
          form.values[fieldName as keyof typeof form.values] ?? "",
        );
        return currentValue.trim() !== parsedValue.trim();
      })
      .map(([fieldName]) => fieldName)
      .sort();
  }

  async function handleParse() {
    setParseError(null);
    setParseWarnings([]);
    if (!parseInput.rawText.trim()) {
      setParseState("parse_failed");
      setParseError("Paste a job description before parsing.");
      return;
    }

    setParseState("parsing");
    try {
      const result = await parseRole({
        rawText: parseInput.rawText,
        source: parseInput.source,
        jobUrl: optionalText(parseInput.jobUrl),
      });
      applyParsedValues(result.parsed, parseInput.rawText);
      const warnings = result.parsed.warnings ?? [];
      const confidence = result.parsed.confidence ?? {};
      setParseWarnings(warnings);
      setParseConfidence(confidence);
      setParseMetadata({
        parserVersion: result.metadata.parserVersion,
        aiModel: result.metadata.model,
        parseTimestamp: new Date().toISOString(),
        parseWarnings: warnings,
        confidence,
        extractedSkills: result.parsed.extractedSkills ?? [],
      });
      setParseState("parsed");
    } catch (err) {
      setParseState("parse_failed");
      setParseError(err instanceof Error ? err.message : "Could not parse role");
    }
  }

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
          parse_metadata: parseMetadata
            ? {
                ...parseMetadata,
                userEditedFields: editedFields(),
              }
            : undefined,
          status: values.status,
          date_found: optionalText(values.dateFound),
          date_posted: optionalText(values.datePosted),
        }),
      )}
    >
      <Stack gap="md">
        <Stack gap="sm">
          <Group justify="space-between" align="center">
            <Text fw={600}>AI intake</Text>
            <Badge variant="light">{parseState.replace("_", " ")}</Badge>
          </Group>
          <Textarea
            label="Paste job description"
            description="Paste content from LinkedIn, recruiter emails, job boards, or company sites."
            minRows={8}
            maxRows={16}
            autosize
            value={parseInput.rawText}
            onChange={(event) => {
              const value = event.currentTarget.value;
              setParseInput((current) => ({
                ...current,
                rawText: value,
              }));
            }}
          />
          <Grid>
            <Grid.Col span={{ base: 12, md: 8 }}>
              <TextInput
                label="Optional URL"
                placeholder="https://example.com/jobs/123"
                value={parseInput.jobUrl}
                onChange={(event) => {
                  const value = event.currentTarget.value;
                  setParseInput((current) => ({
                    ...current,
                    jobUrl: value,
                  }));
                }}
              />
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 4 }}>
              <Select
                label="Optional source"
                data={sourceOptions}
                allowDeselect={false}
                value={parseInput.source}
                onChange={(value) =>
                  setParseInput((current) => ({
                    ...current,
                    source: (value ?? "manual") as SourceType,
                  }))
                }
              />
            </Grid.Col>
          </Grid>
          {parseError ? (
            <Alert color="red" title="Parse failed">
              {parseError}
            </Alert>
          ) : null}
          {parseState === "parsed" ? (
            <Alert color="green" title="Parsed role fields">
              Review the populated fields below before creating the role.
            </Alert>
          ) : null}
          {parseWarnings.length > 0 ? (
            <Alert color="yellow" title="Parser warnings">
              <Stack gap={4}>
                {parseWarnings.map((warning) => (
                  <Text key={warning} size="sm">
                    {warning}
                  </Text>
                ))}
              </Stack>
            </Alert>
          ) : null}
          {Object.keys(parseConfidence).length > 0 ? (
            <Group gap="xs">
              {Object.entries(parseConfidence)
                .slice(0, 6)
                .map(([fieldName, score]) => (
                  <Badge key={fieldName} variant="light">
                    {fieldName}: {confidencePercent(score)}
                  </Badge>
                ))}
            </Group>
          ) : null}
          <Group justify="flex-end">
            <Button
              type="button"
              variant="light"
              loading={parseState === "parsing"}
              onClick={handleParse}
            >
              Parse role
            </Button>
          </Group>
        </Stack>

        <Divider />

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
              maxRows={12}
              autosize
              placeholder="Paste the original job description."
              {...form.getInputProps("rawDescription")}
            />
          </Grid.Col>
          <Grid.Col span={12}>
            <Textarea
              label="Normalized description"
              minRows={4}
              maxRows={10}
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
