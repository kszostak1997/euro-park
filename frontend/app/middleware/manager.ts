export default defineNuxtRouteMiddleware(() => {
  const { user } = useAuth()

  if (user.value?.role === 'USER') {
    return navigateTo('/user')
  }
})
