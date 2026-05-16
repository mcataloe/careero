import React from "react";
import {
  Grid,
  Card,
  Text,
  Badge,
  Group,
  Title,
  Stack,
  Button,
  ScrollArea,
} from "@mantine/core";
import { Application, ApplicationWorkflowState } from "../types/application";

// Colors matched to canonical states
const stateColors: Record<ApplicationWorkflowState, string> = {
  discovered: "gray",
  interested: "blue",
  applied: "teal",
  interviewing: "violet",
  offer: "green",
  rejected: "red",
  withdrawn: "orange",
  archived: "dark",
};

const ACTIVE_PIPELINE_STATES: Exclude<ApplicationWorkflowState, "archived">[] =
  [
    "discovered",
    "interested",
    "applied",
    "interviewing",
    "offer",
    "rejected",
    "withdrawn",
  ];

interface ApplicationsPipelineProps {
  workspaceId: string;
  pipelineData: Record<string, Application[]>;
  onTransitionState: (
    appId: string,
    newState: ApplicationWorkflowState,
  ) => void;
}

export const ApplicationsPipeline: React.FC<ApplicationsPipelineProps> = ({
  workspaceId,
  pipelineData,
  onTransitionState,
}) => {
  return (
    <Stack p="md">
      <Title order={2}>Application Pipeline</Title>
      <Text color="dimmed" size="sm">
        Manage candidate opportunities grouped by their active workflow state.
      </Text>

      <ScrollArea>
        <div
          style={{
            display: "flex",
            gap: "16px",
            minWidth: "1200px",
            paddingBottom: "16px",
          }}
        >
          {ACTIVE_PIPELINE_STATES.map((state) => (
            <div key={state} style={{ flex: "0 0 300px" }}>
              <Group position="apart" mb="sm">
                <Badge color={stateColors[state]} size="lg" radius="sm">
                  {state.toUpperCase()}
                </Badge>
                <Badge color="gray" variant="filled" size="sm">
                  {pipelineData[state]?.length || 0}
                </Badge>
              </Group>

              <Stack spacing="sm">
                {pipelineData[state]?.map((app) => (
                  <Card key={app.id} shadow="sm" p="sm" radius="md" withBorder>
                    <Group position="apart" mb="xs">
                      <Text weight={600} size="sm" lineClamp={1}>
                        {app.title || "Unknown Role"}
                      </Text>
                    </Group>
                    <Text size="xs" color="dimmed" mb="md" lineClamp={1}>
                      {app.company || "Unknown Company"}
                    </Text>

                    {app.availableNextStates &&
                      app.availableNextStates.length > 0 && (
                        <Group spacing="xs" mt="xs">
                          {app.availableNextStates
                            .filter((next) => next !== "archived") // Keep UI focused on active actions
                            .map((nextState) => (
                              <Button
                                key={nextState}
                                variant="light"
                                size="xs"
                                color={stateColors[nextState]}
                                onClick={() =>
                                  onTransitionState(app.id, nextState)
                                }
                              >
                                Move to {nextState}
                              </Button>
                            ))}
                        </Group>
                      )}
                  </Card>
                ))}
                {(!pipelineData[state] || pipelineData[state].length === 0) && (
                  <Text color="dimmed" size="xs" align="center" mt="md">
                    No applications in this state
                  </Text>
                )}
              </Stack>
            </div>
          ))}
        </div>
      </ScrollArea>
    </Stack>
  );
};
