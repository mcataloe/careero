export interface AuthUser {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  displayName: string;
  salutation: string | null;
  pronouns: string | null;
  headshotUrl: string | null;
  authMethod: string;
  accountStatus: string;
  createdAt: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  firstName: string;
  lastName: string;
  password: string;
}
