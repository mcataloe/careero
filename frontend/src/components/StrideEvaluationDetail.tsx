import {
  Badge,
  Button,
  Divider,
  Grid,
  Group,
  List,
  Paper,
  Progress,
  Stack,
  Text,
  Title,
} from "@mantine/core";

import type {
  EvaluationSection,
  EvidenceItem,
  StrideEvaluation,
} from "../types/strideEvaluations";
import { EmptyState } from "./States";

function titleize(value: string | null | undefined) {
  return value ? value.replaceAll("_", " ") : "-";
}

function scoreNumber(score: string | number | null | undefined) {
  if (score === null || score === undefined || score === "") return null;
  const parsed = Number(score);
  return Number.isFinite(parsed) ? parsed : null;
}

function recommendationColor(recommendation: string | null | undefined) {
  if (recommendation === "apply") return "green";
  if (recommendation === "monitor") return "blue";
  if (recommendation === "skip") return "red";
  return "yellow";
}

function aiStatusLabel(evaluation: StrideEvaluation) {
  const aiStatus = evaluation.ai_status ?? evaluation.raw_evaluation_json?.ai_status;
  if (aiStatus === "skipped") return "Skipped AI fallback";
  if (aiStatus === "failed") return "AI failed";
  if (aiStatus === "completed") return "AI enriched";
  return "Deterministic";
}

function EvidenceList({
  items,
  empty,
}: {
  items: EvidenceItem[] | undefined;
  empty: string;
}) {
  const safeItems = items ?? [];
  if (safeItems.length === 0) {
    return <Text c="dimmed">{empty}</Text>;
  }

  return (
    <List spacing="xs">
      {safeItems.map((item, index) => (
        <List.Item key={`${item.code ?? item.message ?? "item"}-${index}`}>
          <Stack gap={2}>
            <Text>{item.message ?? item.code ?? "Evaluation item"}</Text>
            {item.evidence ? (
              <Text size="sm" c="dimmed">
                Evidence: {item.evidence}
              </Text>
            ) : null}
            {item.status || item.severity ? (
              <Group gap="xs">
                {item.status ? <Badge variant="light">{titleize(item.status)}</Badge> : null}
                {item.severity ? (
                  <Badge variant="light" color={item.severity === "high" ? "red" : "yellow"}>
                    {item.severity}
                  </Badge>
                ) : null}
              </Group>
            ) : null}
          </Stack>
        </List.Item>
      ))}
    </List>
  );
}

function AlignmentSection({
  title,
  section,
}: {
  title: string;
  section: EvaluationSection | null | undefined;
}) {
  const score = scoreNumber(section?.score);

  return (
    <Paper withBorder radius="md" p="md">
      <Stack gap="xs">
        <Group justify="space-between" align="flex-start">
          <Title order={4}>{title}</Title>
          {section?.status ? <Badge variant="light">{titleize(section.status)}</Badge> : null}
        </Group>
        {score !== null ? <Progress value={score} /> : null}
        {score !== null ? (
          <Text size="sm" c="dimmed">
            {score}/100
          </Text>
        ) : null}
        <Text>{section?.notes ?? "No details available."}</Text>
        {Array.isArray(section?.evidence) && section.evidence.length > 0 ? (
          <Text size="sm" c="dimmed">
            Evidence: {section.evidence.join("; ")}
          </Text>
        ) : null}
      </Stack>
    </Paper>
  );
}

export function EvaluationStatusBadge({
  evaluation,
  loading = false,
  error,
}: {
  evaluation: StrideEvaluation | null;
  loading?: boolean;
  error?: string | null;
}) {
  if (loading) return <Badge variant="light">Loading evaluation</Badge>;
  if (error) return <Badge color="red">Evaluation error</Badge>;
  if (!evaluation) return <Badge variant="light">Not evaluated</Badge>;
  const aiStatus = evaluation.ai_status ?? evaluation.raw_evaluation_json?.ai_status;
  if (aiStatus === "skipped") {
    return <Badge color="yellow">Skipped AI fallback</Badge>;
  }
  if (aiStatus === "failed") {
    return <Badge color="orange">AI failed</Badge>;
  }
  return <Badge color="green">Completed</Badge>;
}

export function StrideEvaluationDetail({
  evaluation,
  onRun,
  running = false,
  onViewLatest,
}: {
  evaluation: StrideEvaluation | null;
  onRun: (force?: boolean) => Promise<void> | void;
  running?: boolean;
  onViewLatest?: () => void;
}) {
  if (!evaluation) {
    return (
      <Paper withBorder radius="md" p="lg">
        <EmptyState
          title="Not evaluated"
          message="Run STRIDE evaluation to create a local recommendation for this role."
          action={
            <Button loading={running} onClick={() => onRun(false)}>
              Run STRIDE evaluation
            </Button>
          }
        />
      </Paper>
    );
  }

  const score = scoreNumber(evaluation.overall_score);
  const unsupportedWarnings =
    evaluation.raw_evaluation_json?.ai_result?.unsupported_claim_warnings ?? [];

  return (
    <Paper withBorder radius="md" p="lg">
      <Stack gap="lg">
        <Group justify="space-between" align="flex-start">
          <Stack gap={4}>
            <Title order={3}>STRIDE evaluation</Title>
            <Group gap="xs">
              <EvaluationStatusBadge evaluation={evaluation} />
              <Badge variant="light">{aiStatusLabel(evaluation)}</Badge>
            </Group>
          </Stack>
          <Group>
            {onViewLatest ? (
              <Button variant="light" onClick={onViewLatest}>
                View latest evaluation
              </Button>
            ) : null}
            <Button loading={running} onClick={() => onRun(true)}>
              Re-run evaluation
            </Button>
          </Group>
        </Group>

        <Grid>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Paper withBorder radius="md" p="md">
              <Stack gap={4}>
                <Text size="sm" c="dimmed">
                  Overall score
                </Text>
                <Title order={2}>{score ?? "-"}</Title>
                {score !== null ? <Progress value={score} /> : null}
              </Stack>
            </Paper>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Paper withBorder radius="md" p="md">
              <Stack gap={4}>
                <Text size="sm" c="dimmed">
                  Recommendation
                </Text>
                <Badge size="lg" color={recommendationColor(evaluation.recommendation)}>
                  {titleize(evaluation.recommendation)}
                </Badge>
              </Stack>
            </Paper>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Paper withBorder radius="md" p="md">
              <Stack gap={4}>
                <Text size="sm" c="dimmed">
                  Confidence
                </Text>
                <Badge size="lg" variant="light">
                  {titleize(evaluation.confidence_level)}
                </Badge>
              </Stack>
            </Paper>
          </Grid.Col>
        </Grid>

        <Stack gap="xs">
          <Title order={4}>Summary</Title>
          <Text>{evaluation.summary ?? "No summary available."}</Text>
        </Stack>

        <Grid>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <Title order={4}>Strengths</Title>
            <EvidenceList items={evaluation.strengths} empty="No strengths recorded." />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <Title order={4}>Concerns</Title>
            <EvidenceList items={evaluation.concerns} empty="No concerns recorded." />
          </Grid.Col>
        </Grid>

        <Divider />

        <Grid>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <AlignmentSection title="Technical alignment" section={evaluation.technical_alignment} />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <AlignmentSection title="Seniority alignment" section={evaluation.seniority_alignment} />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <AlignmentSection title="Compensation alignment" section={evaluation.compensation_alignment} />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <AlignmentSection title="Remote/location alignment" section={evaluation.remote_alignment} />
          </Grid.Col>
          <Grid.Col span={12}>
            <AlignmentSection title="Resume alignment" section={evaluation.resume_alignment} />
          </Grid.Col>
        </Grid>

        <Grid>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <Title order={4}>ATS keyword gaps</Title>
            {evaluation.missing_keywords.length > 0 ? (
              <Group gap="xs">
                {evaluation.missing_keywords.map((keyword) => (
                  <Badge key={keyword} variant="light" color="yellow">
                    {keyword}
                  </Badge>
                ))}
              </Group>
            ) : (
              <Text c="dimmed">No keyword gaps recorded.</Text>
            )}
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <Title order={4}>Unsupported claim warnings</Title>
            <EvidenceList
              items={unsupportedWarnings}
              empty="No unsupported claim warnings recorded."
            />
          </Grid.Col>
        </Grid>

        {evaluation.error_message || evaluation.raw_evaluation_json?.ai_failure_reason ? (
          <Text size="sm" c="dimmed">
            AI fallback: {evaluation.error_message ?? evaluation.raw_evaluation_json.ai_failure_reason}
          </Text>
        ) : null}
      </Stack>
    </Paper>
  );
}
