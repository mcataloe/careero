export interface AuthUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  display_name: string;
  auth_method: string;
  account_status: string;
  created_at: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}
