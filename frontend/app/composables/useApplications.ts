import type { ApplicationInput, ApplicationPage, ApplicationRow } from '~/types/application'

export function useApplications() {
  const { api } = useApiClient()

  function listOwn(): Promise<ApplicationRow[]> {
    return api<ApplicationRow[]>('/applications')
  }

  function create(data: ApplicationInput): Promise<ApplicationRow> {
    return api<ApplicationRow>('/applications', { method: 'POST', body: data })
  }

  function getOwn(id: number): Promise<ApplicationRow> {
    return api<ApplicationRow>(`/applications/${id}`)
  }

  function update(id: number, data: Partial<ApplicationInput>): Promise<ApplicationRow> {
    return api<ApplicationRow>(`/applications/${id}`, { method: 'PATCH', body: data })
  }

  function listAll(
    params: { status?: string; page?: number; size?: number } = {},
  ): Promise<ApplicationPage> {
    return api<ApplicationPage>('/manager/applications', {
      query: { size: 100, ...params },
    })
  }

  function approve(id: number): Promise<ApplicationRow> {
    return api<ApplicationRow>(`/manager/applications/${id}/approve`, { method: 'POST' })
  }

  function reject(id: number): Promise<ApplicationRow> {
    return api<ApplicationRow>(`/manager/applications/${id}/reject`, { method: 'POST' })
  }

  function requestChanges(id: number, comment: string): Promise<ApplicationRow> {
    return api<ApplicationRow>(`/manager/applications/${id}/request-changes`, {
      method: 'POST',
      body: { comment },
    })
  }

  return { listOwn, create, getOwn, update, listAll, approve, reject, requestChanges }
}
