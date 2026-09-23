# Guia de Desacoplamento do Frontend (React / TanStack)

Este guia orienta a remoção cirúrgica de `@supabase/supabase-js` e a adoção do cliente REST tipado consumindo a API em Go.

---

## 1. Implementação do `api-client.ts` (`src/lib/api-client.ts`)

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export class ApiError extends Error {
  constructor(public status: number, message: string, public data?: any) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('r7_access_token') : null;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    let errorData: any;
    try {
      errorData = await response.json();
    } catch {
      errorData = { error: response.statusText };
    }
    throw new ApiError(response.status, errorData.error || errorData.message || 'Request failed', errorData);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'GET' }),
  post: <T>(endpoint: string, body?: any, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(endpoint: string, body?: any, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: 'PATCH', body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(endpoint: string, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'DELETE' }),
};
```

---

## 2. Refatoração do Hook de Autenticação (`src/hooks/use-auth.ts`)

```typescript
import { useState, useEffect, createContext, useContext } from 'react';
import { apiClient } from '@/lib/api-client';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  role?: string;
  organization_id?: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('r7_access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    apiClient.get<User>('/auth/me')
      .then(setUser)
      .catch(() => {
        localStorage.removeItem('r7_access_token');
        localStorage.removeItem('r7_refresh_token');
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = async (email: string, password: string) => {
    const res = await apiClient.post<{ access_token: string; refresh_token: string; user: User }>('/auth/login', { email, password });
    localStorage.setItem('r7_access_token', res.access_token);
    localStorage.setItem('r7_refresh_token', res.refresh_token);
    setUser(res.user);
    return res.user;
  };

  const logout = () => {
    localStorage.removeItem('r7_access_token');
    localStorage.removeItem('r7_refresh_token');
    setUser(null);
  };

  return { user, loading, login, logout };
}
```

---

## 3. Substituição de Queries em Componentes

| Padrão Antigo (Supabase) | Padrão Novo (API Go REST) |
| :--- | :--- |
| `supabase.from('campaigns').select('*')` | `apiClient.get<Campaign[]>('/campaigns')` |
| `supabase.from('leads').insert(data)` | `apiClient.post('/leads', data)` |
| `supabase.rpc('portal_ambassador_leads', { slug })` | `apiClient.get('/public/portal/' + slug)` |
| `supabase.auth.signInWithPassword({ ... })` | `login(email, password)` |

---

## 4. Validação de Build de Produção

Em aplicações TanStack Start / Nitro, execute o build com target para servidor Node:

```bash
# Build de produção local
NITRO_PRESET=node-server npm run build

# O artefato de execução é gerado em:
# .output/server/index.mjs
```
