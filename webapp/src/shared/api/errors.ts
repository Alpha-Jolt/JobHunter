export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly fields?: Record<string, string>
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export class UnauthorizedError extends ApiError {
  constructor(message = "Session expired. Please log in again.") {
    super(401, "UNAUTHORIZED", message);
    this.name = "UnauthorizedError";
  }
}

export class ForbiddenError extends ApiError {
  constructor(message = "You don't have permission to do that.") {
    super(403, "FORBIDDEN", message);
    this.name = "ForbiddenError";
  }
}

export class RateLimitError extends ApiError {
  constructor(message = "Too many requests. Please wait before trying again.") {
    super(429, "RATE_LIMIT", message);
    this.name = "RateLimitError";
  }
}

export function parseApiError(status: number, data: unknown): ApiError {
  if (typeof data === "object" && data !== null) {
    const d = data as Record<string, unknown>;
    const code = typeof d["code"] === "string" ? d["code"] : "API_ERROR";
    const message =
      typeof d["message"] === "string"
        ? d["message"]
        : typeof d["detail"] === "string"
          ? d["detail"]
          : "An error occurred.";
    const fields =
      typeof d["errors"] === "object" && d["errors"] !== null
        ? (d["errors"] as Record<string, string>)
        : undefined;
    if (status === 401) return new UnauthorizedError(message);
    if (status === 403) return new ForbiddenError(message);
    if (status === 429) return new RateLimitError(message);
    return new ApiError(status, code, message, fields);
  }
  return new ApiError(status, "API_ERROR", "An unexpected error occurred.");
}
