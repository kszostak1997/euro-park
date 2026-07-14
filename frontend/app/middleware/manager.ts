const ALLOWED_ROLES = new Set(['MANAGER', 'ADMIN'])

export default defineNuxtRouteMiddleware(() => {
  const { user } = useAuth()

  if (!user.value || !ALLOWED_ROLES.has(user.value.role)) {
    return navigateTo('/user')
  }
})
