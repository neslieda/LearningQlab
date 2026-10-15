import createClient, { type Client, type ClientOptions } from "openapi-fetch";
import type { components, paths } from "./schema";

export type { components, paths };

/** Anything the API may be called with: a bearer token, or none for the public routes. */
export type TokenProvider = () => string | null | undefined | Promise<string | null | undefined>;

export interface ApiClientOptions extends Omit<ClientOptions, "baseUrl"> {
  baseUrl: string;
  /** Called for every request; the result is sent as `Authorization: Bearer <token>`. */
  getToken?: TokenProvider;
}

export type ApiClient = Client<paths>;

export function createApiClient({ baseUrl, getToken, ...options }: ApiClientOptions): ApiClient {
  const client = createClient<paths>({ baseUrl, ...options });
  if (getToken) {
    client.use({
      async onRequest({ request }) {
        const token = await getToken();
        if (token) request.headers.set("Authorization", `Bearer ${token}`);
        return request;
      },
    });
  }
  return client;
}

type Schemas = components["schemas"];

// Convenience aliases; every type comes from the generated schema.
export type Problem = Schemas["Problem"];
export type ProblemItem = Schemas["ProblemItem"];
export type Me = Schemas["Me"];
export type Role = Schemas["Role"];
export type Doc = Schemas["Doc"];
export type QuestionDocument = Schemas["QuestionDocument"];
export type SyllabusOut = Schemas["SyllabusOut"];

export type LearnerQuestion = Schemas["LearnerQuestion"];
export type LearnerQuestionPage = Schemas["LearnerQuestionPage"];
export type LearnerQuestionSummary = Schemas["LearnerQuestionSummary"];
export type McqAnswer = Schemas["McqAnswer"];
export type WrittenAnswer = Schemas["WrittenAnswer"];
export type McqCheckResult = Schemas["McqCheckResult"];
export type WrittenCheckResult = Schemas["WrittenCheckResult"];
export type CheckRequest = McqAnswer | WrittenAnswer;
export type CheckResult = McqCheckResult | WrittenCheckResult;

export type AdminQuestion = Schemas["AdminQuestion"];
export type AdminQuestionPage = Schemas["AdminQuestionPage"];
export type AdminQuestionSummary = Schemas["AdminQuestionSummary"];
export type AdminVersion = Schemas["AdminVersion"];
export type AdminVersionSummary = Schemas["AdminVersionSummary"];
export type VersionStatus = Schemas["VersionStatus"];
export type History = Schemas["History"];
export type HistoryEntry = Schemas["HistoryEntry"];
export type DecisionRequest = Schemas["DecisionRequest"];
export type ReasonRequest = Schemas["ReasonRequest"];
export type RepublishRequest = Schemas["RepublishRequest"];
export type UpdateDraftRequest = Schemas["UpdateDraftRequest"];
