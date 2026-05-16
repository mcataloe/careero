export type ApplicationWorkflowState =
  | "discovered"
  | "interested"
  | "applied"
  | "interviewing"
  | "offer"
  | "rejected"
  | "withdrawn"
  | "archived";

export interface Application {
  id: string;
  workspaceId: string;
  opportunityId: string;
  currentState: ApplicationWorkflowState;
  availableNextStates: ApplicationWorkflowState[];
  // Placeholders for expanded models (Opportunity refs, timestamps)
  title?: string;
  company?: string;
}

export interface ApplicationStateTransitionRequest {
  newState: ApplicationWorkflowState;
  reason?: string;
  changedBy?: "user" | "system" | "automation";
}

export type ApplicationPipeline = Record<
  Exclude<ApplicationWorkflowState, "archived">,
  Application[]
>;
