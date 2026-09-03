// frontend/src/api/client.ts
// Configurable API Client with automatic fallback to mockService

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'; // Defaults to mock mode for frontend-only

export const isMockMode = (): boolean => USE_MOCK;
export const getApiBaseUrl = (): string => BASE_URL;

export async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  // FUTURE BACKEND API CALL:
  const url = `${BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `API Error: ${response.status} ${response.statusText}`);
    }

    return (await response.json()) as T;
  } catch (err: any) {
    console.warn(`[SatQuery API] Live endpoint ${endpoint} unreachable, fallback will be used:`, err.message);
    throw err;
  }
}
