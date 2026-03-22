import axios, { AxiosRequestConfig, AxiosResponse } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// Directly get token from localStorage
const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null
  try {
    return localStorage.getItem('auth.accessToken')
  } catch (error) {
    console.error('Error accessing localStorage:', error)
    return null
  }
}

// Add auth header to requests
const withAuth = (config?: AxiosRequestConfig): AxiosRequestConfig => {
  const headers = {
    ...(config?.headers || {}),
  } as Record<string, string>

  const token = getAuthToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  return {
    ...(config || {}),
    withCredentials: true,
    headers,
  }
}

// RESPONSE INTERCEPTOR - ADD THIS
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear invalid token
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth.accessToken');
        localStorage.removeItem('auth.refreshToken');
        
        // Don't redirect if already on login page
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export const apiClient = {
  get: async <T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return axios.get<T>(`${API_BASE_URL}${url}`, withAuth(config))
  },
  
  post: async <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return axios.post<T>(`${API_BASE_URL}${url}`, data, withAuth(config))
  },
  
  put: async <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return axios.put<T>(`${API_BASE_URL}${url}`, data, withAuth(config))
  },
  
  delete: async <T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> => {
    return axios.delete<T>(`${API_BASE_URL}${url}`, withAuth(config))
  },
  
  upload: async <T = any>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void,
    fieldName: string = 'file'
  ): Promise<AxiosResponse<T>> => {
    const formData = new FormData()
    formData.append(fieldName, file)

    return axios.post<T>(`${API_BASE_URL}${url}`, formData, withAuth({
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (event) => {
        if (!event.total) return
        const progress = Math.round((event.loaded / event.total) * 100)
        onProgress?.(progress)
      },
    }))
  },
}

export const setAuthToken = (token: string | null) => {
  if (typeof window !== 'undefined') {
    if (token) {
      localStorage.setItem('auth.accessToken', token)
    } else {
      localStorage.removeItem('auth.accessToken')
    }
  }
}
