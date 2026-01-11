import axios from 'axios'
import {
  ChatRequest,
  ChatResponse,
  Phone,
  PhoneListResponse,
  CompareRequest,
  CompareResponse,
  SearchRequest,
  SearchResponse,
  HealthResponse,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Chat endpoints
export const chatApi = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat/message', request)
    return response.data
  },

  getHistory: async (sessionId: string): Promise<{ messages: ChatResponse[] }> => {
    const response = await api.get(`/chat/history/${sessionId}`)
    return response.data
  },

  createSession: async (): Promise<{ session_id: string }> => {
    const response = await api.post('/chat/session')
    return response.data
  },

  clearHistory: async (sessionId: string): Promise<void> => {
    await api.delete(`/chat/history/${sessionId}`)
  },
}

// Product endpoints
export const productApi = {
  getAll: async (params?: {
    brand?: string
    min_price?: number
    max_price?: number
    limit?: number
  }): Promise<PhoneListResponse> => {
    const response = await api.get<PhoneListResponse>('/products', { params })
    return response.data
  },

  getById: async (id: number): Promise<Phone> => {
    const response = await api.get<Phone>(`/products/${id}`)
    return response.data
  },

  search: async (request: SearchRequest): Promise<SearchResponse> => {
    const response = await api.post<SearchResponse>('/products/search', request)
    return response.data
  },

  compare: async (request: CompareRequest): Promise<CompareResponse> => {
    const response = await api.post<CompareResponse>('/products/compare', request)
    return response.data
  },

  getByBrand: async (brand: string): Promise<PhoneListResponse> => {
    const response = await api.get<PhoneListResponse>(`/products/brand/${brand}`)
    return response.data
  },

  getFlagship: async (): Promise<PhoneListResponse> => {
    const response = await api.get<PhoneListResponse>('/products/category/flagship')
    return response.data
  },

  getBudget: async (maxPrice?: number): Promise<PhoneListResponse> => {
    const response = await api.get<PhoneListResponse>('/products/category/budget', {
      params: { max_price: maxPrice },
    })
    return response.data
  },

  getGaming: async (): Promise<PhoneListResponse> => {
    const response = await api.get<PhoneListResponse>('/products/category/gaming')
    return response.data
  },

  getCamera: async (): Promise<PhoneListResponse> => {
    const response = await api.get<PhoneListResponse>('/products/category/camera')
    return response.data
  },
}

// Health endpoint
export const healthApi = {
  check: async (): Promise<HealthResponse> => {
    const response = await api.get<HealthResponse>('/health')
    return response.data
  },
}

export default api
