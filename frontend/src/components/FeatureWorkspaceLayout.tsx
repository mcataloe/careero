import { NavLink, Paper, Stack } from "@mantine/core";
import { NavLink as RouterNavLink } from "react-router-dom";

export interface FeatureWorkspaceNavItem {
  id: string;
  label: string;
  description?: string;
  to: string;
}

export function FeatureWorkspaceLayout({
  navLabel,
  items,
  activeId,
  withDetailPanel = true,
  children,
}: {
  navLabel: string;
  items: FeatureWorkspaceNavItem[];
  activeId: string;
  withDetailPanel?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="feature-workspace">
      <Paper
        className="feature-local-navigation"
        component="nav"
        aria-label={navLabel}
        withBorder
        radius="md"
        p="sm"
      >
        <Stack gap={2}>
          {items.map((item) => (
            <NavLink
              key={item.id}
              component={RouterNavLink}
              to={item.to}
              label={item.label}
              description={item.description}
              active={item.id === activeId}
              aria-current={item.id === activeId ? "page" : undefined}
            />
          ))}
        </Stack>
      </Paper>
      {withDetailPanel ? (
        <Paper className="feature-detail-panel" withBorder radius="md" p="lg">
          {children}
        </Paper>
      ) : (
        <div className="feature-detail-panel">{children}</div>
      )}
    </div>
  );
}
