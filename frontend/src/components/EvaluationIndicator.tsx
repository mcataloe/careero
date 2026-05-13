import { Badge, Group, Loader, Text } from "@mantine/core";

import type { EvaluationSummaryState } from "../types/strideEvaluations";

function titleize(value: string | null | undefined) {
  return value ? value.replaceAll("_", " ") : "-";
}

function colorForRecommendation(value: string | null | undefined) {
  if (value === "apply") return "green";
  if (value === "monitor") return "blue";
  if (value === "skip") return "red";
  return "yellow";
}

export function EvaluationIndicator({ state }: { state?: EvaluationSummaryState }) {
  if (!state || state.status === "loading") {
    return (
      <Group gap="xs">
        <Loader size="xs" />
        <Text size="sm" c="dimmed">
          Loading
        </Text>
      </Group>
    );
  }

  if (state.status === "not_evaluated") {
    return <Badge variant="light">Not evaluated</Badge>;
  }

  if (state.status === "error") {
    return <Badge color="red">Error</Badge>;
  }

  const { evaluation } = state;
  return (
    <Group gap="xs">
      <Badge color={colorForRecommendation(evaluation.recommendation)}>
        {evaluation.overall_score ?? "-"}
      </Badge>
      <Text size="sm">{titleize(evaluation.recommendation)}</Text>
    </Group>
  );
}
