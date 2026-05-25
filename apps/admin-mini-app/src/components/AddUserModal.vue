<script setup>
import { ref } from 'vue'
import { UserPlus, X } from '@lucide/vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['close', 'addUser'])

const fullName = ref('')
const username = ref('')
const telegramId = ref('')
const phone = ref('')
const city = ref('Москва')
const inCore = ref(false)
const notes = ref('')

const errors = ref({})

function validate() {
  errors.value = {}
  if (!fullName.value.trim()) {
    errors.value.fullName = 'Пожалуйста, заполните Полное имя'
  }
  if (!telegramId.value.trim()) {
    errors.value.telegramId = 'Пожалуйста, заполните Telegram ID'
  } else if (!/^\d+$/.test(telegramId.value.trim())) {
    errors.value.telegramId = 'Telegram ID должен состоять только из цифр'
  }
  
  return Object.keys(errors.value).length === 0
}

function submitForm() {
  if (!validate()) return

  const newUser = {
    telegram_id: telegramId.value.trim(),
    username: username.value.trim(),
    full_name: fullName.value.trim(),
    phone: phone.value.trim() || '—',
    city: city.value.trim(),
    email: '',
    timezone: 'UTC+3 (MSK)',
    birth_date: '—',
    registration_date: 'Только что',
    last_active: 'Только что',
    in_core: inCore.value,
    current_step: 'Не начата',
    step_status: 'Не начата',
    notes: notes.value.trim() || 'Добавлен вручную администратором.',
    source: 'Добавлен вручную администратором.',
    channel_subscribed: false,
    channel_check_date: 'Только что',
    methodology_received: false,
    methodology_date: 'Ожидает',
    core_form: { filled: false },
    diagnostics: []
  }

  emit('addUser', newUser)
  resetForm()
  emit('close')
}

function resetForm() {
  fullName.value = ''
  username.value = ''
  telegramId.value = ''
  phone.value = ''
  city.value = 'Москва'
  inCore.value = false
  notes.value = ''
  errors.value = {}
}
</script>

<template>
  <div 
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 transition-all duration-300 select-none"
    @click.self="emit('close')"
  >
    <!-- Modal Dialog -->
    <div class="w-full max-w-md glass-card rounded-2xl border border-white/10 shadow-2xl overflow-hidden flex flex-col animate-scale-up">
      
      <!-- Modal Header -->
      <div class="bg-[#0c1420]/80 border-b border-white/5 p-5 flex justify-between items-center">
        <h3 class="text-sm font-bold text-white flex items-center gap-2">
          <UserPlus :size="18" class="text-primary" />
          Добавить пользователя в БД
        </h3>
        <button 
          @click="emit('close')"
          class="text-on-surface-variant hover:text-white transition-colors cursor-pointer"
        >
          <X :size="18" />
        </button>
      </div>

      <!-- Modal Body -->
      <form @submit.prevent="submitForm" class="p-6 flex flex-col gap-4 overflow-y-auto max-h-[75vh]">
        <!-- Full Name -->
        <div class="space-y-1">
          <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Полное имя <span class="text-rose-500">*</span></label>
          <input 
            v-model="fullName"
            type="text"
            placeholder="Иван Иванов"
            :class="[
              'w-full bg-surface-container-low border rounded-xl py-2 px-3 text-xs text-white focus:ring-1 focus:ring-primary focus:border-transparent outline-none transition-all',
              errors.fullName ? 'border-rose-500' : 'border-white/10'
            ]"
          />
          <p v-if="errors.fullName" class="text-[10px] text-rose-400 font-semibold mt-1">{{ errors.fullName }}</p>
        </div>

        <!-- Telegram ID & Username -->
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Telegram ID <span class="text-rose-500">*</span></label>
            <input 
              v-model="telegramId"
              type="text"
              placeholder="123456789"
              :class="[
                'w-full bg-surface-container-low border rounded-xl py-2 px-3 text-xs text-white focus:ring-1 focus:ring-primary focus:border-transparent outline-none transition-all font-mono',
                errors.telegramId ? 'border-rose-500' : 'border-white/10'
              ]"
            />
            <p v-if="errors.telegramId" class="text-[10px] text-rose-400 font-semibold mt-1">{{ errors.telegramId }}</p>
          </div>
          <div class="space-y-1">
            <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Username (ТГ)</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-on-surface-variant/40 text-xs">@</span>
              <input 
                v-model="username"
                type="text"
                placeholder="username"
                class="w-full bg-surface-container-low border border-white/10 rounded-xl pl-6 pr-3 py-2 text-xs text-white focus:ring-1 focus:ring-primary focus:border-transparent outline-none transition-all font-semibold text-primary"
              />
            </div>
          </div>
        </div>

        <!-- Phone & City -->
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Телефон</label>
            <input 
              v-model="phone"
              type="text"
              placeholder="+7 (999) 000-00-00"
              class="w-full bg-surface-container-low border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:ring-1 focus:ring-primary focus:border-transparent outline-none"
            />
          </div>
          <div class="space-y-1">
            <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Город</label>
            <input 
              v-model="city"
              type="text"
              placeholder="Москва"
              class="w-full bg-surface-container-low border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:ring-1 focus:ring-primary focus:border-transparent outline-none"
            />
          </div>
        </div>

        <!-- Segment / Access Group toggle -->
        <div class="space-y-2">
          <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Сегмент / Группа доступа</label>
          <div class="flex gap-4 items-center">
            <label class="flex items-center gap-2 cursor-pointer text-xs text-white">
              <input 
                type="radio" 
                :value="true" 
                v-model="inCore"
                class="w-3.5 h-3.5 text-primary bg-neutral-900 border-neutral-700 focus:ring-primary"
              />
              В ядре (Core)
            </label>
            <label class="flex items-center gap-2 cursor-pointer text-xs text-white">
              <input 
                type="radio" 
                :value="false" 
                v-model="inCore"
                class="w-3.5 h-3.5 text-primary bg-neutral-900 border-neutral-700 focus:ring-primary"
              />
              Не в ядре
            </label>
          </div>
        </div>

        <!-- Admin notes -->
        <div class="space-y-1">
          <label class="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Заметка администратора</label>
          <textarea 
            v-model="notes"
            class="w-full bg-surface-container-lowest border border-white/10 rounded-xl p-3 text-xs focus:ring-1 focus:ring-primary outline-none min-h-[80px] resize-none"
            placeholder="Добавьте важную информацию о пользователе..."
          />
        </div>

        <!-- Submit actions -->
        <div class="flex gap-3 mt-4">
          <button 
            type="button"
            @click="emit('close')"
            class="flex-1 py-2.5 border border-white/10 hover:bg-white/5 text-white rounded-xl text-xs font-bold transition-all cursor-pointer active:scale-95"
          >
            Отмена
          </button>
          <button 
            type="submit"
            class="flex-1 py-2.5 bg-primary text-on-primary-fixed hover:bg-opacity-95 rounded-xl text-xs font-bold shadow-lg shadow-primary/10 transition-all cursor-pointer active:scale-95"
          >
            Добавить
          </button>
        </div>
      </form>

    </div>
  </div>
</template>

<style scoped>
.animate-scale-up {
  animation: scale-up 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes scale-up {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
