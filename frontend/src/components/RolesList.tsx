import { Badge, Button, Paper, Stack, Table, Text, Title } from "@mantine/core";
import { Link } from "react-router-dom";

import type { Role } from "../types/roles";
import type { EvaluationSummaryState } from "../types/compassEvaluations";
import { EvaluationIndicator } from "./EvaluationIndicator";
import { EmptyState } from "./States";

export function RolesList({
  roles,
  evaluationStates = {},
}: {
  roles: Role[];
  evaluationStates?: Record<string, EvaluationSummaryState>;
}) {
  if (roles.length === 0) {
    return (
      <EmptyState
        title="No opportunities yet"
        message="Add an opportunity you found manually so it is ready for later COMPASS evaluation."
        action={
          <Button component={Link} to="/opportunities/new">
            Add opportunity
          </Button>
        }
      />
    );
  }

  return (
    <Paper withBorder radius="md">
      <Table.ScrollContainer minWidth={780}>
        <Table verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Opportunity</Table.Th>
              <Table.Th>Company</Table.Th>
              <Table.Th>Source</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>COMPASS</Table.Th>
              <Table.Th>Location</Table.Th>
              <Table.Th>Date found</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {roles.map((role) => (
              <Table.Tr key={role.id}>
                <Table.Td>
                  <Stack gap={2}>
                    <Title order={5}>
                      <Link to={`/opportunities/${role.id}`}>{role.title}</Link>
                    </Title>
                    {role.job_url ? (
                      <Text size="xs" c="dimmed" truncate="end">
                        {role.job_url}
                      </Text>
                    ) : null}
                  </Stack>
                </Table.Td>
                <Table.Td>{role.company.name}</Table.Td>
                <Table.Td>{role.source?.name ?? "Unknown"}</Table.Td>
                <Table.Td>
                  <Badge variant="light">{role.status}</Badge>
                </Table.Td>
                <Table.Td>
                  <EvaluationIndicator state={evaluationStates[role.id]} />
                </Table.Td>
                <Table.Td>{role.location ?? "-"}</Table.Td>
                <Table.Td>{role.date_found}</Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Table.ScrollContainer>
    </Paper>
  );
}
