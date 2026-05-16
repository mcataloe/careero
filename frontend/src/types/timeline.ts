export interface TimelineEvent {
  id: string;
  applicationId: string;
  eventType: string;
  title: string;
  description?: string;
  occurredAt: string;
  actor: string;
  sourceType: string;
  sourceId: string;
  metadata?: Record<string, unknown>;
}
