<script setup>
import { ref, onMounted } from 'vue'
import { useTelegram } from './composables/useTelegram.js'

// Lucide Vue Icons
import { 
  Users, 
  Send, 
  Clock, 
  Database,
  ChevronRight,
  Sparkles,
  ShieldCheck,
  AppWindow,
  FileBadge
} from '@lucide/vue'

// Mock initial data
import { initialUsers, initialBroadcasts } from './mockData.js'

// Import components
import DashboardStats from './components/DashboardStats.vue'
import UserList from './components/UserList.vue'
import UserProfileModal from './components/UserProfileModal.vue'
import AddUserModal from './components/AddUserModal.vue'
import BroadcastConstructor from './components/BroadcastConstructor.vue'

const { initApp, haptic } = useTelegram()

// Tabs navigation: 'users', 'broadcasts'
const currentTab = ref('users')

// Reactive database states
const users = ref([])
const broadcasts = ref([])

// Modals/Drawers toggle states
const selectedUser = ref(null)
const isProfileOpen = ref(false)
const isAddModalOpen = ref(false)

// Toast notification
const showToast = ref(false)
const toastMessage = ref('')

// Live Moscow Time Clock
const currentTime = ref('')
function updateTime() {
  const now = new Date()
  const options = {
    timeZone: 'Europe/Moscow',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }
  currentTime.value = now.toLocaleTimeString('ru-RU', options)
}

onMounted(() => {
  // Initialize Telegram SDK
  initApp()
  
  // Start clock
  updateTime()
  setInterval(updateTime, 1000)

  // Load from localStorage or use mock initial data
  const cachedBroadcasts = localStorage.getItem('pml_admin_broadcasts')

  users.value = []

  if (cachedBroadcasts) {
    broadcasts.value = JSON.parse(cachedBroadcasts)
  } else {
    broadcasts.value = initialBroadcasts
    localStorage.setItem('pml_admin_broadcasts', JSON.stringify(initialBroadcasts))
  }
})

function switchTab(tab) {
  haptic()
  currentTab.value = tab
}

// User Actions
function selectUser(user) {
  haptic()
  selectedUser.value = user
  isProfileOpen.value = true
}

function handleSaveUser(updatedUser) {
  const index = users.value.findIndex(u => u.id === updatedUser.id)
  if (index !== -1) {
    users.value[index] = updatedUser
    localStorage.setItem('pml_admin_users', JSON.stringify(users.value))
  }
}

function handleAddUser(newUser) {
  haptic()
  newUser.id = Date.now()
  users.value.unshift(newUser)
  localStorage.setItem('pml_admin_users', JSON.stringify(users.value))
  triggerToast(`Пользователь ${newUser.full_name} успешно добавлен в базу!`)
}

// Broadcast Actions
function handleAddBroadcast(newLog) {
  haptic()
  broadcasts.value.unshift(newLog)
  localStorage.setItem('pml_admin_broadcasts', JSON.stringify(broadcasts.value))
}

function handleDeleteBroadcast(id) {
  haptic()
  broadcasts.value = broadcasts.value.filter(b => b.id !== id)
  localStorage.setItem('pml_admin_broadcasts', JSON.stringify(broadcasts.value))
  triggerToast(`Рассылка ${id} удалена из системы!`)
}

function triggerToast(msg) {
  toastMessage.value = msg
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}
</script>

<template>
  <div class="flex h-screen w-full bg-[#0c141f] text-[#dce2f3] overflow-hidden font-sans select-none">
    
    <!-- Sidebar Navigation - Desktop view -->
    <aside class="hidden md:flex flex-col w-72 bg-[#090e15] border-r border-white/5 flex-shrink-0 z-20">
      
      <!-- Core logotype & Brand identifier -->
      <div class="p-lg border-b border-white/5 space-y-2">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-secondary flex items-center justify-center font-black text-on-primary-fixed select-none text-sm shadow-md shadow-primary/20">
            П
          </div>
          <div>
            <h1 class="font-bold text-sm tracking-wide text-on-surface uppercase pr-1">
              Психология Масштаба
            </h1>
            <span class="text-[10px] font-bold text-primary tracking-widest block uppercase">
              Админ-Консоль PML
            </span>
          </div>
        </div>
        
        <div class="flex items-center gap-1.5 pt-1">
          <span class="inline-flex w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
          <span class="text-[10px] text-on-surface-variant font-mono font-bold uppercase tracking-wider">
            Сервер: Активен (Port 3000)
          </span>
        </div>
      </div>

      <!-- Tab links section -->
      <nav class="p-md flex-1 space-y-1.5 overflow-y-auto">
        <button
          @click="switchTab('users')"
          :class="[
            'w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all cursor-pointer border border-transparent',
            currentTab === 'users'
              ? 'bg-primary-container text-on-primary-container font-semibold shadow-sm border-primary/20'
              : 'text-on-surface-variant hover:bg-white/5 hover:text-on-surface'
          ]"
        >
          <div class="flex items-center gap-3">
            <Users :size="18" :class="currentTab === 'users' ? 'text-primary' : 'text-on-surface-variant'" />
            <span class="text-sm font-semibold">Пользователи бота</span>
          </div>
          <span class="text-[10px] font-semibold font-mono bg-white/5 px-2 py-0.5 rounded-full text-on-surface-variant">
            {{ users.length }}
          </span>
        </button>

        <button
          @click="switchTab('broadcasts')"
          :class="[
            'w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all cursor-pointer border border-transparent',
            currentTab === 'broadcasts'
              ? 'bg-primary-container text-on-primary-container font-semibold shadow-sm border-primary/20'
              : 'text-on-surface-variant hover:bg-white/5 hover:text-on-surface'
          ]"
        >
          <div class="flex items-center gap-3">
            <Send :size="18" :class="currentTab === 'broadcasts' ? 'text-primary' : 'text-on-surface-variant'" />
            <span class="text-sm font-semibold">Конструктор рассылок</span>
          </div>
          <span class="text-[10px] font-semibold font-mono bg-white/5 px-2 py-0.5 rounded-full text-on-surface-variant">
            {{ broadcasts.length }}
          </span>
        </button>
      </nav>

      <!-- Sidebar Footer admin summary info -->
      <div class="p-lg border-t border-white/5 space-y-3 bg-white/2">
        <div class="flex gap-2">
          <div class="flex-grow p-2 rounded bg-surface-container-low text-center border border-white/5">
            <span class="text-[9px] text-on-surface-variant block uppercase font-bold tracking-wider">БД статус</span>
            <span class="text-xs font-bold text-secondary flex items-center justify-center gap-1 mt-0.5 font-mono">
              <Database :size="10" /> Sync (OK)
            </span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content Workspace viewport -->
    <div class="flex-grow flex flex-col min-w-0 bg-[#0c141f] overflow-hidden">
      
      <!-- Dynamic header row metadata -->
      <header class="h-16 border-b border-white/5 bg-[#090e15]/40 backdrop-blur-xl flex items-center justify-between px-4 md:px-6 z-10 flex-shrink-0">
        
        <!-- Mobile responsive navigation -->
        <div class="flex items-center justify-between w-full md:hidden">
          <div class="w-7 h-7 rounded bg-gradient-to-tr from-primary to-secondary flex items-center justify-center font-black text-on-primary-fixed text-xs select-none shadow">
            П
          </div>
          <div class="flex bg-surface-container border border-white/5 p-1 rounded-xl">
            <button
              @click="switchTab('users')"
              :class="[
                'py-1.5 px-3 rounded-lg text-xs font-semibold transition-all cursor-pointer',
                currentTab === 'users' ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant'
              ]"
            >
              Пользователи
            </button>
            <button
              @click="switchTab('broadcasts')"
              :class="[
                'py-1.5 px-3 rounded-lg text-xs font-semibold transition-all cursor-pointer',
                currentTab === 'broadcasts' ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant'
              ]"
            >
              Рассылки
            </button>
          </div>
        </div>

        <div class="hidden md:flex items-center gap-2 font-mono text-[11px] text-on-surface-variant">
          <span class="bg-surface-container-highest text-[#65bdff]/90 px-2 py-0.5 rounded font-bold uppercase border border-white/5">
            dev-preview
          </span>
          <span class="text-on-surface-variant/40">|</span>
          <span class="flex items-center gap-1 select-all cursor-pointer">
            <span class="material-symbols-outlined text-[14px]">link</span>
            pml-bot-production
          </span>
        </div>

        <!-- Moscow time real clock widget -->
        <div class="hidden md:flex items-center gap-3">
          <div class="bg-primary/5 border border-primary/20 px-3.5 py-1.5 rounded-xl flex items-center gap-2 font-mono text-xs text-primary shadow-inner">
            <Clock :size="13" class="text-primary" />
            <span>МСК (GMT+3):</span>
            <strong class="tracking-widest tabular-nums">{{ currentTime || "00:00:00" }}</strong>
          </div>
        </div>
      </header>

      <!-- Scrollable primary card viewport body -->
      <main class="flex-1 overflow-y-auto px-4 md:px-6 py-4 md:py-6 pb-24 md:pb-6 custom-scrollbar">
        <Transition name="fade" mode="out-in">
          <!-- Tab 1: Users -->
          <div v-if="currentTab === 'users'" class="space-y-lg">
            <!-- Inline Detailed Profile View (like html-screen-builder) -->
            <div v-if="selectedUser && isProfileOpen" class="space-y-lg">
              <UserProfileModal 
                :user="selectedUser"
                @close="isProfileOpen = false; selectedUser = null"
                @saveUser="handleSaveUser"
              />
            </div>
            <div v-else class="space-y-lg">
              <DashboardStats :users="users" />
              <UserList 
                @usersLoaded="users = $event"
                @selectUser="selectUser"
                @openAddModal="isAddModalOpen = true"
              />
            </div>
          </div>

          <!-- Tab 2: Broadcasts -->
          <div v-else class="space-y-lg">
            <BroadcastConstructor 
              :users="users" 
              :broadcasts="broadcasts"
              @addBroadcast="handleAddBroadcast" 
              @deleteBroadcast="handleDeleteBroadcast"
            />
          </div>
        </Transition>
      </main>
    </div>

    <!-- Bottom Navigation Bar - Mobile view only (backup accessibility) -->
    <nav class="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-[#0a1019]/95 backdrop-blur-md border-t border-white/5 p-2 flex justify-around select-none">
      <button 
        @click="switchTab('users')"
        :class="[
          'flex flex-col items-center gap-1 px-3 py-1.5 rounded-lg transition-all duration-150',
          currentTab === 'users' ? 'text-primary font-bold' : 'text-[#8a9db9]'
        ]"
      >
        <Users :size="16" />
        <span class="text-[9px] uppercase tracking-wider font-semibold">Пользователи</span>
      </button>

      <button 
        @click="switchTab('broadcasts')"
        :class="[
          'flex flex-col items-center gap-1 px-3 py-1.5 rounded-lg transition-all duration-150',
          currentTab === 'broadcasts' ? 'text-primary font-bold' : 'text-[#8a9db9]'
        ]"
      >
        <Send :size="16" />
        <span class="text-[9px] uppercase tracking-wider font-semibold">Рассылки</span>
      </button>
    </nav>

    <!-- Drawers & Modals Overlay layer -->
    <AddUserModal 
      :isOpen="isAddModalOpen"
      @close="isAddModalOpen = false"
      @addUser="handleAddUser"
    />

    <!-- Toast Notification -->
    <Transition name="fade">
      <div 
        v-if="showToast"
        class="fixed bottom-18 md:bottom-6 left-1/2 -translate-x-1/2 z-50 bg-[#121d2d] border border-primary/30 text-[#dce2f3] px-6 py-3 rounded-xl shadow-2xl text-xs font-semibold select-none flex items-center gap-3 glass-card"
      >
        <div class="w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center">
          <Sparkles :size="12" />
        </div>
        {{ toastMessage }}
      </div>
    </Transition>

  </div>
</template>

<style>
.fade-enter-active, .fade-leave-active {
  transition: opacity 200ms ease, transform 200ms ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(5px);
}
</style>
