// Centralized API error normalization (T046)
export interface ApiErrorMeta {
  status?: number;
  endpoint?: string;
  original?: unknown;
}

export class ApiError extends Error {
  meta: ApiErrorMeta;
  constructor(message: string, meta: ApiErrorMeta = {}) {
    super(message);
    this.meta = meta;
  }
}

export function toApiError(err: any, endpoint: string): ApiError {
  const status = err?.response?.status;
  const message = err?.response?.data?.error || err.message || 'Request failed';
  return new ApiError(message, { status, endpoint, original: err });
}
