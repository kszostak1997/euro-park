export default defineNuxtRouteMiddleware(async () => {
  const { ensureCurrentUser } = useAuth()

  if (!(await ensureCurrentUser())) {
    return navigateTo('/login')
  }
})
