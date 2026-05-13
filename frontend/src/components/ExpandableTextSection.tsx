import { Box, Stack, Spoiler, Text, Title } from "@mantine/core";
import { useState, type ReactNode } from "react";

export function ExpandableTextSection({
  title,
  children,
  maxHeight = 260,
  showLabel = "Show more",
  hideLabel = "Show less",
}: {
  title?: string;
  children: ReactNode;
  maxHeight?: number;
  showLabel?: string;
  hideLabel?: string;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Stack gap="xs">
      {title ? <Title order={4}>{title}</Title> : null}
      <Box pos="relative">
        <Spoiler
          maxHeight={maxHeight}
          showLabel={showLabel}
          hideLabel={hideLabel}
          transitionDuration={180}
          expanded={expanded}
          onExpandedChange={setExpanded}
        >
          {typeof children === "string" ? (
            <Text style={{ whiteSpace: "pre-wrap" }}>{children}</Text>
          ) : (
            children
          )}
        </Spoiler>
        {!expanded ? (
          <Box
            aria-hidden="true"
            className="expandable-text-section__fade"
            pos="absolute"
            bottom={32}
            left={0}
            right={0}
            h={44}
            style={{
              pointerEvents: "none",
              background:
                "linear-gradient(to bottom, rgba(255, 255, 255, 0), var(--mantine-color-body))",
            }}
          />
        ) : null}
      </Box>
    </Stack>
  );
}
