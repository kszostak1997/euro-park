export default defineNuxtRouteMiddleware(async () => {
  const { user, fetchCurrentUser } = useAuth()

  if (!user.value) {
    await fetchCurrentUser()
  }

  if (!user.value) {
    return navigateTo('/login')
  }
})
