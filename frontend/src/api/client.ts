import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";
export const STATIC_BASE_URL = API_BASE_URL.replace("/api", "");

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Types
export interface Project {
  id: number;
  case_number: string;
  case_title: string;
  description?: string;
  location?: string;
  incident_date?: string;
  examiner_name: string;
  examiner_id?: string;
  laboratory?: string;
  status: string;
  created_at: string;
  updated_at: string;
  image_count?: number;
}

export interface ValidationWarning {
  severity: "info" | "warning" | "error";
  message: string;
  code: string;
}

export interface ValidationFlags {
  missing_metadata?: boolean;
  low_quality?: boolean;
  low_resolution?: boolean;
  insufficient_features?: boolean;
  potentially_irrelevant?: boolean;
  missing_gps?: boolean;
  missing_timestamp?: boolean;
  missing_camera_info?: boolean;
}

export interface ValidationSummary {
  total: number;
  suitable: number;
  with_warnings: number;
  rejected: number;
  verified: number;
  average_forensic_score: number;
  warning_summary: Record<string, number>;
  overall_recommendation: string;
}

export interface Image {
  id: number;
  project_id: number;
  filename: string;
  filepath: string;
  file_hash: string;
  width?: number;
  height?: number;
  gps_latitude?: number;
  gps_longitude?: number;
  date_taken?: string;
  uploaded_at: string;
  is_processed: boolean;
  quality_score?: number;
  // Forensic validation fields
  forensic_score?: number;
  is_verified?: boolean;
  is_suitable?: boolean;
  validation_warnings?: ValidationWarning[];
  validation_flags?: ValidationFlags;
}

export interface Reconstruction {
  id: number;
  project_id: number;
  status: string;
  num_images_used?: number;
  num_points?: number;
  num_faces?: number;
  scale_factor: number;
  estimated_accuracy_cm?: number;
  started_at?: string;
  completed_at?: string;
}

export interface Measurement {
  id: number;
  project_id: number;
  measurement_type: string;
  name: string;
  description?: string;
  coordinates: Array<{ x: number; y: number; z: number }>;
  value?: number;
  unit?: string;
  uncertainty?: number;
  created_by: string;
  created_at: string;
}

export interface GpsImagesResponse {
  images: Image[];
  total_with_gps: number;
  suitable_with_gps: number;
  rejected_with_gps: number;
  message?: string;
}

// API Functions
export const projectsAPI = {
  list: () => apiClient.get<Project[]>("/projects"),
  get: (id: number) => apiClient.get<Project>(`/projects/${id}`),
  create: (data: Partial<Project>) =>
    apiClient.post<Project>("/projects", data),
  update: (id: number, data: Partial<Project>) =>
    apiClient.put<Project>(`/projects/${id}`, data),
  delete: (id: number) => apiClient.delete(`/projects/${id}`),
};

export const imagesAPI = {
  list: (projectId: number) =>
    apiClient.get<Image[]>(`/projects/${projectId}/images`),
  upload: (projectId: number, files: FormData) =>
    apiClient.post<Image[]>(`/projects/${projectId}/images`, files, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  getMetadata: (imageId: number) =>
    apiClient.get<Image>(`/images/${imageId}/metadata`),
  verify: (imageId: number) => apiClient.post(`/images/${imageId}/verify`),
  unverify: (imageId: number) => apiClient.delete(`/images/${imageId}/verify`),
  getValidationSummary: (projectId: number) =>
    apiClient.get<ValidationSummary>(
      `/projects/${projectId}/images/validation-summary`,
    ),
  revalidate: (projectId: number) =>
    apiClient.post<{
      message: string;
      validated: number;
      rejected: number;
      suitable: number;
    }>(`/projects/${projectId}/images/revalidate`),
  getGpsImages: (projectId: number) =>
    apiClient.get<GpsImagesResponse>(`/projects/${projectId}/images/gps`),
};

export const reconstructionAPI = {
  start: (projectId: number, data: { quality: string }) =>
    apiClient.post<Reconstruction>(`/projects/${projectId}/reconstruct`, data),
  getStatus: (projectId: number) =>
    apiClient.get<Reconstruction>(
      `/projects/${projectId}/reconstruction/status`,
    ),
};

export const measurementsAPI = {
  list: (projectId: number) =>
    apiClient.get<Measurement[]>(`/projects/${projectId}/measurements`),
  create: (projectId: number, data: Partial<Measurement>) =>
    apiClient.post<Measurement>(`/projects/${projectId}/measurements`, data),
};

export const reportsAPI = {
  generate: (projectId: number, data: any) =>
    apiClient.post(`/projects/${projectId}/report/generate`, data),
  download: (projectId: number) =>
    apiClient.get(`/projects/${projectId}/report`, { responseType: "blob" }),
  getAuditLog: (projectId: number) =>
    apiClient.get(`/projects/${projectId}/audit-log`),
};

export default apiClient;
