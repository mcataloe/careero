import { Alert, Button, Group, Stack } from "@mantine/core";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { archiveRole, getRole, updateRole } from "../api/roles";
import { RoleDetail } from "../components/RoleDetail";
import { ErrorState, LoadingState } from "../components/States";
import type { Role, RoleUpdatePayload } from "../types/roles";

export function RoleDetailPage() {
  const { roleId } = useParams();
  const navigate = useNavigate();
  const [role, setRole] = useState<Role | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [archiving, setArchiving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function loadRole() {
    if (!roleId) return;
    setLoading(true);
    setError(null);
    try {
      setRole(await getRole(roleId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load role");
    } finally {
      setLoading(false);
    }
  }

  async function handleUpdate(payload: RoleUpdatePayload) {
    if (!roleId) return;
    setSaving(true);
    setError(null);
    setNotice(null);
    try {
      setRole(await updateRole(roleId, payload));
      setNotice("Role updated");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update role");
    } finally {
      setSaving(false);
    }
  }

  async function handleArchive() {
    if (!roleId) return;
    setArchiving(true);
    setError(null);
    try {
      await archiveRole(roleId);
      navigate("/roles");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not archive role");
      setArchiving(false);
    }
  }

  useEffect(() => {
    void loadRole();
  }, [roleId]);

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <Button component={Link} to="/roles" variant="subtle">
          Back to roles
        </Button>
      </Group>

      {notice ? <Alert color="green">{notice}</Alert> : null}
      {loading ? <LoadingState label="Loading role" /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={loadRole} /> : null}
      {!loading && !error && role ? (
        <RoleDetail
          role={role}
          onUpdate={handleUpdate}
          onArchive={handleArchive}
          saving={saving}
          archiving={archiving}
        />
      ) : null}
    </Stack>
  );
}
