import type { Role } from "./types/roles";

export const sampleRole: Role = {
  id: "11111111-1111-4111-8111-111111111111",
  title: "Senior Backend Engineer",
  company_id: "22222222-2222-4222-8222-222222222222",
  source_id: "33333333-3333-4333-8333-333333333333",
  job_url: "https://www.linkedin.com/jobs/view/example",
  location: "Chicago, IL",
  remote_type: "hybrid",
  compensation_min: "120000.00",
  compensation_max: "150000.00",
  compensation_currency: "USD",
  raw_description: "Raw pasted job description",
  normalized_description: "Normalized job description",
  status: "found",
  date_found: "2026-05-13",
  date_posted: "2026-05-01",
  created_at: "2026-05-13T12:00:00Z",
  updated_at: "2026-05-13T12:00:00Z",
  company: {
    id: "22222222-2222-4222-8222-222222222222",
    name: "Example Company",
    website_url: "https://example.com",
  },
  source: {
    id: "33333333-3333-4333-8333-333333333333",
    name: "LinkedIn manual",
    source_type: "linkedin_manual",
  },
};
