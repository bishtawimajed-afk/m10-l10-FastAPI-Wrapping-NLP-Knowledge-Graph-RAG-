import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function handleApiError(error: any): Promise<string> {
  if (!axios.isAxiosError(error)) {
    return "An unexpected error occurred.";
  }
  if (!error.response) {
    return "Could not reach the backend.";
  }
  if (error.response.status === 503) {
    return "The backend is starting up — please try again in a moment.";
  }
  if (error.response.status === 422) {
    return JSON.stringify(error.response.data.detail || error.response.data);
  }
  return error.response.data?.detail || "A backend error occurred.";
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});