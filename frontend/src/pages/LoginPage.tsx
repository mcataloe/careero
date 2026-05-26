import { useState } from "react";
import {
  Alert,
  Anchor,
  Button,
  Divider,
  Group,
  Paper,
  PasswordInput,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import { IconBrandGoogle, IconBrandLinkedin, IconLogin2 } from "@tabler/icons-react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthProvider";

export function LoginPage() {
  const { currentUser, isLoading, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [usernameOrEmail, setUsernameOrEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!isLoading && currentUser) {
    return <Navigate to="/dashboard" replace />;
  }

  const redirectTo =
    typeof location.state === "object" &&
    location.state !== null &&
    "from" in location.state
      ? String(location.state.from)
      : "/dashboard";

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (!usernameOrEmail.trim() || !password) {
      setError("Enter your username or email and password.");
      return;
    }
    setSubmitting(true);
    try {
      await login({
        username_or_email: usernameOrEmail.trim(),
        password,
      });
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthLayout title="Careero" subtitle="Sign in to your local career workspace.">
      <form onSubmit={handleSubmit}>
        <Stack gap="md">
          {error ? <Alert color="red">{error}</Alert> : null}
          <TextInput
            label="Username or email"
            value={usernameOrEmail}
            onChange={(event) => setUsernameOrEmail(event.currentTarget.value)}
            autoComplete="username"
            required
          />
          <PasswordInput
            label="Password"
            value={password}
            onChange={(event) => setPassword(event.currentTarget.value)}
            autoComplete="current-password"
            required
          />
          <Button
            type="submit"
            leftSection={<IconLogin2 size={18} />}
            loading={submitting}
          >
            Log in
          </Button>
        </Stack>
      </form>

      <Divider label="SSO" labelPosition="center" />
      <Stack gap="sm">
        <Button
          variant="default"
          leftSection={<IconBrandGoogle size={18} />}
          disabled
          aria-label="Continue with Google - coming soon"
        >
          Continue with Google - Coming soon
        </Button>
        <Button
          variant="default"
          leftSection={<IconBrandLinkedin size={18} />}
          disabled
          aria-label="Continue with LinkedIn - coming soon"
        >
          Continue with LinkedIn - Coming soon
        </Button>
      </Stack>

      <Text size="sm" ta="center">
        New to Careero?{" "}
        <Anchor component={Link} to="/register">
          Create an account
        </Anchor>
      </Text>
    </AuthLayout>
  );
}

export function AuthLayout({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <main className="auth-page">
      <Paper withBorder radius="md" p="xl" className="auth-panel">
        <Stack gap="lg">
          <div>
            <Group justify="space-between" align="baseline">
              <Title order={1}>{title}</Title>
              <Text size="sm" c="dimmed">
                Local-first
              </Text>
            </Group>
            <Text c="dimmed">{subtitle}</Text>
          </div>
          {children}
        </Stack>
      </Paper>
    </main>
  );
}
