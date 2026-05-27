import {
  AppShell as MantineAppShell,
  ActionIcon,
  Burger,
  Button,
  Group,
  NavLink,
  Paper,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import {
  IconBriefcase,
  IconClipboardList,
  IconGauge,
  IconLogout,
  IconRoute,
  IconSettings,
  IconX,
} from "@tabler/icons-react";
import { useEffect, useId } from "react";
import { NavLink as RouterNavLink, useLocation } from "react-router-dom";

import { useAuth } from "../auth/AuthProvider";

const navItems = [
  { label: "Dashboard", to: "/dashboard", icon: IconGauge },
  { label: "Career strategy", to: "/strategy", icon: IconRoute },
  { label: "Opportunities", to: "/opportunities", icon: IconBriefcase },
  { label: "Applications", to: "/applications", icon: IconClipboardList },
  { label: "Settings", to: "/settings", icon: IconSettings },
];

export function AppShellLayout({ children }: { children: React.ReactNode }) {
  const [opened, { close, toggle }] = useDisclosure(false);
  const location = useLocation();
  const navigationId = useId();
  const { currentUser, logout } = useAuth();
  const userLabel =
    currentUser?.displayName ||
    [currentUser?.firstName, currentUser?.lastName].filter(Boolean).join(" ") ||
    currentUser?.email ||
    "User";

  useEffect(() => {
    close();
  }, [close, location.pathname]);

  return (
    <MantineAppShell
      header={{ height: 64 }}
      padding="lg"
    >
      <MantineAppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group gap="sm">
            <Burger
              aria-controls={navigationId}
              aria-expanded={opened}
              aria-label={opened ? "Close global navigation" : "Open global navigation"}
              opened={opened}
              onClick={toggle}
              size="sm"
            />
            <Title order={3}>Careero</Title>
          </Group>
          <Group gap="sm">
            <Text size="sm" c="dimmed" visibleFrom="sm">
              {userLabel}
            </Text>
            <Button
              variant="subtle"
              size="xs"
              leftSection={<IconLogout size={16} />}
              onClick={() => {
                void logout();
              }}
            >
              Log out
            </Button>
          </Group>
        </Group>
      </MantineAppShell.Header>

      {opened ? (
        <Paper
          id={navigationId}
          className="global-navigation"
          component="nav"
          role="navigation"
          aria-label="Global navigation"
          withBorder
          shadow="lg"
          radius="md"
          p="md"
        >
          <Group justify="space-between" align="center" mb="md">
            <div>
              <Text fw={700}>Careero</Text>
              <Text size="xs" c="dimmed">
                Global navigation
              </Text>
            </div>
            <ActionIcon
              aria-label="Close global navigation"
              variant="subtle"
              onClick={close}
            >
              <IconX size={18} />
            </ActionIcon>
          </Group>
          <Stack gap={4}>
            {navItems.map((item) => {
              const Icon = item.icon;
              const active =
                location.pathname === item.to ||
                (item.to === "/strategy" &&
                  location.pathname.startsWith("/workspaces/")) ||
                (item.to !== "/dashboard" && location.pathname.startsWith(item.to));

              return (
                <NavLink
                  key={item.to}
                  component={RouterNavLink}
                  to={item.to}
                  label={item.label}
                  leftSection={<Icon size={18} />}
                  active={active}
                  aria-current={active ? "page" : undefined}
                />
              );
            })}
          </Stack>
        </Paper>
      ) : null}

      <MantineAppShell.Main>{children}</MantineAppShell.Main>
    </MantineAppShell>
  );
}
