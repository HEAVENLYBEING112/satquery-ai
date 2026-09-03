// frontend/src/api/assets.ts
import { isMockMode } from './client';
import { AssetUploadResponse, Modality } from '../types/engine';
import { mockUploadAsset } from './mock/mockService';

/**
 * Uploads a satellite image file (GeoTIFF, TIFF, PNG, JPEG)
 */
export async function uploadAsset(file: File, modality: Modality = 'optical'): Promise<AssetUploadResponse> {
  if (isMockMode()) {
    return mockUploadAsset(file, modality);
  }

  // FUTURE BACKEND API:
  // const formData = new FormData();
  // formData.append('file', file);
  // const res = await fetch(`${getApiBaseUrl()}/api/v1/assets`, { method: 'POST', body: formData });
  // return res.json();
  return mockUploadAsset(file, modality);
}
