export default defineNuxtRouteMiddleware(async () => {
  const { ensureCurrentUser } = useAuth()

  const user = await ensureCurrentUser()
  if (user) {
    return navigateTo(roleLandingPath(user.role))
  }
})
