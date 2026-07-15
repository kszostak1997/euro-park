export interface BarrierCheckResult {
  registration_number: string
  access_granted: boolean
}

export function useBarrier() {
  const { api } = useApiClient()

  function checkAccess(registrationNumber: string): Promise<BarrierCheckResult> {
    return api<BarrierCheckResult>('/barrier/check-access', {
      method: 'POST',
      body: { registration_number: registrationNumber },
    })
  }

  return { checkAccess }
}
