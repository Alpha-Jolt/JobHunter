'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { templatesApi, type CreateTemplateInput } from '@/lib/api/templates'

const STALE = 2 * 60_000 // 2min

export function useTemplates() {
  return useQuery({
    queryKey: ['templates'],
    queryFn: () => templatesApi.list(),
    staleTime: STALE
  })
}

export function useTemplateVersions(id: string, page = 1) {
  return useQuery({
    queryKey: ['templates', id, 'versions', page],
    queryFn: () => templatesApi.getVersions(id, page),
    staleTime: STALE
  })
}

export function useCreateTemplate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (input: CreateTemplateInput) => templatesApi.create(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['templates'] })
  })
}

export function useUpdateTemplate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: Partial<CreateTemplateInput> }) =>
      templatesApi.update(id, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['templates'] })
  })
}

export function useDeleteTemplate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => templatesApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['templates'] })
  })
}

export function useRollbackTemplate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, version }: { id: string; version: number }) =>
      templatesApi.rollback(id, version),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['templates'] })
  })
}
