import axios from 'axios';
import { supabase } from '@/supabase';
import router from '@/routers'; // Make sure this import is correct

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || import.meta.env.VITE_BACKEND_URL,
});

// Add a request interceptor to automatically attach the auth token
apiClient.interceptors.request.use(async (config) => {
  // Skip interceptor for URLs that contain OAuth parameters or are not API calls
  const isOAuthCallback =
    config.url?.includes('access_token=') ||
    config.url?.includes('provider_token=') ||
    config.url?.includes('error=') ||
    config.url?.includes('error_code=') ||
    config.url?.includes('error_description=') ||
    config.url?.includes('/auth/') ||
    config.url?.startsWith('/documents/access_token') || // This is your specific case
    !config.url?.startsWith('/'); // Skip if not a relative path

  if (isOAuthCallback) {
    console.warn('Skipping API interceptor for OAuth callback URL:', config.url);
    return Promise.reject(new Error('OAuth callback URL - not an API request'));
  }

  try {
    const { data: { session } } = await supabase.auth.getSession();

    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }

    return config;
  } catch (error) {
    return Promise.reject(error);
  }
}, (error) => {
  return Promise.reject(error);
});

// Add a response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Check if this is an OAuth callback error
    if (error.config?.url?.includes('access_token=') ||
      error.config?.url?.includes('error=')) {
      console.error('OAuth callback intercepted as API request:', error.config.url);
      return Promise.reject(new Error('OAuth callback intercepted - check your OAuth flow'));
    }

    // Don't try to refresh token on login/signup pages to prevent redirect loops
    const currentRoute = router.currentRoute.value;
    if (currentRoute.name === 'signin' || currentRoute.name === 'signup') {
      return Promise.reject(error);
    }

    // Check if the error is a 401 and we haven't already retried the request
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const { data, error: refreshError } = await supabase.auth.refreshSession();

        if (refreshError || !data.session) {
          router.push({ name: 'landing' });
          return Promise.reject(refreshError || new Error('Session refresh failed.'));
        }

        return apiClient(originalRequest);
      } catch (e) {
        return Promise.reject(e);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;