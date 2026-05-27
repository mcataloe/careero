import { useState } from "react";
import {
  Alert,
  Anchor,
  Button,
  PasswordInput,
  Stack,
  Text,
  TextInput,
} from "@mantine/core";
import { IconUserPlus } from "@tabler/icons-react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthProvider";
import { AuthLayout } from "./LoginPage";

export function RegisterPage() {
  const { currentUser, isLoading, register } = useAuth();
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!isLoading && currentUser) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (!firstName.trim() || !lastName.trim() || !email.trim() || !password) {
      setError("Complete all fields to create your account.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      await register({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        password,
      });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthLayout title="Create your Careero account" subtitle="Use your professional name, email, and password for this workspace.">
      <form onSubmit={handleSubmit}>
        <Stack gap="md">
          {error ? <Alert color="red">{error}</Alert> : null}
          <TextInput
            label="First name"
            value={firstName}
            onChange={(event) => setFirstName(event.currentTarget.value)}
            autoComplete="given-name"
            required
          />
          <TextInput
            label="Email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.currentTarget.value)}
            autoComplete="email"
            required
          />
          <TextInput
            label="Last name"
            value={lastName}
            onChange={(event) => setLastName(event.currentTarget.value)}
            autoComplete="family-name"
            required
          />
          <PasswordInput
            label="Password"
            value={password}
            onChange={(event) => setPassword(event.currentTarget.value)}
            autoComplete="new-password"
            required
          />
          <PasswordInput
            label="Confirm password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.currentTarget.value)}
            autoComplete="new-password"
            required
          />
          <Button
            type="submit"
            leftSection={<IconUserPlus size={18} />}
            loading={submitting}
          >
            Create account
          </Button>
        </Stack>
      </form>
      <Text size="sm" ta="center">
        Already have an account?{" "}
        <Anchor component={Link} to="/login">
          Log in
        </Anchor>
      </Text>
    </AuthLayout>
  );
}
