<script setup lang="ts">
import type { SelectOption } from '~/types/form'
import type { AuthUser, UserPage } from '~/types/user'

definePageMeta({ layout: 'manager', middleware: ['auth', 'manager'] })

const PAGE_SIZE = 10

const { user } = useAuth()
const { api } = useApiClient()

const page = ref(1)

const {
  data: usersPage,
  pending: usersPending,
  refresh: refreshUsers,
} = useAsyncData<UserPage>(
  'manager-users',
  () => api('/manager/users', { query: { page: page.value, size: PAGE_SIZE } }),
  { watch: [page] },
)

const allUsers = computed<AuthUser[]>(() => usersPage.value?.items ?? [])

const isAdmin = computed(() => user.value?.role === 'ADMIN')

const ROLE_OPTIONS: SelectOption[] = [
  { value: 'USER', label: 'USER' },
  { value: 'MANAGER', label: 'MANAGER' },
  { value: 'ADMIN', label: 'ADMIN' },
]

const { target: showUserForm, open: openCreateUserRaw, close: closeCreateUser } = useDisclosure()
const newUserEmail = ref('')
const newUserPassword = ref('')
const newUserRole = ref('USER')

function openCreateUser() {
  newUserEmail.value = ''
  newUserPassword.value = ''
  newUserRole.value = 'USER'
  openCreateUserRaw()
}

const { loading: userFormLoading, submit: submitCreateUserAction } = useModalForm(async () => {
  closeCreateUser()
  await refreshUsers()
})

function submitCreateUser() {
  return submitCreateUserAction(
    () =>
      api('/manager/users', {
        method: 'POST',
        body: {
          email: newUserEmail.value,
          password: newUserPassword.value,
          role: newUserRole.value,
        },
      }),
    201,
  )
}

const { target: editUserTarget, open: openEditUserRaw, close: closeEditUser } = useDisclosure<AuthUser>()
const editUserRole = ref('USER')

function openEditUser(target: AuthUser) {
  editUserRole.value = target.role
  openEditUserRaw(target)
}

const { loading: editUserLoading, submit: submitEditUserAction } = useModalForm(async () => {
  closeEditUser()
  await refreshUsers()
})

function submitEditUser() {
  if (!editUserTarget.value) return
  return submitEditUserAction(() =>
    api(`/manager/users/${editUserTarget.value!.id}/role`, {
      method: 'PATCH',
      body: { role: editUserRole.value },
    }),
  )
}

const {
  target: deleteConfirmTarget,
  open: openDeleteUser,
  close: closeDeleteUser,
} = useDisclosure<AuthUser>()

const { loading: deleteUserLoading, submit: confirmDeleteUserAction } = useModalForm(async () => {
  closeDeleteUser()
  await refreshUsers()
})

function confirmDeleteUser() {
  if (!deleteConfirmTarget.value) return
  return confirmDeleteUserAction(() =>
    api(`/manager/users/${deleteConfirmTarget.value!.id}`, { method: 'DELETE' }),
  )
}
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <div>
        <h2>Użytkownicy</h2>
        <p class="panel-subtitle">
          <span v-if="usersPending" class="sk sk-subtitle" />
          <template v-else>{{ usersPage?.total ?? 0 }} użytkowników</template>
        </p>
      </div>
      <LoadingButton v-if="isAdmin" @click="openCreateUser">Dodaj użytkownika</LoadingButton>
    </div>

    <AppModal v-if="showUserForm" title="Nowy użytkownik" @close="closeCreateUser">
      <FormInput
        id="newUserEmail"
        v-model="newUserEmail"
        label="Email"
        type="email"
        placeholder="np. jan.kowalski@eurocert.com"
      />
      <FormInput
        id="newUserPassword"
        v-model="newUserPassword"
        label="Hasło"
        type="password"
        placeholder="Min. 4 znaki"
      />
      <FormSelect id="newUserRole" v-model="newUserRole" label="Rola" :options="ROLE_OPTIONS" />
      <div class="form-actions">
        <LoadingButton :loading="userFormLoading" @click="submitCreateUser">
          Utwórz
        </LoadingButton>
        <LoadingButton variant="outline" :disabled="userFormLoading" @click="closeCreateUser">
          Anuluj
        </LoadingButton>
      </div>
    </AppModal>

    <AppModal v-if="editUserTarget" title="Edytuj użytkownika" @close="closeEditUser">
      <p class="modal-subtitle">{{ editUserTarget.email }}</p>
      <FormSelect id="editUserRole" v-model="editUserRole" label="Rola" :options="ROLE_OPTIONS" />
      <div class="form-actions">
        <LoadingButton :loading="editUserLoading" @click="submitEditUser">Zapisz</LoadingButton>
        <LoadingButton variant="outline" :disabled="editUserLoading" @click="closeEditUser">
          Anuluj
        </LoadingButton>
      </div>
    </AppModal>

    <AppModal v-if="deleteConfirmTarget" title="Usuń użytkownika" @close="closeDeleteUser">
      <p class="modal-subtitle">Na pewno usunąć {{ deleteConfirmTarget.email }}?</p>
      <div class="form-actions">
        <LoadingButton
          variant="destructive"
          :loading="deleteUserLoading"
          @click="confirmDeleteUser"
        >
          Usuń
        </LoadingButton>
        <LoadingButton variant="outline" :disabled="deleteUserLoading" @click="closeDeleteUser">
          Anuluj
        </LoadingButton>
      </div>
    </AppModal>

    <div class="app-card table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Email</th>
            <th>Rola</th>
            <th v-if="isAdmin" class="actions-col">Akcje</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="usersPending">
            <tr v-for="n in PAGE_SIZE" :key="`sk-${n}`">
              <td><span class="sk" style="width: 30px; height: 12px" /></td>
              <td><span class="sk" style="width: 160px; height: 12px" /></td>
              <td><span class="sk" style="width: 70px; height: 12px" /></td>
              <td v-if="isAdmin" class="actions-col">
                <span class="sk" style="width: 60px; height: 21px; border-radius: 6px" />
              </td>
            </tr>
          </template>

          <template v-else-if="!allUsers.length">
            <tr>
              <td :colspan="isAdmin ? 4 : 3" class="empty-row">Brak użytkowników.</td>
            </tr>
            <tr
              v-for="n in PAGE_SIZE - 1"
              :key="`filler-${n}`"
              class="filler-row"
              aria-hidden="true"
            >
              <td :colspan="isAdmin ? 4 : 3">&nbsp;</td>
            </tr>
          </template>

          <template v-else>
            <template v-for="u in allUsers" :key="u.id">
              <tr>
                <td>#{{ u.id }}</td>
                <td>{{ u.email }}</td>
                <td>{{ u.role }}</td>
                <td v-if="isAdmin" class="actions-col">
                  <span v-if="u.id === user?.id" class="no-actions">To Ty</span>
                  <div v-else class="row-actions">
                    <IconButton
                      variant="neutral"
                      label="Edytuj użytkownika"
                      @click="openEditUser(u)"
                    >
                      <AppIcon name="pencil" />
                    </IconButton>
                    <IconButton
                      variant="destructive"
                      label="Usuń użytkownika"
                      @click="openDeleteUser(u)"
                    >
                      <AppIcon name="trash" />
                    </IconButton>
                  </div>
                </td>
              </tr>
            </template>
            <tr
              v-for="n in Math.max(0, PAGE_SIZE - allUsers.length)"
              :key="`filler-${n}`"
              class="filler-row"
              aria-hidden="true"
            >
              <td :colspan="isAdmin ? 4 : 3">&nbsp;</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div class="pagination-slot">
      <AppPagination
        v-model:page="page"
        :size="PAGE_SIZE"
        :total="usersPage?.total ?? 0"
        :loading="usersPending"
      />
    </div>
  </section>
</template>

