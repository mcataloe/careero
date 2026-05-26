import {
  Alert,
  Badge,
  Button,
  Checkbox,
  Group,
  Paper,
  Stack,
  Table,
  Text,
  Title,
} from "@mantine/core";
import { IconFileExport, IconRefresh, IconTrashX } from "@tabler/icons-react";
import { useEffect, useState } from "react";

import {
  cancelAccountLifecycleRequest,
  createAccountLifecycleRequest,
  listAccountLifecycleRequests,
} from "../api/accountLifecycle";
import { ErrorState, LoadingState } from "./States";
import type { AccountLifecycleRequest } from "../types/accountLifecycle";

function formatType(value: string) {
  return value.replaceAll("_", " ");
}

export function AccountLifecyclePanel() {
  const [requests, setRequests] = useState<AccountLifecycleRequest[]>([]);
  const [note, setNote] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [confirmDeletion, setConfirmDeletion] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadRequests() {
    setLoading(true);
    setError(null);
    try {
      const response = await listAccountLifecycleRequests();
      setRequests(response.requests);
      setNote(response.lifecycle_note);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load lifecycle requests");
    } finally {
      setLoading(false);
    }
  }

  async function recordRequest(requestType: "data_export" | "account_deletion") {
    setSaving(true);
    setStatus(null);
    setError(null);
    try {
      const request = await createAccountLifecycleRequest({
        request_type: requestType,
        request_reason:
          requestType === "account_deletion"
            ? "User recorded a local deletion request from Settings."
            : "User recorded a local export request from Settings.",
        deletion_confirmation:
          requestType === "account_deletion" ? "record deletion request" : undefined,
      });
      setRequests((current) => [request, ...current]);
      setStatus(request.message);
      setConfirmDeletion(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not record lifecycle request");
    } finally {
      setSaving(false);
    }
  }

  async function cancelRequest(requestId: string) {
    setSaving(true);
    setStatus(null);
    setError(null);
    try {
      const updated = await cancelAccountLifecycleRequest(requestId);
      setRequests((current) =>
        current.map((request) => (request.id === updated.id ? updated : request)),
      );
      setStatus("Lifecycle request canceled locally.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not cancel request");
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => {
    void loadRequests();
  }, []);

  if (loading) {
    return <LoadingState label="Loading account lifecycle requests" />;
  }

  if (error && requests.length === 0) {
    return <ErrorState message={error} onRetry={loadRequests} />;
  }

  return (
    <Paper withBorder radius="md" p="lg">
      <Stack gap="md">
        <Group justify="space-between" align="flex-start">
          <div>
            <Title order={3}>Account lifecycle requests</Title>
            <Text c="dimmed" size="sm" mt="xs">
              Record local export or deletion requests without changing stored data.
            </Text>
          </div>
          <Button
            variant="light"
            leftSection={<IconRefresh size={18} />}
            onClick={loadRequests}
          >
            Refresh
          </Button>
        </Group>

        <Alert color="blue">
          {note ??
            "Lifecycle requests are local audit records only and do not delete data."}
        </Alert>

        <Group align="flex-end">
          <Button
            leftSection={<IconFileExport size={18} />}
            loading={saving}
            onClick={() => void recordRequest("data_export")}
          >
            Record export request
          </Button>
          <Stack gap={6}>
            <Checkbox
              checked={confirmDeletion}
              label="I understand this records a request and does not delete data."
              onChange={(event) => setConfirmDeletion(event.currentTarget.checked)}
            />
            <Button
              color="red"
              variant="light"
              leftSection={<IconTrashX size={18} />}
              disabled={!confirmDeletion}
              loading={saving}
              onClick={() => void recordRequest("account_deletion")}
            >
              Record deletion request
            </Button>
          </Stack>
        </Group>

        {status ? (
          <Text c="green" size="sm" role="status">
            {status}
          </Text>
        ) : null}
        {error ? (
          <Text c="red" size="sm" role="alert">
            {error}
          </Text>
        ) : null}

        {requests.length === 0 ? (
          <Text c="dimmed" size="sm">
            No local lifecycle requests have been recorded.
          </Text>
        ) : (
          <Table.ScrollContainer minWidth={640}>
            <Table verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Type</Table.Th>
                  <Table.Th>Status</Table.Th>
                  <Table.Th>Requested</Table.Th>
                  <Table.Th>Action</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {requests.map((request) => (
                  <Table.Tr key={request.id}>
                    <Table.Td>{formatType(request.request_type)}</Table.Td>
                    <Table.Td>
                      <Badge variant="light">{formatType(request.status)}</Badge>
                    </Table.Td>
                    <Table.Td>{new Date(request.requested_at).toLocaleString()}</Table.Td>
                    <Table.Td>
                      {request.status === "requested" ? (
                        <Button
                          size="xs"
                          variant="subtle"
                          loading={saving}
                          onClick={() => void cancelRequest(request.id)}
                        >
                          Cancel
                        </Button>
                      ) : (
                        <Text c="dimmed" size="sm">
                          No action
                        </Text>
                      )}
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        )}
      </Stack>
    </Paper>
  );
}
