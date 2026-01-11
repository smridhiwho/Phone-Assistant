import { useQuery, useMutation } from '@tanstack/react-query'
import { productApi } from '../services/api'
import { CompareRequest } from '../types'

export function useProducts(params?: {
  brand?: string
  min_price?: number
  max_price?: number
  limit?: number
}) {
  return useQuery({
    queryKey: ['products', params],
    queryFn: () => productApi.getAll(params),
  })
}

export function useProduct(id: number) {
  return useQuery({
    queryKey: ['product', id],
    queryFn: () => productApi.getById(id),
    enabled: !!id,
  })
}

export function useCompareProducts() {
  return useMutation({
    mutationFn: (request: CompareRequest) => productApi.compare(request),
  })
}

export function useFlagshipPhones() {
  return useQuery({
    queryKey: ['products', 'flagship'],
    queryFn: () => productApi.getFlagship(),
  })
}

export function useBudgetPhones(maxPrice?: number) {
  return useQuery({
    queryKey: ['products', 'budget', maxPrice],
    queryFn: () => productApi.getBudget(maxPrice),
  })
}

export function useGamingPhones() {
  return useQuery({
    queryKey: ['products', 'gaming'],
    queryFn: () => productApi.getGaming(),
  })
}

export function useCameraPhones() {
  return useQuery({
    queryKey: ['products', 'camera'],
    queryFn: () => productApi.getCamera(),
  })
}
