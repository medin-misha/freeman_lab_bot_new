<script setup>
import { ref, computed, watch } from 'vue'
import { 
  Send, 
  Eye, 
  HelpCircle, 
  Sparkles, 
  Upload, 
  FileText, 
  X, 
  Bold, 
  Italic, 
  Link2, 
  CheckCircle,
  FileCheck2,
  Clock, 
  Trash2,
  ChevronDown
} from '@lucide/vue'

const props = defineProps({
  users: {
    type: Array,
    required: true
  },
  broadcasts: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['addBroadcast', 'deleteBroadcast'])

// Tabs logic
const activeTab = ref('composer')

// Targeting filters
const selectedSegment = ref('Все')
const selectedDiagnostic = ref('Все диагностики')
const bookletFilter = ref(false)
const userIdFilter = ref('')

// Message editor states
const msgText = ref('Приветствую! Мы обновили нашу главную методичку по психологии масштаба.\nСкачать ее вы можете, нажав на кнопку ниже.\nЖелаем продуктивного дня!')
const attachedFile = ref(null) // Mock uploaded file { name, size }
const isUploading = ref(false)
const uploadProgress = ref(0)

// Stats simulation
const lastSentTime = ref('Сегодня, 10:20')
const scheduledCount = ref(3)

// Notification states
const toastMessage = ref('')
const showToast = ref(false)

// Dynamic Reach Counter
const reachCount = computed(() => {
  let base = 12482
  if (selectedSegment.value === 'В ядре') {
    base = 428
  } else if (selectedSegment.value === 'Не в ядре') {
    base = 12054
  }

  // Multiply by diagnostic choice
  if (selectedDiagnostic.value !== 'Все диагностики') {
    base = Math.floor(base * 0.35)
  }

  // Interconnect booklet filter
  if (bookletFilter.value) {
    base = Math.floor(base * 0.72)
  }

  // Interconnect chat search ID
  if (userIdFilter.value.trim().length > 0) {
    base = 1
  }

  return Math.max(1, base)
})

// Text Helper for toolbars
function insertTextHelper(before, after = '') {
  const textarea = document.getElementById('broadcast-text')
  if (!textarea) return
  
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = textarea.value
  const selected = text.substring(start, end)
  const replacement = before + (selected || "текст") + after
  
  msgText.value = text.substring(0, start) + replacement + text.substring(end)
  
  // Focus back
  setTimeout(() => {
    textarea.focus()
    textarea.setSelectionRange(start + before.length, start + before.length + (selected || "текст").length)
  }, 100)
}

// Media upload emulation
function handleFileSelect(e) {
  if (e.target.files && e.target.files[0]) {
    simulateUpload(e.target.files[0].name)
  }
}

function handleFileDrop(e) {
  e.preventDefault()
  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
    simulateUpload(e.dataTransfer.files[0].name)
  }
}

function simulateUpload(fileName) {
  isUploading.value = true
  uploadProgress.value = 10
  const interval = setInterval(() => {
    if (uploadProgress.value >= 100) {
      clearInterval(interval)
      isUploading.value = false
      attachedFile.value = { name: fileName, size: "3.2 MB" }
      triggerToast('Медиа-файл загружен в ПМЛ хранилище!')
    } else {
      uploadProgress.value += 30
    }
  }, 200)
}

function triggerToast(msg) {
  toastMessage.value = msg
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 4000)
}

// Send broadcast action
function handleSendMessage(statusType) {
  if (!msgText.value.trim()) {
    triggerToast('Сначала напишите текст рассылки!')
    return
  }

  const immediate = statusType === 'sent'
  const newBroadcast = {
    id: "BC-" + Math.floor(100 + Math.random() * 900),
    text: msgText.value,
    segment: selectedSegment.value,
    diagnosticFilter: selectedDiagnostic.value,
    bookletOnly: bookletFilter.value,
    sentDate: immediate ? 'Только что' : 'Завтра, 12:00',
    status: statusType === 'sent' ? 'sent' : 'scheduled',
    reach: reachCount.value,
    targeting: {
      segment: selectedSegment.value,
      diagnostics: selectedDiagnostic.value,
      only_with_methodology: bookletFilter.value
    }
  }

  emit('addBroadcast', newBroadcast)
  
  if (immediate) {
    const now = new Date()
    const options = { hour: '2-digit', minute: '2-digit' }
    lastSentTime.value = 'Сегодня, ' + now.toLocaleTimeString('ru-RU', options)
    triggerToast('Рассылка успешно запущена в Telegram-боте PML!')
  } else {
    scheduledCount.value += 1
    triggerToast('Рассылка запланирована на отправку!')
  }

  // Reset composer form
  msgText.value = ''
  attachedFile.value = null
}

function handleDelete(id, status) {
  emit('deleteBroadcast', id)
  if (status === 'scheduled' || status === 'Запланировано') {
    scheduledCount.value = Math.max(0, scheduledCount.value - 1)
  }
}
</script>

<template>
  <div class="space-y-lg relative">
    
    <!-- Toast Notification Banner -->
    <Transition name="toast">
      <div 
        v-if="showToast"
        class="fixed top-20 right-4 left-4 md:left-auto md:right-6 z-50 bg-[#151c27] border-l-4 border-secondary px-6 py-4 rounded-xl shadow-xl flex items-center gap-3 border border-white/5"
      >
        <div class="w-8 h-8 rounded-full bg-secondary/15 flex items-center justify-center text-secondary">
          <CheckCircle :size="16" />
        </div>
        <div>
          <p class="text-sm font-semibold text-on-surface">{{ toastMessage }}</p>
          <p class="text-[11px] text-on-surface-variant">Все API процессы бота PML синхронизированы</p>
        </div>
      </div>
    </Transition>

    <!-- Header Section -->
    <section class="select-none">
      <h2 class="text-3xl font-bold tracking-tight text-primary flex items-center gap-2">
        Конструктор рассылок (Письма & TG Пуши)
      </h2>
      <p class="text-sm text-on-surface-variant mt-1.5 max-w-3xl leading-relaxed">
        Создавайте и отправляйте мгновенные или запланированные сообщения вашей аудитории. Используйте умные фильтры ПМЛ для точечного таргетинга респондентов.
      </p>
    </section>

    <!-- Tabs Navigation Bar -->
    <div class="flex border-b border-white/5 gap-4 select-none">
      <button
        @click="activeTab = 'composer'"
        :class="[
          'pb-2.5 text-sm transition-all relative cursor-pointer',
          activeTab === 'composer' ? 'text-primary font-bold' : 'text-on-surface-variant hover:text-on-surface font-semibold'
        ]"
      >
        Новая рассылка
        <div v-if="activeTab === 'composer'" class="absolute bottom-0 left-0 w-full h-[2px] bg-primary" />
      </button>
      <button
        @click="activeTab = 'history'"
        :class="[
          'pb-2.5 text-sm transition-all relative cursor-pointer',
          activeTab === 'history' ? 'text-primary font-bold' : 'text-on-surface-variant hover:text-on-surface font-semibold'
        ]"
      >
        История и Запланировано ({{ broadcasts.length }})
        <div v-if="activeTab === 'history'" class="absolute bottom-0 left-0 w-full h-[2px] bg-primary" />
      </button>
    </div>

    <!-- Active Tab views rendering -->
    <Transition name="fade" mode="out-in">
      
      <!-- Tab 1: Composer -->
      <div v-if="activeTab === 'composer'" class="grid grid-cols-1 lg:grid-cols-12 gap-lg items-start">
        
        <!-- Left Column: Filters & Target Estimation Card -->
        <div class="lg:col-span-5 space-y-lg">
          
          <!-- Reach Number Bento Widget -->
          <div class="glass-card rounded-2xl p-lg relative overflow-hidden group border border-white/5 select-none">
            <div class="absolute -right-4 -top-4 w-24 h-24 bg-primary/10 rounded-full blur-2xl group-hover:bg-primary/20 transition-all duration-700"></div>
            <div class="relative z-10 space-y-2">
              <span class="text-[10px] text-primary uppercase tracking-widest block font-bold">Ожидаемый охват рассылки</span>
              
              <div class="flex items-baseline gap-2">
                <span class="text-4xl font-black text-on-surface tracking-tight" id="reach-count">
                  {{ reachCount.toLocaleString('ru-RU') }}
                </span>
                <span class="text-xs text-on-surface-variant opacity-70">респондентов</span>
              </div>

              <div class="w-full bg-surface-container-highest h-1.5 rounded-full overflow-hidden">
                <div 
                  class="bg-primary h-full shadow-[0_0_15px_rgba(124,58,237,0.4)] transition-all duration-500"
                  :style="{ width: `${Math.min(100, Math.max(5, (reachCount/12482)*100))}%` }"
                />
              </div>
              
              <p class="text-[11px] text-on-surface-variant italic pt-2">
                * На основе активных сессий телеграм-бота за последние 30 дней.
              </p>
            </div>
          </div>

          <!-- Target Parameters filters Form Card -->
          <div class="glass-card rounded-2xl p-lg space-y-md border border-white/5">
            <div class="flex items-center gap-2 mb-2 pb-2 border-b border-white/5 select-none">
              <span class="material-symbols-outlined text-primary text-[22px]" style="font-variation-settings: 'FILL' 1">filter_alt</span>
              <h3 class="font-bold text-headline-sm text-on-surface uppercase tracking-wide text-xs">Параметры таргетинга</h3>
            </div>

            <!-- Segment Selector Tab Group -->
            <div class="space-y-1.5 select-none">
              <label class="text-xs text-on-surface-variant font-semibold">Сегмент ядра респондентов</label>
              <div class="flex p-1 bg-surface-container rounded-xl gap-1 border border-white/5">
                <button
                  v-for="seg in ['В ядре', 'Не в ядре', 'Все']"
                  :key="seg"
                  @click="selectedSegment = seg"
                  :class="[
                    'flex-grow py-2 px-1 rounded-lg text-center text-xs transition-all cursor-pointer font-semibold',
                    selectedSegment === seg
                      ? 'bg-primary-container text-on-primary-container shadow-sm font-semibold'
                      : 'text-on-surface-variant hover:bg-surface-container-highest'
                  ]"
                >
                  {{ seg }}
                </button>
              </div>
            </div>

            <!-- Diagnostics filter -->
            <div class="space-y-1.5 select-none">
              <label class="text-xs text-on-surface-variant font-semibold">Участие в диагностике ПМЛ</label>
              <div class="relative">
                <select
                  v-model="selectedDiagnostic"
                  class="w-full bg-surface-container border border-white/10 rounded-xl px-4 py-3 text-sm text-on-surface focus:ring-1 focus:ring-primary focus:border-transparent outline-none cursor-pointer appearance-none font-semibold"
                >
                  <option>Все диагностики</option>
                  <option>Личностный масштаб v1.2</option>
                  <option>Эмоциональный интеллект</option>
                  <option>Архетипы власти</option>
                </select>
                <ChevronDown :size="16" class="absolute right-4 top-4 text-on-surface-variant pointer-events-none" />
              </div>
            </div>

            <!-- Booklet filter Switch -->
            <div class="flex items-center justify-between p-3.5 rounded-xl bg-surface-container border border-white/5 select-none">
              <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-secondary text-[22px]" style="font-variation-settings: 'FILL' 1">menu_book</span>
                <div>
                  <span class="font-bold text-xs text-on-surface block">Получил методичку ПМЛ</span>
                  <span class="text-[10px] text-on-surface-variant block">Исключить ожидания</span>
                </div>
              </div>
              <button 
                @click="bookletFilter = !bookletFilter"
                :class="[
                  'w-11 h-6 rounded-full relative p-0.5 transition-colors cursor-pointer',
                  bookletFilter ? 'bg-secondary' : 'bg-surface-container-highest'
                ]"
              >
                <div :class="[
                  'w-5 h-5 bg-white rounded-full shadow transition-all',
                  bookletFilter ? 'translate-x-[20px]' : 'translate-x-0'
                ]" />
              </button>
            </div>

            <!-- Chat ID Custom Filter -->
            <div class="space-y-1.5">
              <div class="flex justify-between items-center select-none">
                <label class="text-xs text-on-surface-variant font-semibold">Поиск по chat_id / Telegram ID</label>
                <button 
                  v-if="userIdFilter" 
                  @click="userIdFilter = ''" 
                  class="text-[10px] text-red-400 font-semibold"
                >
                  Сбросить
                </button>
              </div>
              <div class="flex items-center bg-surface-container border border-white/10 rounded-xl px-4 py-3 focus-within:ring-1 focus-within:ring-primary focus-within:border-transparent outline-none transition-all">
                <span class="material-symbols-outlined text-[20px] text-on-surface-variant mr-3 select-none">alternate_email</span>
                <input 
                  v-model="userIdFilter"
                  class="bg-transparent border-none focus:ring-0 text-sm outline-none w-full text-on-surface placeholder:text-on-surface-variant/40" 
                  placeholder="Введите ID пользователя для точечной отладки..." 
                  type="text"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Constructor / Message Editor -->
        <div class="lg:col-span-7 space-y-lg">
          
          <div class="glass-card rounded-2xl p-lg space-y-lg border border-primary/10 shadow-xl shadow-primary/2">
            <div class="flex items-center justify-between pb-2 border-b border-white/5 select-none">
              <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-primary text-[22px]" style="font-variation-settings: 'FILL' 1">edit_note</span>
                <h3 class="font-bold text-headline-sm text-on-surface uppercase tracking-wide text-xs">Конструктор сообщения</h3>
              </div>
              <span class="text-[10px] font-bold text-primary bg-primary/10 px-2.5 py-1 rounded">Markdown Support</span>
            </div>

            <!-- Macro Placeholder details tooltip -->
            <div class="bg-primary/5 p-3 rounded-xl border border-primary/10 flex items-start gap-2.5 select-none">
              <Sparkles :size="16" class="text-primary mt-0.5 flex-shrink-0 animate-pulse" />
              <p class="text-[11px] text-primary leading-snug">
                Вы можете вставлять метатег <strong class="bg-[#151c27] px-1 py-0.5 rounded font-mono text-amber-200">{`{name}`}</strong> в тело письма для автоматического обращения к получателю по его Полному Имени в Telegram (например, <em>«Здравствуйте, Иван!»</em>).
              </p>
            </div>

            <!-- Editor Textarea input field -->
            <div class="space-y-sm">
              <textarea 
                id="broadcast-text"
                v-model="msgText"
                class="w-full h-56 bg-surface-container border border-white/10 rounded-xl p-4 text-sm text-on-surface focus:ring-1 focus:ring-primary outline-none transition-all resize-none placeholder:text-on-surface-variant/20 leading-relaxed font-sans" 
                placeholder="Введите текст вашего сообщения... Поддерживается стандартное форматирование Markdown."
              />
              
              <!-- Textarea editor toolbar widgets -->
              <div class="flex items-center justify-between bg-surface-container-low p-2 rounded-xl border border-white/5 select-none">
                <div class="flex gap-1">
                  <button 
                    @click="insertTextHelper('**', '**')"
                    class="p-1.5 hover:bg-surface-container-highest rounded text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" 
                    title="Жирный"
                  >
                    <Bold :size="15" />
                  </button>
                  <button 
                    @click="insertTextHelper('*', '*')"
                    class="p-1.5 hover:bg-surface-container-highest rounded text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" 
                    title="Курсив"
                  >
                    <Italic :size="15" />
                  </button>
                  <button 
                    @click="insertTextHelper('[Ссылка](', ')')"
                    class="p-1.5 hover:bg-surface-container-highest rounded text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" 
                    title="Вставить ссылку"
                  >
                    <Link2 :size="15" />
                  </button>
                  <button 
                    @click="insertTextHelper('🔥')"
                    class="p-1.5 hover:bg-surface-container-highest rounded text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer text-xs" 
                    title="Эмодзи огонь"
                  >
                    🔥
                  </button>
                  <button 
                    @click="insertTextHelper('📌')"
                    class="p-1.5 hover:bg-surface-container-highest rounded text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer text-xs" 
                    title="Эмодзи пин"
                  >
                    📌
                  </button>
                  <button 
                    @click="insertTextHelper('Здравствуйте, {name}!')"
                    class="p-1 hover:bg-primary/10 rounded text-xs text-primary font-bold px-2 transition-colors cursor-pointer" 
                    title="Добавить тег обращения по имени"
                  >
                    {`+ {name}`}
                  </button>
                </div>

                <div class="text-[10px] text-on-surface-variant font-mono pr-2 font-semibold">
                  Символов: <span :class="msgText.length > 500 ? 'text-amber-200' : 'text-primary'">{{ msgText.length }}</span>
                </div>
              </div>
            </div>

            <!-- Drag & Drop Attachment area -->
            <div 
              @dragover.prevent
              @drop="handleFileDrop"
              class="border-2 border-dashed border-white/10 rounded-2xl p-6 flex flex-col items-center justify-center space-y-2 hover:border-primary/40 hover:bg-primary/2 transition-all cursor-pointer group relative overflow-hidden"
            >
              <input 
                type="file" 
                id="broadcast-attachments"
                class="absolute inset-0 opacity-0 cursor-pointer"
                @change="handleFileSelect"
              />
              
              <div v-if="isUploading" class="w-full text-center space-y-md py-2 select-none">
                 <Clock class="mx-auto text-primary animate-spin" :size="24" />
                 <div class="text-xs text-on-surface font-semibold">Загрузка вложения в ПМЛ хранилище {{ uploadProgress }}%</div>
                 <div class="w-48 mx-auto bg-surface-container h-1 rounded-full overflow-hidden">
                   <div class="bg-primary h-full transition-all" :style="{ width: `${uploadProgress}%` }" />
                 </div>
              </div>
              <div v-else-if="attachedFile" class="flex items-center justify-between w-full bg-surface-container/60 p-3 rounded-xl border border-white/5 relative z-10 select-none">
                <div class="flex items-center gap-3">
                  <div class="p-2 rounded-lg bg-primary/10 text-primary">
                    <FileText :size="18" />
                  </div>
                  <div class="text-left font-sans">
                    <p class="text-xs font-semibold text-on-surface">{{ attachedFile.name }}</p>
                    <p class="text-[10px] text-on-surface-variant">{{ attachedFile.size }} • Загружен</p>
                  </div>
                </div>
                <button 
                  @click.prevent="attachedFile = null"
                  class="p-1 px-1.5 rounded-lg hover:bg-red-400/10 text-red-400 text-xs font-semibold transition-colors relative z-20 pointer-events-auto cursor-pointer"
                >
                  Удалить
                </button>
              </div>
              <div v-else class="text-center select-none">
                <div class="w-12 h-12 rounded-full bg-surface-container-highest flex items-center justify-center text-on-surface-variant group-hover:text-primary transition-colors flex-shrink-0 mx-auto mb-2">
                  <Upload :size="22" />
                </div>
                <div class="font-sans">
                  <p class="font-semibold text-xs text-on-surface">Выберите медиа-файл или перетащите его сюда</p>
                  <p class="text-[10px] text-on-surface-variant mt-1">PNG, JPG, PDF, MP3 (до 10MB)</p>
                </div>
              </div>
            </div>

            <!-- Markdown instant preview block -->
            <div v-if="msgText.trim().length > 0" class="bg-surface-container-low p-4 rounded-xl border border-white/5 space-y-2 select-none">
              <span class="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">Визуальный Предпросмотр</span>
              <div class="text-xs text-on-surface-variant leading-relaxed whitespace-pre-wrap italic">
                {{ msgText.replace(/\{name\}/g, 'Александр') }}
              </div>
            </div>

            <!-- Dispatch triggers -->
            <div class="flex flex-col sm:flex-row gap-4 pt-2 select-none">
              <button
                @click="handleSendMessage('sent')"
                class="flex-1 bg-primary text-on-primary-fixed font-semibold py-3 px-5 rounded-xl shadow-lg shadow-primary/15 transition-all text-sm flex items-center justify-center gap-2 cursor-pointer border border-[#c4b3f5] hover:brightness-110 active:scale-95"
              >
                <Send :size="15" />
                Отправить немедленно
              </button>
              <button
                @click="handleSendMessage('scheduled')"
                class="px-6 border border-white/10 bg-surface-container-low text-on-surface py-3 rounded-xl hover:bg-surface-container-highest cursor-pointer font-semibold transition-all active:scale-95 text-xs flex items-center justify-center gap-2"
              >
                <Clock :size="15" />
                Запланировать на завтра
              </button>
            </div>
          </div>

          <!-- Bottom stats row -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-md select-none">
            <div class="glass-card rounded-2xl p-md flex items-center gap-3 border border-white/5">
              <div class="w-10 h-10 rounded-xl bg-secondary/15 flex items-center justify-center text-secondary">
                <CheckCircle :size="18" />
              </div>
              <div>
                <p class="font-semibold text-[10px] text-on-surface-variant uppercase tracking-wider">Последняя успешная</p>
                <p class="font-semibold text-sm text-on-surface">{{ lastSentTime }}</p>
              </div>
            </div>

            <div class="glass-card rounded-2xl p-md flex items-center gap-3 border border-white/5">
              <div class="w-10 h-10 rounded-xl bg-indigo-400/15 flex items-center justify-center text-indigo-300">
                <FileCheck2 :size="18" />
              </div>
              <div>
                <p class="font-semibold text-[10px] text-on-surface-variant uppercase tracking-wider">Очередь вещания</p>
                <p class="font-semibold text-sm text-on-surface">{{ scheduledCount }} рассылки запланированы</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 2: History List -->
      <div v-else class="space-y-md">
        <div class="bg-surface-container rounded-2xl border border-white/5 overflow-hidden">
          <div class="p-4 bg-white/2 border-b border-white/5 font-semibold text-xs uppercase tracking-wider text-on-surface-variant select-none">
            Логи отправленных и запланированных пушей
          </div>
          <div class="divide-y divide-white/5">
            <div 
              v-if="broadcasts.length > 0" 
              v-for="bc in broadcasts" 
              :key="bc.id" 
              class="p-lg hover:bg-white/2 transition-colors flex flex-col md:flex-row md:items-start justify-between gap-md"
            >
              <div class="space-y-2 flex-1 max-w-3xl">
                <div class="flex items-center gap-2 select-none">
                  <span class="font-mono text-xs font-bold text-primary bg-primary/10 px-2 py-0.5 rounded select-all">{{ bc.id }}</span>
                  <span :class="[
                    'text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider',
                    (bc.status === 'sent' || bc.status === 'Отправлено') ? 'bg-secondary/20 text-secondary' : 'bg-indigo-400/20 text-indigo-300'
                  ]">
                    {{ (bc.status === 'sent' || bc.status === 'Отправлено') ? 'Отправлено' : 'Запланировано' }}
                  </span>
                  <span class="text-xs text-on-surface-variant">
                    Охват: <strong>{{ bc.reach?.toLocaleString('ru-RU') || 1 }}</strong> респондентов
                  </span>
                </div>
                <p class="text-xs text-on-surface bg-black/10 p-3 rounded-lg leading-relaxed whitespace-pre-wrap font-sans font-medium">
                  {{ bc.text }}
                </p>
                <div class="flex flex-wrap gap-md text-[11px] text-on-surface-variant font-mono select-none">
                  <span>Сегмент: <strong>{{ bc.segment || bc.targeting?.segment || 'Все' }}</strong></span>
                  <span>Диагностика: <strong>{{ bc.diagnosticFilter || bc.targeting?.diagnostics || 'Все' }}</strong></span>
                  <span>Только с методичкой: <strong>{{ (bc.bookletOnly || bc.targeting?.only_with_methodology) ? 'Да' : 'Нет' }}</strong></span>
                </div>
              </div>

              <div class="flex flex-row md:flex-col items-center md:items-end justify-between md:justify-start gap-md flex-shrink-0 select-none">
                <div class="text-right">
                  <p class="text-[10px] text-on-surface-variant font-semibold uppercase tracking-wider">Дата запуска</p>
                  <p class="text-xs font-mono font-bold text-on-surface mt-0.5">{{ bc.sentDate || bc.time_label }}</p>
                </div>
                <button
                  @click="handleDelete(bc.id, bc.status)"
                  class="px-3 py-1.5 rounded-lg bg-red-400/10 text-red-400 hover:bg-red-400/20 text-xs font-semibold flex items-center gap-1 transition-colors cursor-pointer"
                >
                  <Trash2 :size="12" />
                  Удалить
                </button>
              </div>
            </div>

            <div v-else class="p-12 text-center text-on-surface-variant/60 select-none font-semibold">
              Истории трансляций пока нет. Напишите текст в конструкторе для пилотного пуша.
            </div>
          </div>
        </div>
      </div>

    </Transition>

  </div>
</template>

<style scoped>
.toast-enter-active, .toast-leave-active {
  transition: opacity 220ms ease, transform 220ms ease;
}
.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
