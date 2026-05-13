import { Alert, Button, Center, Loader, Stack, Text, Title } from "@mantine/core";
import { IconAlertCircle, IconInbox } from "@tabler/icons-react";

export function LoadingState({ label = "Loading" }: { label?: string }) {
  return (
    <Center py="xl">
      <Stack align="center" gap="sm">
        <Loader />
        <Text c="dimmed">{label}</Text>
      </Stack>
    </Center>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <Alert icon={<IconAlertCircle size={18} />} color="red" title="Something went wrong">
      <Stack gap="sm">
        <Text>{message}</Text>
        {onRetry ? (
          <Button variant="light" color="red" onClick={onRetry}>
            Try again
          </Button>
        ) : null}
      </Stack>
    </Alert>
  );
}

export function EmptyState({
  title,
  message,
  action,
}: {
  title: string;
  message: string;
  action?: React.ReactNode;
}) {
  return (
    <Center py="xl">
      <Stack align="center" gap="sm">
        <IconInbox size={36} color="var(--mantine-color-gray-5)" />
        <Title order={3}>{title}</Title>
        <Text c="dimmed" ta="center" maw={460}>
          {message}
        </Text>
        {action}
      </Stack>
    </Center>
  );
}
