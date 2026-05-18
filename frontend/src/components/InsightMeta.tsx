import { Badge, Group, Text } from "@mantine/core";

export function InsightMeta({
  confidence,
  basis,
}: {
  confidence: string;
  basis?: string;
}) {
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
