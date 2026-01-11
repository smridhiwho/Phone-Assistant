export interface Phone {
  id: number;
  brand: string;
  model: string;
  price_inr: number;
  display_size?: number;
  display_type?: string;
  display_resolution?: string;
  refresh_rate?: number;
  processor?: string;
  ram_gb?: number;
  storage_gb?: number;
  rear_camera?: string;
  front_camera?: string;
  battery_mah?: number;
  fast_charging_w?: number;
  wireless_charging?: boolean;
  os?: string;
  launch_year?: number;
  dimensions?: string;
  weight_g?: number;
  features?: string[];
  colors?: string[];
  highlights?: string;
  image_url?: string;
  created_at?: string;
}

export interface PhoneListResponse {
  products: Phone[];
  count: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  products?: Phone[];
  suggestions?: string[];
  timestamp: Date;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  context?: Record<string, unknown>;
}

export interface ChatResponse {
  response: string;
  products: Phone[];
  intent: string;
  suggestions: string[];
  session_id: string;
}

export interface ComparisonSpec {
  spec_name: string;
  values: Record<string, string>;
  winner?: string;
}

export interface CompareRequest {
  product_ids: number[];
}

export interface CompareResponse {
  phones: Phone[];
  comparison: ComparisonSpec[];
  summary: string;
  recommendation?: string;
}

export interface SearchRequest {
  query: string;
  filters?: SearchFilters;
}

export interface SearchFilters {
  brand?: string;
  min_price?: number;
  max_price?: number;
  min_ram?: number;
  min_battery?: number;
  features?: string[];
}

export interface SearchResponse {
  products: Phone[];
  explanation: string;
  count: number;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  database_connected: boolean;
  version: string;
}
