import { Box, Stack, Text } from "@mantine/core";
import type { ReactNode } from "react";

import { ExpandableTextSection } from "./ExpandableTextSection";

export function ReadOnlyField({
  label,
  value,
  empty = "-",
  long = false,
  maxHeight = 260,
  children,
}: {
  label: string;
  value?: string | number | null;
  empty?: string;
  long?: boolean;
  maxHeight?: number;
  children?: ReactNode;
}) {
  const hasValue =
    children !== undefined ||
    (value !== null && value !== undefined && String(value).trim().length > 0);
  const content = children ?? (
    <Text style={{ whiteSpace: "pre-wrap" }}>{hasValue ? value : empty}</Text>
  );

  return (
    <Stack gap={6}>
      <Text size="sm" fw={600} c="dimmed">
        {label}
      </Text>
      <Box className="readonly-field">
        {long ? (
          <ExpandableTextSection maxHeight={maxHeight}>
            {content}
          </ExpandableTextSection>
        ) : (
          content
        )}
      </Box>
    </Stack>
  );
}
