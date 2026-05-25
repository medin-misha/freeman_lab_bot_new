<script setup>
import { ref, watch } from 'vue'
import { 
  ArrowLeft, 
  Send, 
  Save, 
  Fingerprint, 
  User as UserIcon, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  TrendingUp, 
  HelpCircle,
  FileText, 
  Mic, 
  FileSpreadsheet, 
  Network, 
  Tag, 
  ToggleLeft, 
  ChevronDown, 
  ChevronUp, 
  History, 
  Check, 
  Smartphone, 
  MapPin, 
  Calendar 
} from '@lucide/vue'

const props = defineProps({
  user: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'saveUser'])

// Local reactive edit states matching UserDetail.tsx
const fullName = ref('')
const phone = ref('')
const city = ref('')
const email = ref('')
const timezone = ref('')
const birthDate = ref('')
const localNotes = ref('')
const channelSubscribed = ref(false)
const inCore = ref(false)
const bookletReceived = ref(false)

// UI Interactivity states
const isAccordionOpen = ref(true)
const showNotification = ref(false)
const notificationMsg = ref('')
const copiedId = ref(false)

watch(() => props.user, (newVal) => {
  if (newVal) {
    fullName.value = newVal.full_name || ''
    phone.value = newVal.phone || ''
    city.value = newVal.city || ''
    email.value = newVal.email || ''
    timezone.value = newVal.timezone || 'UTC+3 (MSK)'
    birthDate.value = newVal.birth_date || ''
    localNotes.value = newVal.notes || ''
    channelSubscribed.value = newVal.channel_subscribed || false
    inCore.value = newVal.in_core || false
    bookletReceived.value = newVal.methodology_received || false
  }
}, { immediate: true })

function handleCopyId() {
  navigator.clipboard.writeText(props.user.telegram_id || props.user.id)
  copiedId.value = true
  triggerNotification('Telegram ID скопирован!')
  setTimeout(() => copiedId.value = false, 2000)
}

function handleTelegramClick() {
  triggerNotification(`Открываем чат Telegram для пользователя @${props.user.username || props.user.telegram_id}...`)
  if (props.user.username) {
    window.open(`https://t.me/${props.user.username}`, '_blank')
  }
}

function handleSave() {
  const updatedUser = {
    ...props.user,
    full_name: fullName.value,
    phone: phone.value,
    city: city.value,
    email: email.value,
    timezone: timezone.value,
    birth_date: birthDate.value,
    notes: localNotes.value,
    channel_subscribed: channelSubscribed.value,
    in_core: inCore.value,
    methodology_received: bookletReceived.value
  }
  emit('saveUser', updatedUser)
  triggerNotification('Изменения профиля успешно сохранены в базе ПМЛ!')
}

function triggerNotification(msg) {
  notificationMsg.value = msg
  showNotification.value = true
  setTimeout(() => {
    showNotification.value = false
  }, 3000)
}

function playVoice(diagCode) {
  triggerNotification(`🔊 Прослушивание голосового ответа для диагностики ${diagCode}...`)
}

function downloadReport(diagCode) {
  triggerNotification(`📥 Скачивание PDF-отчета для диагностики ${diagCode}...`)
}

function viewTranscript(diagCode) {
  triggerNotification(`📄 Открытие транскрибации для диагностики ${diagCode}...`)
}
</script>

<template>
  <div class="space-y-lg relative">
    
    <!-- Toast Notification Banner -->
    <Transition name="toast">
      <div 
        v-if="showNotification"
        class="fixed top-20 right-4 left-4 md:left-auto md:right-6 z-50 bg-[#19202b] border-l-4 border-secondary px-6 py-4 rounded-xl shadow-xl flex items-center gap-3 border border-white/5"
      >
        <div class="w-8 h-8 rounded-full bg-secondary/15 flex items-center justify-center text-secondary">
          <Check :size="16" />
        </div>
        <div>
          <p class="text-sm font-semibold text-on-surface">{{ notificationMsg }}</p>
          <p class="text-[11px] text-on-surface-variant">База данных обновлена в реальном времени</p>
        </div>
      </div>
    </Transition>

    <!-- Breadcrumbs & Actions Header -->
    <div class="mb-lg flex flex-col md:flex-row md:items-end justify-between gap-md">
      <div>
        <nav class="flex items-center gap-2 text-on-surface-variant text-xs mb-3 select-none">
          <span 
            @click="emit('close')"
            class="hover:text-primary cursor-pointer flex items-center gap-1 transition-colors"
          >
            <ArrowLeft :size="12" />
            Пользователи
          </span>
          <span class="material-symbols-outlined text-[14px]">chevron_right</span>
          <span class="text-primary font-bold">@{{ user.username || user.telegram_id }}</span>
        </nav>
        
        <div class="flex flex-col sm:flex-row sm:items-center gap-3">
          <h2 class="text-2xl lg:text-3xl font-bold text-on-surface">
            {{ fullName || user.full_name }}
          </h2>
          <span :class="[
            'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border self-start sm:self-auto select-none',
            inCore 
              ? 'bg-secondary/10 text-secondary border-secondary/20' 
              : 'bg-on-surface-variant/10 text-on-surface-variant border-on-surface-variant/20'
          ]">
            {{ inCore ? 'Ядро группы' : 'Не в ядре' }}
          </span>
          <span class="bg-secondary/10 text-secondary text-xs px-2.5 py-0.5 rounded-full border border-secondary/20 font-semibold self-start sm:self-auto select-none">
            Активен
          </span>
        </div>
      </div>

      <div class="flex gap-2 self-start md:self-auto select-none">
        <button 
          @click="handleTelegramClick"
          class="bg-surface-container-highest text-on-surface hover:bg-white/5 hover:text-white px-4 py-2.5 rounded-xl text-xs flex items-center gap-2 border border-white/5 transition-all active:scale-95 cursor-pointer font-semibold"
        >
          <Send :size="14" class="text-primary" />
          Написать в ТГ
        </button>
        <button 
          @click="handleSave"
          class="bg-primary text-on-primary-fixed hover:bg-opacity-95 px-5 py-2.5 rounded-xl text-xs flex items-center gap-2 font-semibold shadow-lg shadow-primary/10 transition-all active:scale-95 cursor-pointer"
        >
          <Save :size="14" />
          Сохранить изменения
        </button>
      </div>
    </div>

    <!-- Main Content Grid Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-lg items-start">
      
      <!-- Left Column: Primary User Cards -->
      <div class="lg:col-span-4 space-y-lg">
        
        <!-- Identification Card -->
        <section class="glass-card rounded-2xl p-lg space-y-md border border-white/5">
          <div class="flex items-center gap-2.5 pb-2 border-b border-white/5 select-none">
            <Fingerprint class="text-primary" :size="20" />
            <h3 class="font-semibold text-sm tracking-wide text-on-surface uppercase pr-1">Идентификация</h3>
          </div>
          
          <div class="space-y-3 text-sm">
            <div class="flex justify-between items-center">
              <span class="text-on-surface-variant text-xs">Telegram ID</span>
              <div class="flex items-center gap-2">
                <span 
                  @click="handleCopyId"
                  class="font-mono text-on-surface font-semibold bg-white/5 px-2 py-0.5 rounded select-all cursor-pointer text-xs"
                >
                  {{ user.telegram_id }}
                </span>
                <button 
                  @click="handleCopyId"
                  class="text-primary hover:text-white transition-colors text-[10px] font-semibold"
                >
                  {{ copiedId ? 'Скопировано!' : 'Копировать' }}
                </button>
              </div>
            </div>

            <div class="flex justify-between items-center">
              <span class="text-on-surface-variant text-xs">Username</span>
              <span class="text-primary font-semibold">@{{ user.username || '—' }}</span>
            </div>

            <div class="flex justify-between items-center">
              <span class="text-on-surface-variant text-xs">Язык интерфейса</span>
              <span class="bg-surface-container-highest text-on-surface px-2 py-0.5 rounded font-mono text-xs select-none">RU</span>
            </div>

            <div class="flex justify-between items-center">
              <span class="text-on-surface-variant text-xs">Был в сети</span>
              <span class="text-on-surface font-mono text-xs font-semibold">{{ user.last_active }}</span>
            </div>

            <div class="flex justify-between items-center">
              <span class="text-on-surface-variant text-xs">Дата регистрации</span>
              <span class="text-on-surface font-mono text-xs">{{ user.registration_date }}</span>
            </div>
          </div>
        </section>

        <!-- Profile Details Editable Card -->
        <section class="glass-card rounded-2xl p-lg space-y-md border border-white/5">
          <div class="flex items-center gap-2.5 pb-2 border-b border-white/5 select-none">
            <UserIcon class="text-primary" :size="20" />
            <h3 class="font-semibold text-sm tracking-wide text-on-surface uppercase pr-1">Профиль участника</h3>
          </div>

          <div class="space-y-md">
            <div class="space-y-1">
              <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold select-none">Полное имя</label>
              <div class="relative">
                <span class="absolute left-3 top-2.5 text-on-surface-variant/50"><UserIcon :size="14" /></span>
                <input 
                  type="text" 
                  v-model="fullName"
                  class="w-full bg-surface-container-low border border-white/10 rounded-xl py-2 pl-9 pr-3 text-sm focus:ring-1 focus:ring-primary focus:border-transparent outline-none"
                />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-md">
              <div class="space-y-1">
                <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold select-none">Телефон</label>
                <div class="relative">
                  <span class="absolute left-3 top-2.5 text-on-surface-variant/50"><Smartphone :size="14" /></span>
                  <input 
                    type="text" 
                    v-model="phone"
                    class="w-full text-xs bg-surface-container-low border border-white/10 rounded-xl py-2 pl-8 pr-2 focus:ring-1 focus:ring-primary focus:border-transparent outline-none"
                  />
                </div>
              </div>

              <div class="space-y-1">
                <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold select-none">Город</label>
                <div class="relative">
                  <span class="absolute left-3 top-2.5 text-on-surface-variant/50"><MapPin :size="14" /></span>
                  <input 
                    type="text" 
                    v-model="city"
                    class="w-full text-xs bg-surface-container-low border border-white/10 rounded-xl py-2 pl-8 pr-2 focus:ring-1 focus:ring-primary focus:border-transparent outline-none"
                  />
                </div>
              </div>
            </div>

            <div class="space-y-1">
              <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold select-none">Электронная почта</label>
              <input 
                type="email" 
                v-model="email"
                class="w-full bg-surface-container-low border border-white/10 rounded-xl py-2 px-3 text-xs focus:ring-1 focus:ring-primary focus:border-transparent outline-none"
              />
            </div>

            <div class="grid grid-cols-2 gap-md">
              <div class="space-y-1">
                <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold select-none">Часовой пояс</label>
                <input 
                  type="text" 
                  v-model="timezone"
                  class="w-full bg-surface-container-low border border-white/10 rounded-xl py-2 px-3 text-xs focus:ring-1 focus:ring-primary focus:border-transparent outline-none font-mono"
                />
              </div>
              <div class="space-y-1">
                <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold select-none">Дата рождения</label>
                <div class="relative">
                  <span class="absolute left-3 top-2.5 text-on-surface-variant/50"><Calendar :size="12" /></span>
                  <input 
                    type="text" 
                    v-model="birthDate"
                    class="w-full text-xs bg-surface-container-low border border-white/10 rounded-xl py-2 pl-8 pr-2 focus:ring-1 focus:ring-primary outline-none"
                  />
                </div>
              </div>
            </div>

            <div class="space-y-1 pt-2">
              <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold select-none">Сегмент / Статус доступа</label>
              <select 
                v-model="inCore"
                class="w-full bg-surface-container-low border border-white/10 rounded-xl py-2 px-3 text-xs focus:ring-1 focus:ring-primary focus:border-transparent outline-none cursor-pointer"
              >
                <option :value="true">В ядре (Core)</option>
                <option :value="false">Не в ядре</option>
              </select>
            </div>

            <div class="space-y-1.5 pt-2">
              <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold select-none">Заметка админа</label>
              <textarea 
                v-model="localNotes"
                class="w-full bg-surface-container-lowest border border-white/10 rounded-xl p-3 text-xs focus:ring-1 focus:ring-primary outline-none min-h-[100px] resize-none"
                placeholder="Добавьте важную информацию о пользователе..."
              />
            </div>
          </div>
        </section>
      </div>

      <!-- Right Column: UTM marketing statistics & checklist audits -->
      <div class="lg:col-span-8 space-y-lg">
        
        <!-- UTM marketing stats row -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-md">
          <section class="glass-card rounded-2xl p-md border border-white/5 relative overflow-hidden flex flex-col justify-between hover:border-primary/20 transition-colors duration-300">
            <div class="flex items-center gap-2 mb-2 text-on-surface-variant/70 select-none">
              <Tag :size="14" class="text-primary" />
              <span class="text-xs font-semibold">Источник (UTM)</span>
            </div>
            <div class="font-semibold text-lg text-primary truncate">
              {{ user.source && user.source.includes('ручную') ? 'Admin_Console' : (user.source || 'Organic_Traffic') }}
            </div>
            <div class="text-[11px] text-on-surface-variant font-mono mt-1 select-none">
              Source Log: {{ user.source || 'yandex_direct' }}
            </div>
          </section>

          <section class="glass-card rounded-2xl p-md border border-white/5 relative overflow-hidden flex flex-col justify-between hover:border-white/10 transition-colors duration-300">
            <div class="flex items-center gap-1.5 mb-2 text-on-surface-variant/70 select-none">
              <Network :size="14" class="text-secondary" />
              <span class="text-xs font-semibold">Текущая ветка</span>
            </div>
            <div class="font-semibold text-lg text-on-surface truncate">
              Core_Application_V2
            </div>
            <div class="text-[11px] text-on-surface-variant mt-1 font-semibold text-secondary flex items-center gap-1 select-none">
              <span class="w-1.5 h-1.5 rounded-full bg-secondary"></span>
              {{ user.current_step || "Шаг 4: Мотивация" }}
            </div>
          </section>

          <section class="glass-card rounded-2xl p-md border border-white/5 flex flex-col justify-between hover:border-secondary/20 transition-colors duration-300">
            <div class="flex items-center justify-between select-none">
              <div class="flex items-center gap-1.5 text-on-surface-variant/70">
                <ToggleLeft :size="14" :class="channelSubscribed ? 'text-secondary' : 'text-on-surface-variant'" />
                <span class="text-xs font-semibold">Подписка на канал</span>
              </div>
            </div>
            
            <div class="flex items-center justify-between mt-2 select-none">
              <span :class="['font-semibold text-lg', channelSubscribed ? 'text-secondary' : 'text-on-surface-variant']">
                {{ channelSubscribed ? "Да" : "Нет" }}
              </span>
              
              <button 
                @click="channelSubscribed = !channelSubscribed"
                :class="[
                  'w-9 h-5 rounded-full relative p-0.5 transition-colors cursor-pointer',
                  channelSubscribed ? 'bg-secondary' : 'bg-surface-container-highest'
                ]"
              >
                <div :class="[
                  'w-4 h-4 bg-white rounded-full shadow transition-all',
                  channelSubscribed ? 'translate-x-[16px]' : 'translate-x-0'
                ]" />
              </button>
            </div>
            <div class="text-[11px] text-on-surface-variant font-mono mt-1 select-none">
              Проверка: {{ user.channel_check_date || 'Сегодня' }}
            </div>
          </section>
        </div>

        <!-- Bot Statuses row -->
        <section class="glass-card rounded-2xl p-lg border border-white/5">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-lg text-center sm:text-left select-none">
            <div class="space-y-1">
              <div class="text-on-surface-variant text-[10px] font-bold uppercase tracking-wider">Методичка PML</div>
              <div class="flex items-center gap-2 justify-center sm:justify-start">
                <button 
                  @click="bookletReceived = !bookletReceived"
                  class="focus:outline-none cursor-pointer flex items-center"
                >
                  <span v-if="bookletReceived" class="material-symbols-outlined text-secondary font-bold text-[22px]">check_circle</span>
                  <span v-else class="material-symbols-outlined text-on-surface-variant/40 text-[22px]">pending</span>
                </button>
                <span class="font-bold text-headline-sm">
                  {{ bookletReceived ? "Получена" : "Ожидает" }}
                </span>
              </div>
              <p class="text-[11px] text-on-surface-variant">
                {{ bookletReceived ? (user.methodology_date || "Выдана сегодня в боте") : "Линк отправлен в бот" }}
              </p>
            </div>

            <div class="border-t sm:border-t-0 sm:border-l border-white/5 pt-lg sm:pt-0 sm:pl-lg space-y-1">
              <div class="text-on-surface-variant text-[10px] font-bold uppercase tracking-wider">Анкета Ядра</div>
              <div :class="['flex items-center gap-2 justify-center sm:justify-start', user.core_form?.filled ? 'text-secondary' : 'text-primary']">
                <span class="material-symbols-outlined text-[22px] font-bold">check_circle</span>
                <span class="font-bold text-headline-sm">
                  {{ user.core_form?.filled ? 'Заполнена' : 'Не начата' }}
                </span>
              </div>
              <p class="text-[11px] text-on-surface-variant">
                {{ user.core_form?.filled ? (user.core_form?.updated_at || 'Обновлено') : 'Отбор в группу' }}
              </p>
            </div>

            <div class="border-t sm:border-t-0 sm:border-l border-white/5 pt-lg sm:pt-0 sm:pl-lg space-y-1">
              <div class="text-on-surface-variant text-[10px] font-bold uppercase tracking-wider">Отзывы & Согласие</div>
              <div class="flex items-center gap-2 justify-center sm:justify-start">
                <span class="material-symbols-outlined text-secondary text-[22px] font-bold">check_circle</span>
                <span class="font-bold text-headline-sm">Согласен / Ок</span>
              </div>
              <p class="text-[11px] text-on-surface-variant">{{ user.core_form?.feedback_log || 'лог: 192.168.1.1' }}</p>
            </div>
          </div>
        </section>

        <!-- Diagnostics List Section -->
        <section class="glass-card rounded-2xl p-lg border border-white/5">
          <div class="flex items-center justify-between mb-lg border-b border-white/5 pb-2">
            <div class="flex items-center gap-2 select-none">
              <span class="material-symbols-outlined text-primary text-[22px]" style="font-variation-settings: 'FILL' 1">query_stats</span>
              <h3 class="font-semibold text-headline-sm text-on-surface uppercase tracking-wide text-xs">Результаты диагностик</h3>
            </div>
            
            <div class="flex gap-md font-mono select-none">
              <div class="flex flex-col items-end">
                <span class="text-[10px] text-on-surface-variant font-semibold">Пройдено</span>
                <span class="text-sm font-bold text-primary">
                  {{ user.diagnostics?.filter(d => d.status === 'Готово').length || 0 }}
                </span>
              </div>
              <div class="w-[1px] h-8 bg-white/10" />
              <div class="flex flex-col items-end">
                <span class="text-[10px] text-on-surface-variant font-semibold">Всего</span>
                <span class="text-sm font-bold text-secondary">
                  {{ user.diagnostics?.length || 0 }}
                </span>
              </div>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left">
              <thead class="text-on-surface-variant text-xs border-b border-white/5 select-none">
                <tr>
                  <th class="pb-2 font-medium">Код</th>
                  <th class="pb-2 font-medium">Диагностика</th>
                  <th class="pb-2 font-medium">Статус опроса</th>
                  <th class="pb-2 font-medium">Дата завершения</th>
                  <th class="pb-2 font-medium text-right">Материалы респондента</th>
                </tr>
              </thead>
              <tbody class="text-xs text-on-surface divide-y divide-white/5 font-sans">
                <tr v-if="user.diagnostics && user.diagnostics.length > 0" v-for="diag in user.diagnostics" :key="diag.code" class="hover:bg-white/2 transition-colors">
                  <td class="py-3 font-mono font-semibold text-primary select-all">{{ diag.code }}</td>
                  <td class="py-3 font-semibold text-on-surface">{{ diag.name }}</td>
                  <td class="py-3 select-none">
                    <span v-if="diag.status === 'Готово'" class="text-secondary flex items-center gap-1 font-semibold">
                      <span class="w-1.5 h-1.5 bg-secondary rounded-full animate-pulse"></span>
                      Готово
                    </span>
                    <span v-else class="text-on-surface-variant/60">Прервано</span>
                  </td>
                  <td class="py-3 text-on-surface-variant font-mono">{{ diag.date }}</td>
                  <td class="py-3 text-right">
                    <div class="flex justify-end gap-2">
                      <button 
                        @click="playVoice(diag.code)"
                        :disabled="!diag.voice"
                        :class="[
                          'p-1.5 rounded-lg transition-colors cursor-pointer',
                          diag.voice ? 'text-primary hover:bg-primary/10' : 'text-on-surface-variant/20 cursor-not-allowed'
                        ]"
                        :title="diag.voice ? 'Прослушать голосовой ответ' : 'Голосовой ответ отсутствует'"
                      >
                        <Mic :size="14" />
                      </button>
                      <button 
                        @click="downloadReport(diag.code)"
                        :disabled="!diag.report"
                        :class="[
                          'p-1.5 rounded-lg transition-colors cursor-pointer',
                          diag.report ? 'text-primary hover:bg-primary/10' : 'text-on-surface-variant/20 cursor-not-allowed'
                        ]"
                        :title="diag.report ? 'Скачать PDF отчет' : 'Отчет не сгенерирован'"
                      >
                        <FileText :size="14" />
                      </button>
                      <button 
                        @click="viewTranscript(diag.code)"
                        :disabled="!diag.transcript"
                        :class="[
                          'p-1.5 rounded-lg transition-colors cursor-pointer',
                          diag.transcript ? 'text-primary hover:bg-primary/10' : 'text-on-surface-variant/20 cursor-not-allowed'
                        ]"
                        :title="diag.transcript ? 'Посмотреть транскрибацию' : 'Транскрипт отсутствует'"
                      >
                        <FileSpreadsheet :size="14" />
                      </button>
                    </div>
                  </td>
                </tr>

                <tr v-else>
                  <td colspan="5" class="py-6 text-center text-on-surface-variant/60 select-none">
                    Пользователь еще не запускал психологические диагностики в боте PML.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- Expandable Core Questionnaire Applications detail -->
        <section class="space-y-sm">
          <div class="flex items-center gap-1.5 px-1 select-none">
            <span class="material-symbols-outlined text-primary text-[20px]" style="font-variation-settings: 'FILL' 1">assignment</span>
            <h3 class="font-semibold text-headline-sm text-on-surface uppercase tracking-wide text-xs">Анкеты Ядра (Core)</h3>
          </div>

          <div 
            v-if="user.core_form?.filled" 
            :class="[
              'glass-card rounded-2xl overflow-hidden border border-white/5 transition-all border-l-4',
              user.core_form?.filled ? 'border-l-primary' : 'border-l-white/10'
            ]"
          >
            <!-- Accordion Trigger -->
            <div 
              @click="isAccordionOpen = !isAccordionOpen"
              class="p-lg bg-primary/2 hover:bg-primary/5 cursor-pointer flex justify-between items-center group transition-colors select-none"
            >
              <div>
                <h4 class="font-bold text-headline-sm text-primary mb-0.5 flex items-center gap-2">
                  CORE-APPLICATION-01
                  <span class="text-[10px] bg-primary/20 text-primary uppercase font-bold px-2 py-0.5 rounded tracking-wide">Актуальная</span>
                </h4>
                <p class="text-xs text-on-surface-variant">Подана {{ user.core_form?.updated_at || 'недавно' }}</p>
              </div>
              
              <div
                :style="{ transform: isAccordionOpen ? 'rotate(180deg)' : 'rotate(0deg)' }"
                class="text-primary transition-transform duration-200"
              >
                <ChevronDown :size="20" />
              </div>
            </div>

            <!-- Accordion Body -->
            <div v-show="isAccordionOpen" class="overflow-hidden border-t border-white/5">
              <div class="p-lg space-y-md text-xs font-sans">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-lg">
                  <div class="space-y-md">
                    <div>
                      <label class="block text-on-surface-variant text-[10px] font-semibold uppercase tracking-wider mb-2 select-none">Деятельность</label>
                      <p class="bg-surface-container p-3 rounded-xl border border-white/5 text-on-surface font-semibold leading-relaxed">
                        {{ user.core_form.activity }}
                      </p>
                    </div>

                    <div>
                      <label class="block text-on-surface-variant text-[10px] font-semibold uppercase tracking-wider mb-2 select-none">Глубинный Запрос</label>
                      <p class="bg-surface-container p-3 rounded-xl border border-white/5 text-on-surface font-semibold leading-relaxed">
                        {{ user.core_form.request }}
                      </p>
                    </div>

                    <div>
                      <label class="block text-on-surface-variant text-[10px] font-semibold uppercase tracking-wider mb-2 select-none">Приоритеты масштабирования</label>
                      <div class="flex flex-wrap gap-1.5 mt-1 select-none">
                        <span 
                          v-for="prio in user.core_form.priorities"
                          :key="prio"
                          class="bg-primary-container/20 text-on-primary-container px-3 py-1 rounded-full border border-primary/20 hover:bg-primary/20 transition-all font-semibold"
                        >
                          {{ prio }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div class="space-y-md">
                    <div class="grid grid-cols-2 gap-md select-none">
                      <div class="bg-surface-container p-3 rounded-xl border border-white/5 text-center">
                        <span class="text-[10px] font-semibold text-on-surface-variant block mb-1 uppercase tracking-wider">Готовность к изменениям</span>
                        <span class="font-bold text-headline-sm text-secondary">{{ user.core_form.readiness || 'Высокая' }}</span>
                      </div>
                      <div class="bg-surface-container p-3 rounded-xl border border-white/5 text-center">
                        <span class="text-[10px] font-semibold text-on-surface-variant block mb-1 uppercase tracking-wider">Время в неделю</span>
                        <span class="font-bold text-headline-sm text-on-surface">{{ user.core_form.weekly_time || '10 ч.' }}</span>
                      </div>
                    </div>

                    <div>
                      <label class="block text-on-surface-variant text-[10px] font-semibold uppercase tracking-wider mb-2 select-none">Трудности</label>
                      <p class="text-on-surface italic p-3 bg-surface-container rounded-xl border border-white/5 leading-relaxed font-semibold">
                        &ldquo;{{ user.core_form.difficulties }}&rdquo;
                      </p>
                    </div>

                    <div class="flex items-center justify-between p-3 bg-surface-container rounded-xl border border-white/5 font-semibold select-none">
                      <span class="text-on-surface">Статус оплаты участия</span>
                      <span v-if="user.core_form.payment_status === 'ОПЛАЧЕНО'" class="bg-secondary text-on-secondary px-3 py-1 rounded-full text-[10px] tracking-wide font-black">
                        ОПЛАЧЕНО
                      </span>
                      <span v-else class="bg-error text-on-error px-3 py-1 rounded-full text-[10px] tracking-wide font-black">
                        НЕ ОПЛАЧЕНО
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="glass-card rounded-2xl p-lg text-center text-on-surface-variant/60 border border-white/5 select-none font-semibold">
            Анкета отбора в Ядро группы еще не заполнена пользователем.
          </div>
        </section>

        <!-- Analysis timeline session registrations -->
        <section class="glass-card rounded-2xl p-lg border border-white/5">
          <div class="flex items-center gap-2 mb-lg border-b border-white/5 pb-2 select-none">
            <History class="text-primary animate-spin" style="animation-duration: 8s" :size="20" />
            <h3 class="font-semibold text-headline-sm text-on-surface uppercase tracking-wide text-xs">Регистрация на разборы</h3>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-md font-mono select-none">
            <div class="p-2 rounded-xl text-center border bg-primary/5 border-primary/20 text-on-surface hover:shadow-lg hover:shadow-primary/5">
              <span class="text-[10px] text-on-surface-variant block font-semibold">18.05.2026</span>
              <span class="text-xs font-bold block mt-1">16:30</span>
            </div>
            <div class="p-2 rounded-xl text-center border bg-surface-container-highest border-white/5 opacity-40">
              <span class="text-[10px] text-on-surface-variant block font-semibold">12.04.2026</span>
              <span class="text-xs font-bold block mt-1">14:00</span>
            </div>
          </div>
        </section>

      </div>
    </div>
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
