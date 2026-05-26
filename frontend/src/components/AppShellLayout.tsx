import {
  AppShell as MantineAppShell,
  Burger,
  Button,
  Group,
  NavLink,
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
} from "@tabler/icons-react";
import { NavLink as RouterNavLink, useLocation } from "react-router-dom";

import { useAuth } from "../auth/AuthProvider";

const navItems = [
  { label: "Dashboard", to: "/dashboard", icon: IconGauge },
  { label: "Strategy", to: "/strategy", icon: IconRoute },
  { label: "Opportunities", to: "/opportunities", icon: IconBriefcase },
  { label: "Applications", to: "/applications", icon: IconClipboardList },
  { label: "Settings", to: "/settings", icon: IconSettings },
];

export function AppShellLayout({ children }: { children: React.ReactNode }) {
  const [opened, { toggle }] = useDisclosure();
  const location = useLocation();
  const { currentUser, logout } = useAuth();
  const userLabel =
    currentUser?.display_name || currentUser?.username || currentUser?.email || "User";

  return (
    <MantineAppShell
      header={{ height: 64 }}
      navbar={{
        width: 240,
        breakpoint: "sm",
        collapsed: { mobile: !opened },
      }}
      padding="lg"
    >
      <MantineAppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group gap="sm">
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
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

      <MantineAppShell.Navbar p="md">
        <Stack gap={4}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const active =
              location.pathname === item.to ||
              (item.to !== "/dashboard" && location.pathname.startsWith(item.to));

            return (
              <NavLink
                key={item.to}
                component={RouterNavLink}
                to={item.to}
                label={item.label}
                leftSection={<Icon size={18} />}
                active={active}
              />
            );
          })}
        </Stack>
      </MantineAppShell.Navbar>

      <MantineAppShell.Main>{children}</MantineAppShell.Main>
    </MantineAppShell>
  );
}
