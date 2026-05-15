import { Button, Group, Paper, ScrollArea } from "@mantine/core";

export interface SectionNavigationItem {
  label: string;
  targetId: string;
}

export function SectionNavigation({ items }: { items: SectionNavigationItem[] }) {
  function scrollToSection(targetId: string) {
    document.getElementById(targetId)?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  return (
    <Paper
      withBorder
      radius="md"
      p="xs"
      style={{
        position: "sticky",
        top: 8,
        zIndex: 20,
        background: "var(--mantine-color-body)",
      }}
    >
      <ScrollArea type="never" offsetScrollbars scrollbarSize={4}>
        <Group gap="xs" wrap="nowrap">
          {items.map((item) => (
            <Button
              key={item.targetId}
              component="a"
              href={`#${item.targetId}`}
              variant="default"
              size="sm"
              className="section-navigation__link"
              onClick={(event) => {
                event.preventDefault();
                scrollToSection(item.targetId);
              }}
              style={{ flex: "0 0 auto" }}
            >
              {item.label}
            </Button>
          ))}
        </Group>
      </ScrollArea>
    </Paper>
  );
}
