import {
  Badge,
  Box,
  Button,
  Group,
  SimpleGrid,
  Spoiler,
  Stack,
  Text,
  ThemeIcon,
} from "@mantine/core";
import { IconAlertTriangle, IconArrowRight, IconInfoCircle } from "@tabler/icons-react";
import { Link } from "react-router-dom";
import type {
  Insight,
  InsightGenerationMethod,
  InsightScope,
  InsightSeverity,
} from "../types/insights";

export function InsightMeta({
  confidence,
  basis,
  insight,
}: {
  confidence: string;
  basis?: string;
  insight?: Insight;
}) {
  if (insight) {
    return <InsightMetadata insight={insight} />;
  }

  return (
    <>
      <Group justify="space-between" align="flex-start">
        <Badge variant="light">{confidence}</Badge>
      </Group>
      {basis ? (
        <Text size="xs" c="dimmed">
          {basis}
        </Text>
      ) : null}
    </>
  );
}

export function InsightListSection({
  insights,
  emptyTitle,
  emptyMessage,
  limit = 8,
}: {
  insights: Insight[];
  emptyTitle: string;
  emptyMessage: string;
  limit?: number;
}) {
  const visibleInsights = insights.slice(0, limit);

  if (visibleInsights.length === 0) {
    return <InsightEmptyState title={emptyTitle} message={emptyMessage} />;
  }

  return (
    <Stack gap={0}>
      {visibleInsights.map((insight) => (
        <InsightRow key={insight.id} insight={insight} />
      ))}
    </Stack>
  );
}

export function InsightRow({ insight }: { insight: Insight }) {
  return (
    <Box py="sm" style={{ borderTop: "1px solid var(--mantine-color-gray-2)" }}>
      <Stack gap="xs">
        <Group justify="space-between" align="flex-start" gap="sm">
          <Group gap="xs" align="flex-start" wrap="nowrap">
            <ThemeIcon
              variant="light"
              color={severityColor(insight.severity)}
              aria-label={`Severity: ${formatLabel(insight.severity)}`}
              mt={2}
            >
              {isRiskSeverity(insight.severity) ? (
                <IconAlertTriangle size={16} />
              ) : (
                <IconInfoCircle size={16} />
              )}
            </ThemeIcon>
            <div>
              <Group gap="xs">
                <Text fw={600}>{insight.label}</Text>
                <Badge color={severityColor(insight.severity)} variant="light">
                  {formatLabel(insight.severity)}
                </Badge>
                {insight.priority !== null ? (
                  <Badge variant="outline">Priority {insight.priority}</Badge>
                ) : null}
              </Group>
              <Text size="sm" c="dimmed">
                {insight.message}
              </Text>
            </div>
          </Group>
          <InsightAction insight={insight} />
        </Group>

        <InsightMetadata insight={insight} />
      </Stack>
    </Box>
  );
}

export function InsightEmptyState({
  title,
  message,
}: {
  title: string;
  message: string;
}) {
  return (
    <Box py="md">
      <Stack gap={4}>
        <Text fw={600}>{title}</Text>
        <Text c="dimmed" size="sm">
          {message}
        </Text>
      </Stack>
    </Box>
  );
}

function InsightMetadata({ insight }: { insight: Insight }) {
  const detailItems = [
    { label: "Basis", value: insight.basis },
    { label: "Confidence", value: insight.confidence_explanation },
    {
      label: "Uncertainty",
      value: insight.known_uncertainty.length
        ? insight.known_uncertainty.join("; ")
        : null,
    },
    {
      label: "Warnings",
      value: insight.warnings.length ? insight.warnings.join("; ") : null,
    },
    {
      label: "Sources",
      value: insight.source_references.length
        ? insight.source_references
            .map((source) =>
              source.field
                ? `${source.label} (${formatLabel(source.source_type)}: ${source.field})`
                : `${source.label} (${formatLabel(source.source_type)})`,
            )
            .join("; ")
        : null,
    },
  ].filter((item): item is { label: string; value: string } => Boolean(item.value));

  return (
    <Stack gap={4}>
      <Group gap="xs">
        <Badge variant="light">{insight.confidence}</Badge>
        <Badge variant="outline">{formatLabel(insight.confidence_level)}</Badge>
        <Badge variant="outline">{generationLabel(insight.generation_method)}</Badge>
        <Badge variant="outline">{scopeLabel(insight.scope)}</Badge>
        {insight.freshness.is_stale ? (
          <Badge color="yellow" variant="light">
            Stale
          </Badge>
        ) : null}
      </Group>
      <Text size="xs" c="dimmed">
        Generated {formatDateTime(insight.freshness.generated_at)}
        {insight.freshness.source_updated_at
          ? `; source updated ${formatDateTime(insight.freshness.source_updated_at)}`
          : ""}
        {insight.freshness.refresh_reason
          ? `; refresh reason: ${insight.freshness.refresh_reason}`
          : ""}
      </Text>
      {detailItems.length > 0 ? (
        <Spoiler maxHeight={26} showLabel="Show insight basis" hideLabel="Hide insight basis">
          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="xs">
            {detailItems.map((item) => (
              <div key={item.label}>
                <Text size="xs" fw={600}>
                  {item.label}
                </Text>
                <Text size="xs" c="dimmed">
                  {item.value}
                </Text>
              </div>
            ))}
          </SimpleGrid>
        </Spoiler>
      ) : null}
    </Stack>
  );
}

function InsightAction({ insight }: { insight: Insight }) {
  const action = insight.recommended_action;

  if (!action) {
    return null;
  }

  if (action.route_path) {
    return (
      <Button
        component={Link}
        to={action.route_path}
        size="xs"
        variant="light"
        rightSection={<IconArrowRight size={14} />}
      >
        {action.label}
      </Button>
    );
  }

  return (
    <Badge color={action.review_required ? "yellow" : "gray"} variant="light">
      {action.review_required ? "Review required: " : ""}
      {action.label}
    </Badge>
  );
}

function severityColor(severity: InsightSeverity) {
  if (severity === "critical" || severity === "warning") return "red";
  if (severity === "caution") return "yellow";
  if (severity === "positive") return "green";
  return "blue";
}

function isRiskSeverity(severity: InsightSeverity) {
  return severity === "critical" || severity === "warning" || severity === "caution";
}

function generationLabel(method: InsightGenerationMethod) {
  if (method === "ai_generated") return "AI generated";
  if (method === "user_authored") return "User authored";
  return formatLabel(method);
}

function scopeLabel(scope: InsightScope) {
  if (scope.opportunity_id) return "Opportunity";
  if (scope.application_id) return "Application";
  if (scope.artifact_id) return "Artifact";
  if (scope.compass_evaluation_id) return "COMPASS";
  if (scope.workspace_id) return "Search track";
  return scope.user_scoped ? "All workspaces" : "General";
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatLabel(value: string) {
  return value.replaceAll("_", " ");
}
