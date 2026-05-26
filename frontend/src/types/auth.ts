export interface AuthUser {
  id: string;
  username: string | null;
  email: string;
  display_name: string;
  auth_method: string;
  account_status: string;
  created_at: string;
}

export interface LoginPayload {
  username_or_email: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  display_name: string;
  password: string;
}
