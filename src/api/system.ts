// frontend/src/api/system.ts
import { isMockMode } from './client';
import { CapabilitiesResponse, HealthResponse } from '../types/engine';
import { mockGetCapabilities, mockGetHealth } from './mock/mockService';

export async function getSystemHealth(): Promise<HealthResponse> {
  if (isMockMode()) {
    return mockGetHealth();
  }
  // FUTURE BACKEND API:
  // return request<HealthResponse>('/api/v1/health');
  return mockGetHealth();
}

export async function getCapabilities(): Promise<CapabilitiesResponse> {
  if (isMockMode()) {
    return mockGetCapabilities();
  }
  // FUTURE BACKEND API:
  // return request<CapabilitiesResponse>('/api/v1/capabilities');
  return mockGetCapabilities();
}
