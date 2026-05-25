<script setup>
import { computed } from 'vue'
import { TrendingUp, Clock, CheckCircle2 } from '@lucide/vue'

const props = defineProps({
  users: {
    type: Array,
    required: true
  }
})

const totalRawCount = computed(() => 12412 + props.users.length)
const activeToday = computed(() => 1198 + Math.floor(props.users.length * 0.4))
const coreCount = computed(() => props.users.filter(u => u.in_core).length)
const newCount = computed(() => 82 + props.users.length)
</script>

<template>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-md">
    <!-- Card 1 -->
    <div class="glass-card p-md rounded-2xl border border-white/5 space-y-2 flex flex-col justify-between hover:border-primary/40 transition-colors duration-300">
      <span class="text-on-surface-variant uppercase tracking-wider text-[10px] font-semibold">Всего пользователей</span>
      <div class="text-2xl font-bold text-primary">{{ totalRawCount.toLocaleString('ru-RU') }}</div>
      <div class="flex items-center gap-1 text-secondary text-xs font-semibold">
        <TrendingUp :size="12" />
        <span>+5% за неделю</span>
      </div>
    </div>

    <!-- Card 2 -->
    <div class="glass-card p-md rounded-2xl border border-white/5 space-y-2 flex flex-col justify-between hover:border-secondary/40 transition-colors duration-300">
      <span class="text-on-surface-variant uppercase tracking-wider text-[10px] font-semibold">В ядре группы</span>
      <div class="text-2xl font-bold text-secondary">{{ 428 + coreCount }}</div>
      <div class="flex items-center gap-1 text-secondary text-xs font-semibold">
        <CheckCircle2 :size="12" class="text-secondary" />
        <span>Стабильный рост</span>
      </div>
    </div>

    <!-- Card 3 -->
    <div class="glass-card p-md rounded-2xl border border-white/5 space-y-2 flex flex-col justify-between hover:border-white/10 transition-colors duration-300">
      <span class="text-on-surface-variant uppercase tracking-wider text-[10px] font-semibold">Активны сегодня</span>
      <div class="text-2xl font-bold text-on-surface">{{ activeToday.toLocaleString('ru-RU') }}</div>
      <div class="flex items-center gap-1 text-on-surface-variant text-xs font-semibold">
        <Clock :size="12" />
        <span>Пик: 14:00</span>
      </div>
    </div>

    <!-- Card 4 -->
    <div class="glass-card p-md rounded-2xl border border-white/5 space-y-2 flex flex-col justify-between hover:border-tertiary/40 transition-colors duration-300">
      <span class="text-on-surface-variant uppercase tracking-wider text-[10px] font-semibold">Новых (24ч)</span>
      <div class="text-2xl font-bold text-tertiary">{{ newCount }}</div>
      <div class="flex items-center gap-1 text-error text-xs font-semibold">
        <TrendingUp :size="12" class="rotate-180 text-error" />
        <span>-2% vs вчер.</span>
      </div>
    </div>
  </div>
</template>
