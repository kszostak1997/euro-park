<script setup lang="ts">
const { user, isLoggedIn, logout } = useAuth()
const router = useRouter()

async function handleLogout() {
  logout()
  await router.push('/login')
}
</script>

<template>
  <div>
    <header class="app-header">
      <div class="app-header-left">
        <span class="app-brand">Euro Park</span>
        <nav v-if="isLoggedIn" class="app-tabs">
          <NuxtLink v-if="user?.role === 'USER'" to="/user">Moje wnioski</NuxtLink>
          <template v-else>
            <NuxtLink to="/manager" active-class="" exact-active-class="router-link-active">
              Wnioski
            </NuxtLink>
            <NuxtLink to="/manager/users">Użytkownicy</NuxtLink>
          </template>
        </nav>
      </div>
      <nav class="app-nav">
        <template v-if="isLoggedIn">
          <span class="app-nav-email">{{ user?.email }} ({{ user?.role }})</span>
          <LoadingButton variant="outline" @click="handleLogout">Wyloguj</LoadingButton>
        </template>
        <template v-else>
          <NuxtLink to="/login">Zaloguj</NuxtLink>
          <NuxtLink to="/register">Zarejestruj</NuxtLink>
        </template>
      </nav>
    </header>
    <ToastContainer />
    <slot />
  </div>
</template>
