import { UserRole, Users } from "./types";

type AccountUsersReponse = {
  account_id: string;
  name: string;
  users: {
    id: string;
    name: string;
    email: string;
    user_role_on_account: "admin" | "technical" | "billing";
    last_login_at: string;
  }[];
};

type ParsedAccountUsersResponse = {
  accountId: string;
  organisationName: string;
  users: Users;
};

const parseAccountsResponse = (
  response: AccountUsersReponse
): ParsedAccountUsersResponse => ({
  accountId: response.account_id,
  organisationName: response.name,
  users: response.users.map((user) => ({
    id: user.email,
    name: user.name,
    email: user.email,
    role: user.user_role_on_account,
    lastLoginAt: user.last_login_at,
  })),
});

const requestAccountUsers = async (): Promise<ParsedAccountUsersResponse> => {
  const response = await fetch(
    `/advantage/account-users${window.location.search}`,
    {
      cache: "no-store",
    }
  );

  return response.json().then(parseAccountsResponse);
};

const accountUserRequestInit: RequestInit = {
  cache: "no-store",
  credentials: "include",
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
};

const getAccountUserRequestUrl = (accountId: string, urlParams: string) =>
  `/advantage/accounts/${accountId}/user${urlParams}`;

type JSONResponse = {
  data?: Record<string, unknown>;
  error?: string;
  errors?: string;
};

const handleResponse = async (response: Response): Promise<JSONResponse> => {
  const responseJson: JSONResponse = await response.json();

  if (!response.ok) {
    throw new Error(responseJson.error || responseJson.errors);
  }
  return responseJson;
};

const fetchJSON = async (
  input: RequestInfo,
  init?: RequestInit
): Promise<JSONResponse> => fetch(input, init).then(handleResponse);

const requestAddUser = ({
  accountId,
  email,
  name,
  role,
}: {
  accountId: string;
  email: string;
  name: string;
  role: UserRole;
}): Promise<JSONResponse> =>
  fetchJSON(getAccountUserRequestUrl(accountId, window.location.search), {
    ...accountUserRequestInit,
    method: "POST",
    body: JSON.stringify({ email, name, role }),
  });

const requestUpdateUser = ({
  accountId,
  email,
  role,
}: {
  accountId: string;
  email: string;
  role: UserRole;
}): Promise<JSONResponse> =>
  fetchJSON(getAccountUserRequestUrl(accountId, window.location.search), {
    ...accountUserRequestInit,
    method: "PUT",
    body: JSON.stringify({ email, role }),
  });

const requestDeleteUser = async ({
  accountId,
  email,
}: {
  accountId: string;
  email: string;
}): Promise<JSONResponse> =>
  fetchJSON(getAccountUserRequestUrl(accountId, window.location.search), {
    ...accountUserRequestInit,
    method: "DELETE",
    body: JSON.stringify({ email }),
  });

export {
  requestAccountUsers,
  requestAddUser,
  requestUpdateUser,
  requestDeleteUser,
};