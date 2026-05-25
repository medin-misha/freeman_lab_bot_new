<script setup>
const props = defineProps({
  broadcasts: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['deleteBroadcast'])
</script>

<template>
  <div class="bg-[#121c2c]/40 border border-[#1e2d44]/50 rounded-xl p-5 shadow-xl flex flex-col gap-5">
    
    <div>
      <h2 class="text-lg font-bold text-white flex items-center gap-2 select-none">
        <span class="material-symbols-outlined text-blue-500">history</span>
        Логи отправленных и запланированных пушей
      </h2>
      <p class="text-xs text-[#8a9db9] mt-0.5 select-none">
        История вещания и календарная сетка отложенных рассылок. Администраторы могут отозвать или удалить запланированное сообщение до начала отправки.
      </p>
    </div>

    <!-- Active Broadcasts Grid/List -->
    <div v-if="broadcasts.length > 0" class="flex flex-col gap-4">
      <div 
        v-for="log in broadcasts" 
        :key="log.id"
        class="bg-[#0e1624]/60 border border-[#1e2d44]/40 rounded-xl p-4 flex flex-col md:flex-row justify-between md:items-center gap-4 hover:border-blue-500/20 transition-all duration-200"
      >
        <!-- Info Column -->
        <div class="flex-1 flex flex-col gap-2">
          <!-- Top badge line -->
          <div class="flex flex-wrap items-center gap-2 select-none">
            <span class="text-[10px] font-bold text-blue-400 font-mono">РАССЫЛКА #{{ log.id }}</span>
            <span 
              :class="[
                'px-1.5 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider',
                log.status === 'Отправлено' 
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              ]"
            >
              {{ log.status }}
            </span>
            <span class="text-[10px] text-[#5c7799]">{{ log.time_label }}</span>
          </div>

          <!-- Message Body Snippet -->
          <p class="text-xs text-[#dce2f3] bg-[#0c1420]/50 p-2.5 rounded-lg border border-[#1e2d44]/30 leading-relaxed font-normal whitespace-pre-wrap">
            {{ log.text }}
          </p>

          <!-- Targeting Criteria metadata badges -->
          <div class="flex flex-wrap gap-1.5 mt-1 select-none text-[9px] text-[#8a9db9]">
            <span class="bg-[#121c2d] px-2 py-0.5 border border-[#1e2d44]/40 rounded">
              Охват: <strong class="text-white">{{ log.reach }}</strong> респондентов
            </span>
            <span class="bg-[#121c2d] px-2 py-0.5 border border-[#1e2d44]/40 rounded">
              Сегмент: <strong class="text-white">{{ log.targeting.segment }}</strong>
            </span>
            <span class="bg-[#121c2d] px-2 py-0.5 border border-[#1e2d44]/40 rounded">
              Диагностика: <strong class="text-white">{{ log.targeting.diagnostics }}</strong>
            </span>
            <span class="bg-[#121c2d] px-2 py-0.5 border border-[#1e2d44]/40 rounded">
              Только с методичкой: <strong class="text-white">{{ log.targeting.only_with_methodology ? 'Да' : 'Нет' }}</strong>
            </span>
          </div>
        </div>

        <!-- Action Column -->
        <div class="flex md:flex-col items-end gap-2 justify-end select-none">
          <button 
            @click="emit('deleteBroadcast', log.id)"
            class="flex items-center gap-1 px-3 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 hover:border-rose-500/30 text-rose-400 rounded-lg text-xs font-semibold hover:scale-[1.02] active:scale-[0.98] transition-all duration-200"
          >
            <span class="material-symbols-outlined text-sm select-none">delete</span>
            Удалить
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="border border-[#1e2d44]/20 bg-[#0e1624]/40 p-8 rounded-xl text-center select-none">
      <span class="material-symbols-outlined text-4xl text-[#4f6b8b] mb-2">broadcast_on_personal</span>
      <p class="text-sm font-semibold text-white">Истории трансляций пока нет</p>
      <p class="text-xs text-[#5c7799] mt-0.5">Напишите текст в конструкторе для пилотного пуша сообщения.</p>
    </div>

  </div>
</template>
