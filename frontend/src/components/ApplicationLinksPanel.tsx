import {
  Button,
  Card,
  Group,
  Select,
  Stack,
  Text,
  TextInput,
} from "@mantine/core";
import { useState } from "react";

import {
  createApplicationLink,
  deleteApplicationLink,
  updateApplicationLink,
} from "../api/applications";
import type {
  ApplicationExternalLink,
  ApplicationExternalLinkPayload,
  ApplicationExternalLinkType,
} from "../types/applications";

const LINK_TYPE_OPTIONS: { value: ApplicationExternalLinkType; label: string }[] = [
  { value: "job_posting", label: "Job posting" },
  { value: "company_careers", label: "Company careers" },
  { value: "recruiter_profile", label: "Recruiter profile" },
  { value: "application_portal", label: "Application portal" },
  { value: "interview_prep", label: "Interview prep" },
  { value: "email_thread", label: "Email thread" },
  { value: "other", label: "Other" },
];

function linkTypeLabel(value: string | null) {
  if (!value) {
    return "Other";
  }
  return LINK_TYPE_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

const emptyLink: ApplicationExternalLinkPayload = {
  label: "",
  url: "",
  type: "other",
};

export function ApplicationLinksPanel({
  applicationId,
  links,
  onChanged,
}: {
  applicationId: string;
  links: ApplicationExternalLink[];
  onChanged: () => Promise<void>;
}) {
  const [draft, setDraft] = useState<ApplicationExternalLinkPayload>(emptyLink);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editDraft, setEditDraft] =
    useState<ApplicationExternalLinkPayload>(emptyLink);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canCreate = Boolean(draft.label.trim() && draft.url.trim());
  const canEdit = Boolean(editDraft.label.trim() && editDraft.url.trim());

  async function submitCreate() {
    if (!canCreate) {
      return;
    }
    await runMutation(async () => {
      await createApplicationLink(applicationId, {
        label: draft.label.trim(),
        url: draft.url.trim(),
        type: draft.type,
      });
      setDraft(emptyLink);
    });
  }

  function startEdit(link: ApplicationExternalLink) {
    setEditingId(link.id);
    setEditDraft({
      label: link.label,
      url: link.url,
      type: link.type ?? "other",
      metadata: link.metadata,
    });
    setError(null);
  }

  async function submitEdit(linkId: string) {
    if (!canEdit) {
      return;
    }
    await runMutation(async () => {
      await updateApplicationLink(applicationId, linkId, {
        label: editDraft.label.trim(),
        url: editDraft.url.trim(),
        type: editDraft.type,
      });
      setEditingId(null);
    });
  }

  async function deleteLink(linkId: string) {
    await runMutation(async () => {
      await deleteApplicationLink(applicationId, linkId);
      if (editingId === linkId) {
        setEditingId(null);
      }
    });
  }

  async function runMutation(mutation: () => Promise<void>) {
    setBusy(true);
    setError(null);
    try {
      await mutation();
      await onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update links");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card withBorder radius="md" p="lg">
      <Stack gap="md">
        <div>
          <Text fw={600}>External links</Text>
          <Text size="sm" c="dimmed">
            Keep job postings, portals, recruiter profiles, and prep resources
            attached to this workflow.
          </Text>
        </div>

        <Stack gap="sm">
          <Group align="end" grow>
            <TextInput
              label="Label"
              placeholder="Job posting"
              value={draft.label}
              onChange={(event) =>
                setDraft((current) => ({
                  ...current,
                  label: event.currentTarget.value,
                }))
              }
            />
            <TextInput
              label="URL"
              placeholder="https://example.com"
              value={draft.url}
              onChange={(event) =>
                setDraft((current) => ({
                  ...current,
                  url: event.currentTarget.value,
                }))
              }
            />
          </Group>
          <Group justify="space-between" align="end">
            <Select
              label="Link type"
              value={draft.type ?? "other"}
              data={LINK_TYPE_OPTIONS}
              onChange={(value) =>
                setDraft((current) => ({
                  ...current,
                  type: (value as ApplicationExternalLinkType | null) ?? "other",
                }))
              }
              w={{ base: "100%", sm: 240 }}
            />
            <Button onClick={submitCreate} loading={busy} disabled={!canCreate}>
              Add link
            </Button>
          </Group>
        </Stack>

        {error ? (
          <Text c="red" size="sm" role="alert">
            {error}
          </Text>
        ) : null}

        {links.length === 0 ? (
          <Text c="dimmed" size="sm">
            No external links yet.
          </Text>
        ) : (
          <Stack gap="sm">
            {links.map((link) => (
              <Card key={link.id} withBorder radius="sm" p="md">
                {editingId === link.id ? (
                  <Stack gap="sm">
                    <Group align="end" grow>
                      <TextInput
                        label="Label"
                        value={editDraft.label}
                        onChange={(event) =>
                          setEditDraft((current) => ({
                            ...current,
                            label: event.currentTarget.value,
                          }))
                        }
                      />
                      <TextInput
                        label="URL"
                        value={editDraft.url}
                        onChange={(event) =>
                          setEditDraft((current) => ({
                            ...current,
                            url: event.currentTarget.value,
                          }))
                        }
                      />
                    </Group>
                    <Group justify="space-between" align="end">
                      <Select
                        label="Link type"
                        value={editDraft.type ?? "other"}
                        data={LINK_TYPE_OPTIONS}
                        onChange={(value) =>
                          setEditDraft((current) => ({
                            ...current,
                            type:
                              (value as ApplicationExternalLinkType | null) ??
                              "other",
                          }))
                        }
                        w={{ base: "100%", sm: 240 }}
                      />
                      <Group gap="xs">
                        <Button
                          variant="default"
                          onClick={() => setEditingId(null)}
                          disabled={busy}
                        >
                          Cancel
                        </Button>
                        <Button
                          onClick={() => submitEdit(link.id)}
                          loading={busy}
                          disabled={!canEdit}
                        >
                          Save link
                        </Button>
                      </Group>
                    </Group>
                  </Stack>
                ) : (
                  <Group justify="space-between" align="flex-start">
                    <div>
                      <Text
                        component="a"
                        href={link.url}
                        target="_blank"
                        rel="noreferrer noopener"
                        fw={600}
                      >
                        {link.label}
                      </Text>
                      <Text size="xs" c="dimmed">
                        {linkTypeLabel(link.type)}
                      </Text>
                    </div>
                    <Group gap="xs">
                      <Button
                        size="xs"
                        variant="default"
                        onClick={() => startEdit(link)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="xs"
                        variant="outline"
                        color="red"
                        onClick={() => deleteLink(link.id)}
                        loading={busy}
                      >
                        Delete
                      </Button>
                    </Group>
                  </Group>
                )}
              </Card>
            ))}
          </Stack>
        )}
      </Stack>
    </Card>
  );
}
