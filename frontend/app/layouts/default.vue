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
      <span style="font-weight: 600">Euro Park</span>
      <nav class="app-nav">
        <template v-if="isLoggedIn">
          <NuxtLink v-if="user?.role === 'USER'" to="/applications"
            >Moje wnioski</NuxtLink
          >
          <NuxtLink v-else to="/manager">Panel zarządcy</NuxtLink>
          <span class="app-nav-email">{{ user?.email }}</span>
          <button class="btn btn--outline" type="button" @click="handleLogout">
            Wyloguj
          </button>
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
