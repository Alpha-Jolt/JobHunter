import { apiClient } from './client'
import type { WorkspaceUser, FlatRole } from '@/lib/types/api'

export const adminApi = {
  listUsers: () =>
    apiClient.get<{ success: boolean; users: WorkspaceUser[] }>('/api/admin/users'),

  inviteUser: (email: string, role: FlatRole) =>
    apiClient.post<{ success: boolean; user: WorkspaceUser }>('/api/admin/users', { email, role }),

  changeRole: (userId: string, role: FlatRole) =>
    apiClient.put<{ success: boolean }>(`/api/admin/users/${userId}/role`, { role }),

  removeUser: (userId: string) =>
    apiClient.delete<{ success: boolean }>(`/api/admin/users/${userId}`)
}
