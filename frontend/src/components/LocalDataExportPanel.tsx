import { Alert, Button, Group, Paper, Stack, Text, Title } from "@mantine/core";
import { IconDownload, IconInfoCircle } from "@tabler/icons-react";
import { useState } from "react";

import { getLocalDataExport } from "../api/dataExport";
import type { LocalDataExport } from "../types/dataExport";

function exportFilename(data: LocalDataExport) {
  const generatedAt = data.metadata.generated_at.replaceAll(":", "-");
  return `careero-local-export-${generatedAt}.json`;
}

function downloadJson(data: LocalDataExport) {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = exportFilename(data);
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

export function LocalDataExportPanel() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleDownload() {
    setLoading(true);
    setStatus(null);
    setError(null);
    try {
      const data = await getLocalDataExport();
      downloadJson(data);
      setStatus(`Export prepared with ${data.opportunities.length} opportunities.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not prepare local export");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Paper withBorder radius="md" p="lg">
      <Stack gap="md">
        <Group justify="space-between" align="flex-start">
          <div>
            <Title order={3}>Local data export</Title>
            <Text c="dimmed" size="sm" mt="xs">
              Download a JSON package of records owned by the current local user.
            </Text>
          </div>
          <Button
            leftSection={<IconDownload size={18} />}
            loading={loading}
            onClick={handleDownload}
          >
            Download JSON
          </Button>
        </Group>

        <Alert color="blue" icon={<IconInfoCircle size={18} />}>
          This export stays in your browser session. It does not create cloud backup,
          public sharing, hosted account export, or production account support.
        </Alert>

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
      </Stack>
    </Paper>
  );
}
