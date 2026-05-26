import {
  Alert,
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
import type { ReactNode } from "react";

import type {
  EvaluationSection,
  EvidenceItem,
  CompassEvaluation,
} from "../types/compassEvaluations";
import { ExpandableTextSection } from "./ExpandableTextSection";
import { MarkdownPreviewBlock } from "./MarkdownPreviewBlock";
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

function aiStatusLabel(evaluation: CompassEvaluation) {
  const aiStatus = evaluation.ai_status ?? evaluation.raw_evaluation_json?.ai_status;
  if (aiStatus === "skipped") return "Skipped AI fallback";
  if (aiStatus === "failed") return "AI failed";
  if (aiStatus === "completed") return "AI enriched";
  return "Deterministic";
}

function evaluationStatus(evaluation: CompassEvaluation) {
  return evaluation.evaluation_status ?? evaluation.status ?? "completed";
}

function overallScore(evaluation: CompassEvaluation) {
  return scoreNumber(evaluation.overall_score ?? evaluation.overallScore);
}

function recommendation(evaluation: CompassEvaluation) {
  return evaluation.recommendation ?? evaluation.recommendations?.decision ?? null;
}

function confidenceLevel(evaluation: CompassEvaluation) {
  return evaluation.confidence_level ?? evaluation.confidence?.level ?? null;
}

function sectionSummary(section: EvaluationSection | null | undefined) {
  return section?.notes ?? section?.summary ?? "No details available.";
}

function evidenceText(evidence: EvidenceItem["evidence"]) {
  if (Array.isArray(evidence)) return evidence.join("; ");
  return evidence ?? null;
}

function sectionFromCanonical(
  evaluation: CompassEvaluation,
  key: keyof NonNullable<CompassEvaluation["sections"]>,
  fallback: EvaluationSection | null | undefined,
) {
  return evaluation.sections?.[key] ?? fallback;
}

function evidenceItemsFromStrings(values: string[] | undefined, labelPrefix: string) {
  return (values ?? []).map((value) => ({
    label: value,
    message: value,
    code: `${labelPrefix}_${value}`,
  }));
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
      {safeItems.map((item, index) => {
        const body = item.message ?? item.label ?? item.code ?? "Evaluation item";
        const details = item.notes ?? evidenceText(item.evidence);

        return (
          <List.Item key={`${item.code ?? item.label ?? item.message ?? "item"}-${index}`}>
            <Stack gap={2}>
              <Text>{body}</Text>
              {details ? (
                <Text size="sm" c="dimmed">
                  {item.notes ? "Notes" : "Evidence"}: {details}
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
        );
      })}
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
        <ExpandableTextSection maxHeight={180}>
          <MarkdownPreviewBlock value={sectionSummary(section)} />
        </ExpandableTextSection>
        {Array.isArray(section?.evidence) && section.evidence.length > 0 ? (
          <Text size="sm" c="dimmed">
            Evidence: {section.evidence.join("; ")}
          </Text>
        ) : null}
        {Array.isArray(section?.gaps) && section.gaps.length > 0 ? (
          <Text size="sm" c="dimmed">
            Gaps: {section.gaps.join("; ")}
          </Text>
        ) : null}
      </Stack>
    </Paper>
  );
}

function EvaluationSectionBlock({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <section id={id}>
      <Stack gap="sm">
        <Title order={3}>{title}</Title>
        {children}
      </Stack>
    </section>
  );
}

export function EvaluationStatusBadge({
  evaluation,
  loading = false,
  error,
}: {
  evaluation: CompassEvaluation | null;
  loading?: boolean;
  error?: string | null;
}) {
  if (loading) return <Badge variant="light">Loading evaluation</Badge>;
  if (error) return <Badge color="red">Evaluation error</Badge>;
  if (!evaluation) return <Badge variant="light">Not evaluated</Badge>;
  if (evaluationStatus(evaluation) === "failed") return <Badge color="red">Validation failed</Badge>;
  const aiStatus = evaluation.ai_status ?? evaluation.raw_evaluation_json?.ai_status;
  if (aiStatus === "skipped") {
    return <Badge color="yellow">Skipped AI fallback</Badge>;
  }
  if (aiStatus === "failed") {
    return <Badge color="orange">AI failed</Badge>;
  }
  return <Badge color="green">Completed</Badge>;
}

export function CompassEvaluationDetail({
  evaluation,
  onRun,
  running = false,
  onViewLatest,
}: {
  evaluation: CompassEvaluation | null;
  onRun: (force?: boolean) => Promise<void> | void;
  running?: boolean;
  onViewLatest?: () => void;
}) {
  if (!evaluation) {
    return (
      <Paper withBorder radius="md" p="lg">
        <EmptyState
          title="Not evaluated"
          message="Run COMPASS evaluation to create a local recommendation for this opportunity."
          action={
            <Button loading={running} onClick={() => onRun(false)}>
              Run COMPASS evaluation
            </Button>
          }
        />
      </Paper>
    );
  }

  const score = overallScore(evaluation);
  const decision = recommendation(evaluation);
  const confidence = confidenceLevel(evaluation);
  const unsupportedWarnings =
    evaluation.raw_evaluation_json?.ai_result?.unsupported_claim_warnings ?? [];
  const evidenceGaps = evaluation.raw_evaluation_json?.ai_result?.evidence_gaps ?? [];
  const positioningOpportunities =
    evaluation.raw_evaluation_json?.ai_result?.positioning_opportunities ?? [];
  const validationIssues = evaluation.raw_evaluation_json?.validationIssues ?? [];
  const status = evaluationStatus(evaluation);
  const atsKeywords = evaluation.ats_keywords ?? evaluation.atsFindings?.matchedKeywords ?? [];
  const missingKeywords =
    evaluation.missing_keywords ?? evaluation.atsFindings?.missingKeywords ?? [];
  const assumptions = evaluation.assumptions ?? [];
  const gaps =
    evaluation.gaps && evaluation.gaps.length > 0 ? evaluation.gaps : evidenceGaps;
  const risks =
    evaluation.risks && evaluation.risks.length > 0 ? evaluation.risks : evaluation.concerns ?? [];
  const compensationSection =
    sectionFromCanonical(evaluation, "compensationAlignment", evaluation.compensation_alignment) ??
    evaluation.compensationFindings;
  const remoteSection = sectionFromCanonical(evaluation, "remoteAlignment", evaluation.remote_alignment);

  return (
    <Paper withBorder radius="md" p="lg">
      <Stack gap="lg">
        <Group justify="space-between" align="flex-start">
          <Stack gap={4}>
            <Title order={3}>COMPASS evaluation</Title>
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

        {status === "failed" ? (
          <Alert color="red" title="Validation failed">
            This evaluation did not produce a completed validated result. Review the fallback details before relying on it.
          </Alert>
        ) : null}

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
                <Badge size="lg" color={recommendationColor(decision)}>
                  {titleize(decision)}
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
                  {titleize(confidence)}
                </Badge>
              </Stack>
            </Paper>
          </Grid.Col>
        </Grid>

        <EvaluationSectionBlock id="compass-summary" title="Summary">
          <ExpandableTextSection maxHeight={220}>
            <MarkdownPreviewBlock value={evaluation.summary ?? "No summary available."} />
          </ExpandableTextSection>
        </EvaluationSectionBlock>

        <EvaluationSectionBlock id="compass-fit-analysis" title="Fit analysis">
          <Grid>
            <Grid.Col span={{ base: 12, md: 6 }}>
              <AlignmentSection
                title="Strategic fit"
                section={sectionFromCanonical(evaluation, "strategicFit", undefined)}
              />
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 6 }}>
              <AlignmentSection
                title="Technical alignment"
                section={sectionFromCanonical(evaluation, "technicalAlignment", evaluation.technical_alignment)}
              />
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 6 }}>
              <AlignmentSection
                title="Seniority alignment"
                section={sectionFromCanonical(evaluation, "seniorityAlignment", evaluation.seniority_alignment)}
              />
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 6 }}>
              <AlignmentSection
                title="Resume alignment"
                section={sectionFromCanonical(evaluation, "atsResumeAlignment", evaluation.resume_alignment)}
              />
            </Grid.Col>
          </Grid>
        </EvaluationSectionBlock>

        <Grid>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <EvaluationSectionBlock id="compass-strengths" title="Strengths">
              <EvidenceList items={evaluation.strengths} empty="No strengths recorded." />
            </EvaluationSectionBlock>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <EvaluationSectionBlock id="compass-gaps" title="Gaps">
              <EvidenceList items={gaps} empty="No gaps recorded." />
            </EvaluationSectionBlock>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <EvaluationSectionBlock id="compass-risks" title="Risks">
              <EvidenceList items={risks} empty="No risks recorded." />
            </EvaluationSectionBlock>
          </Grid.Col>
        </Grid>

        <Divider />

        <Grid>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <EvaluationSectionBlock id="compass-ats-findings" title="ATS findings">
              <Stack gap="sm">
                <Text size="sm" c="dimmed">
                  Matched keywords
                </Text>
                {atsKeywords.length > 0 ? (
                  <Group gap="xs">
                    {atsKeywords.map((keyword) => (
                      <Badge key={keyword} variant="light" color="green">
                        {keyword}
                      </Badge>
                    ))}
                  </Group>
                ) : (
                  <Text c="dimmed">No ATS keywords recorded.</Text>
                )}
                <Text size="sm" c="dimmed">
                  Keyword gaps
                </Text>
                {missingKeywords.length > 0 ? (
                  <Group gap="xs">
                    {missingKeywords.map((keyword) => (
                      <Badge key={keyword} variant="light" color="yellow">
                        {keyword}
                      </Badge>
                    ))}
                  </Group>
                ) : (
                  <Text c="dimmed">No keyword gaps recorded.</Text>
                )}
              </Stack>
            </EvaluationSectionBlock>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <EvaluationSectionBlock id="compass-compensation" title="Compensation">
              <AlignmentSection title="Compensation alignment" section={compensationSection} />
            </EvaluationSectionBlock>
          </Grid.Col>
        </Grid>

        <Grid>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <EvaluationSectionBlock id="compass-remote-fit" title="Remote fit">
              <AlignmentSection title="Remote/location alignment" section={remoteSection} />
            </EvaluationSectionBlock>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <EvaluationSectionBlock id="compass-interview-positioning" title="Interview positioning">
              <EvidenceList
                items={[
                  ...positioningOpportunities,
                  ...evidenceItemsFromStrings(
                    evaluation.recommendations?.nextActions,
                    "next_action",
                  ),
                ]}
                empty="No interview positioning guidance recorded."
              />
            </EvaluationSectionBlock>
          </Grid.Col>
        </Grid>

        <EvaluationSectionBlock id="compass-recommendations" title="Recommendations">
          <Stack gap="sm">
            <Badge size="lg" color={recommendationColor(decision)}>
              {titleize(decision)}
            </Badge>
            <ExpandableTextSection maxHeight={180}>
              <MarkdownPreviewBlock
                value={
                  evaluation.recommendations?.rationale ??
                  "No recommendation rationale recorded."
                }
              />
            </ExpandableTextSection>
          </Stack>
        </EvaluationSectionBlock>

        <EvaluationSectionBlock id="compass-assumptions-confidence" title="Assumptions / confidence">
          <Grid>
            <Grid.Col span={{ base: 12, md: 6 }}>
              <Paper withBorder radius="md" p="md">
                <Stack gap="xs">
                  <Title order={4}>Confidence</Title>
                  <Badge variant="light">{titleize(confidence)}</Badge>
                  {evaluation.confidence?.score !== undefined ? (
                    <Progress value={(evaluation.confidence.score ?? 0) * 100} />
                  ) : null}
                  <ExpandableTextSection maxHeight={160}>
                    <MarkdownPreviewBlock
                      value={
                        evaluation.confidence?.rationale ??
                        "No confidence rationale recorded."
                      }
                    />
                  </ExpandableTextSection>
                </Stack>
              </Paper>
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 6 }}>
              <Paper withBorder radius="md" p="md">
                <Stack gap="xs">
                  <Title order={4}>Assumptions</Title>
                  {assumptions.length > 0 ? (
                    <List spacing="xs">
                      {assumptions.map((assumption) => (
                        <List.Item key={assumption}>{assumption}</List.Item>
                      ))}
                    </List>
                  ) : (
                    <Text c="dimmed">No assumptions recorded.</Text>
                  )}
                </Stack>
              </Paper>
            </Grid.Col>
          </Grid>
        </EvaluationSectionBlock>

        <EvaluationSectionBlock id="compass-unsupported-warnings" title="Unsupported claim warnings">
          <EvidenceList
            items={unsupportedWarnings}
            empty="No unsupported claim warnings recorded."
          />
        </EvaluationSectionBlock>

        {validationIssues.length > 0 ? (
          <EvaluationSectionBlock id="compass-validation-issues" title="Validation issues">
            <EvidenceList
              items={validationIssues.map((issue, index) => ({
                code: `validation_issue_${index}`,
                message:
                  typeof issue === "object" && issue !== null && "message" in issue
                    ? String(issue.message)
                    : String(issue),
              }))}
              empty="No validation issues recorded."
            />
          </EvaluationSectionBlock>
        ) : null}

        {evaluation.error_message || evaluation.raw_evaluation_json?.ai_failure_reason ? (
          <Text size="sm" c="dimmed">
            AI fallback: {evaluation.error_message ?? evaluation.raw_evaluation_json?.ai_failure_reason}
          </Text>
        ) : null}
      </Stack>
    </Paper>
  );
}
