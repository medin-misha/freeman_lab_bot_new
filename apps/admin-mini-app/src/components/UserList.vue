<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, UserPlus, ChevronRight, ChevronLeft } from '@lucide/vue'
import { fetchUsers } from '../services/api.js'

const emit = defineEmits(['selectUser', 'openAddModal', 'usersLoaded'])

const searchQuery = ref('')
const selectedSegment = ref('Все') // 'Все', 'В ядре', 'Не в ядре'
const currentPage = ref(1)
const itemsPerPage = 8

const usersList = ref([])
const loading = ref(false)
const hasNext = ref(false)

// Клиентская сегментация загруженного списка для совместимости с фильтром сегментов
const displayedUsers = computed(() => {
  return usersList.value.filter(user => {
    if (selectedSegment.value === 'В ядре' && !user.in_core) return false
    if (selectedSegment.value === 'Не в ядре' && user.in_core) return false
    return true
  })
})

async function loadUsers() {
  loading.value = true
  try {
    const result = await fetchUsers({
      page: currentPage.value,
      limit: itemsPerPage,
      search: searchQuery.value
    })
    usersList.value = result.users
    hasNext.value = result.hasNext
    emit('usersLoaded', result.users)
  } catch (error) {
    console.error('Не удалось загрузить пользователей:', error)
  } finally {
    loading.value = false
  }
}

// Дебаунс для поиска, чтобы избежать лишней нагрузки на бэкенд
let debounceTimeout = null
function handleSearchInput() {
  currentPage.value = 1
  if (debounceTimeout) clearTimeout(debounceTimeout)
  debounceTimeout = setTimeout(() => {
    loadUsers()
  }, 400)
}

function selectSegment(segment) {
  selectedSegment.value = segment
}

function handlePageChange(page) {
  if (page >= 1) {
    currentPage.value = page
    loadUsers()
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<template>
  <div class="space-y-lg">
    <!-- Header with Action -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-md">
      <div>
        <h2 class="text-3xl font-bold tracking-tight text-[#dce2f3] flex items-center gap-2 select-none">
          Управление пользователями
        </h2>
        <p class="text-sm text-on-surface-variant mt-1 select-none">
          Мониторинг активности, сегментация аудитории и детальный анализ психологических диагностик ПМЛ.
        </p>
      </div>
      <button 
        @click="emit('openAddModal')"
        class="bg-primary text-on-primary-fixed hover:bg-opacity-95 px-6 py-2.5 rounded-full font-semibold flex items-center gap-2 shadow-lg shadow-primary/15 self-start md:self-auto cursor-pointer transition-all hover:scale-[1.02] active:scale-[0.98]"
      >
        <UserPlus :size="18" />
        Добавить вручную
      </button>
    </div>

    <!-- Search and Filters bar -->
    <div class="grid grid-cols-1 md:grid-cols-12 gap-md">
      <!-- Search Input -->
      <div class="md:col-span-7 relative">
        <span class="absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant select-none pointer-events-none">
          <Search :size="18" />
        </span>
        <input 
          v-model="searchQuery"
          @input="handleSearchInput"
          type="text"
          placeholder="Поиск по username, имени..."
          class="w-full bg-surface-container border border-white/10 rounded-xl py-3 pl-12 pr-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all font-sans text-on-surface placeholder:text-on-surface-variant/40 text-sm"
        />
        <button 
          v-if="searchQuery" 
          @click="searchQuery = ''; loadUsers()"
          class="absolute inset-y-0 right-4 flex items-center text-on-surface-variant hover:text-white transition-colors cursor-pointer"
        >
          <span class="material-symbols-outlined text-sm font-semibold select-none">close</span>
        </button>
      </div>

      <!-- Segment Tabs -->
      <div class="md:col-span-5 flex p-1 bg-surface-container rounded-xl gap-1 border border-white/5 overflow-hidden">
        <button 
          v-for="segment in ['Все', 'В ядре', 'Не в ядре']" 
          :key="segment"
          @click="selectSegment(segment)"
          :class="[
            'flex-1 py-2 px-1 rounded-lg text-center font-semibold text-[11px] lg:text-[12px] transition-all cursor-pointer select-none',
            selectedSegment === segment 
              ? 'bg-primary-container text-on-primary-container shadow-sm font-semibold' 
              : 'text-on-surface-variant hover:bg-surface-container-highest hover:text-on-surface'
          ]"
        >
          {{ segment }}
        </button>
      </div>
    </div>

    <!-- Users Table Container -->
    <div class="bg-surface-container rounded-3xl border border-white/5 overflow-hidden shadow-2xl">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-white/5 bg-white/2 select-none">
              <th class="px-6 py-4 font-semibold text-on-surface-variant text-[11px] uppercase tracking-wider">Username / ID</th>
              <th class="px-6 py-4 font-semibold text-on-surface-variant text-[11px] uppercase tracking-wider">Полное имя</th>
              <th class="px-6 py-4 font-semibold text-on-surface-variant text-[11px] uppercase tracking-wider">Статус</th>
              <th class="px-6 py-4 font-semibold text-on-surface-variant text-[11px] uppercase tracking-wider">Последний вход</th>
              <th class="px-6 py-4 font-semibold text-on-surface-variant text-[11px] uppercase tracking-wider">Активность в боте</th>
              <th class="px-6 py-4"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5 text-sm text-[#dce2f3] relative">
            <!-- Loading Indicator -->
            <tr v-if="loading">
              <td colspan="6" class="px-6 py-16 text-center">
                <div class="flex flex-col items-center justify-center gap-3">
                  <div class="w-8 h-8 rounded-full border-2 border-primary/20 border-t-primary animate-spin"></div>
                  <span class="text-xs text-on-surface-variant font-medium animate-pulse font-mono uppercase tracking-wider">Загрузка данных...</span>
                </div>
              </td>
            </tr>

            <template v-else>
              <tr 
                v-for="user in displayedUsers" 
                :key="user.id"
                @click="emit('selectUser', user)"
                class="hover:bg-white/5 transition-all group cursor-pointer duration-150 relative"
              >
                <!-- Username & ID -->
                <td class="px-6 py-5">
                  <div class="flex flex-col">
                    <span class="font-semibold text-primary group-hover:text-amber-200 transition-colors">
                      @{{ user.username || 'id' + user.telegram_id }}
                    </span>
                    <span class="text-[11px] text-on-surface-variant font-mono">
                      {{ user.telegram_id || user.id }}
                    </span>
                  </div>
                </td>

                <!-- Full Name -->
                <td class="px-6 py-5 font-semibold text-on-surface">
                  {{ user.full_name }}
                </td>

                <!-- Status Badge -->
                <td class="px-6 py-5">
                  <span 
                    :class="[
                      'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border',
                      user.in_core 
                        ? 'bg-secondary/10 text-secondary border-secondary/20' 
                        : 'bg-on-surface-variant/10 text-on-surface-variant border-on-surface-variant/20'
                    ]"
                  >
                    {{ user.in_core ? 'В ядре' : 'Не в ядре' }}
                  </span>
                </td>

                <!-- Last Active -->
                <td class="px-6 py-5 text-on-surface-variant/80 text-xs font-mono">
                  {{ user.last_active }}
                </td>

                <!-- Bot Activity Step -->
                <td class="px-6 py-5">
                  <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container-highest text-xs">
                    <span 
                      :class="[
                        'w-1.5 h-1.5 rounded-full',
                        user.step_status === 'Готово' || user.step_status === 'Получена' ? 'bg-secondary' :
                        user.step_status === 'В процессе' ? 'bg-amber-400 animate-pulse' : 'bg-on-surface-variant'
                      ]"
                    ></span>
                    {{ user.current_step }}
                  </span>
                </td>

                <!-- Actions Arrow Button -->
                <td class="px-6 py-5 text-right">
                  <button 
                    class="text-on-surface-variant hover:text-primary transition-colors p-1 rounded-lg hover:bg-white/5 group-hover:scale-110 duration-150"
                  >
                    <ChevronRight :size="18" />
                  </button>
                </td>
              </tr>

              <!-- Empty State -->
              <tr v-if="displayedUsers.length === 0">
                <td colspan="6" class="px-6 py-12 text-center text-on-surface-variant/60">
                  Пользователи не найдены. Попробуйте изменить параметры поиска или фильтров.
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <!-- Pagination bar -->
      <div class="px-6 py-4 border-t border-white/5 flex items-center justify-between bg-white/2">
        <span class="text-xs text-on-surface-variant font-mono">
          Страница {{ currentPage }} {{ loading ? '(Загрузка...)' : '' }}
        </span>
        <div class="flex items-center gap-2 select-none">
          <button 
            @click="handlePageChange(currentPage - 1)"
            :disabled="currentPage === 1 || loading"
            class="px-4 py-2 rounded-xl bg-white/2 hover:bg-white/5 text-on-surface-variant disabled:opacity-20 disabled:cursor-not-allowed transition-all cursor-pointer flex items-center gap-1.5 text-xs font-bold border border-white/5"
          >
            <ChevronLeft :size="14" />
            Назад
          </button>
          
          <button 
            @click="handlePageChange(currentPage + 1)"
            :disabled="!hasNext || loading"
            class="px-4 py-2 rounded-xl bg-white/2 hover:bg-white/5 text-on-surface-variant disabled:opacity-20 disabled:cursor-not-allowed transition-all cursor-pointer flex items-center gap-1.5 text-xs font-bold border border-white/5"
          >
            Вперед
            <ChevronRight :size="14" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
