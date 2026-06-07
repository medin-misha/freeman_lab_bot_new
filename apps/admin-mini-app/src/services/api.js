import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Вспомогательная функция для форматирования даты в человекочитаемый вид
 */
function formatDate(dateString, withTime = false) {
  if (!dateString) return '—'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '—'
  
  const options = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }
  
  if (withTime) {
    options.hour = '2-digit'
    options.minute = '2-digit'
  }
  
  return date.toLocaleString('ru-RU', options)
}

/**
 * Маппер для преобразования структуры пользователя бэкенда в структуру, используемую в UI
 */
export function mapBackendUserToList(backendUser) {
  const profile = backendUser.user_profile || {}
  const botStats = backendUser.bot_stats || {}
  const coreReq = backendUser.core_request || {}
  
  // Форматирование даты выдачи методички
  let methodologyDateStr = 'Ожидает'
  if (botStats.received_methodology) {
    methodologyDateStr = botStats.received_methodology_at 
      ? `Выдана ${formatDate(botStats.received_methodology_at, true)}` 
      : 'Линк отправлен в бот'
  }

  // Форматирование даты обновления анкеты
  let coreFormUpdatedAt = 'недавно'
  if (coreReq.updated_at) {
    coreFormUpdatedAt = `Обновлено ${formatDate(coreReq.updated_at)}`
  }

  // Форматирование даты рождения
  let birthDateStr = ''
  if (profile.date_of_birth) {
    const dob = new Date(profile.date_of_birth)
    if (!isNaN(dob.getTime())) {
      const day = String(dob.getDate()).padStart(2, '0')
      const month = String(dob.getMonth() + 1).padStart(2, '0')
      const year = dob.getFullYear()
      birthDateStr = `${day}.${month}.${year}`
    }
  }

  // Маппинг списка диагностик
  const diagnosticsMapped = (backendUser.diagnostic_runs || []).map(run => {
    let diagName = "Диагностика"
    if (run.diagnostic_code === 'default') {
      diagName = "Личностный масштаб"
    } else if (run.diagnostic_code === 'invisible') {
      diagName = "Архетипы власти"
    } else {
      diagName = run.diagnostic_code
    }

    return {
      code: run.diagnostic_code,
      name: diagName,
      status: run.status === 'completed' || run.status === 'finished' ? 'Готово' : 'Прервано',
      date: run.completed_at ? formatDate(run.completed_at, true) : formatDate(run.created_at, true),
      voice: run.voice_file_id ? `${API_BASE_URL}/files/${run.voice_file_id}` : null,
      report: run.result_file_id ? `${API_BASE_URL}/files/${run.result_file_id}` : null,
      transcript: run.transcribation_file_id ? `${API_BASE_URL}/files/${run.transcribation_file_id}` : null
    }
  })

  return {
    id: backendUser.id,
    profile_id: profile.id || null,
    telegram_id: String(backendUser.telegram_id),
    username: backendUser.username || '',
    full_name: profile.full_name || 'Без имени',
    phone: profile.phone || '',
    city: profile.city || '',
    email: profile.email || '',
    timezone: profile.timezone || 'UTC+3 (MSK)',
    birth_date: birthDateStr,
    registration_date: formatDate(backendUser.created_at),
    last_active: backendUser.last_seen_at ? formatDate(backendUser.last_seen_at, true) : '—',
    
    in_core: botStats.core_application_submitted || false,
    current_step: botStats.current_branch || 'Шаг 1: Приветствие',
    step_status: botStats.core_application_submitted ? 'Готово' : 'В процессе',
    notes: profile.note || '',
    source: botStats.source || 'Organic_Traffic',
    channel_subscribed: botStats.channel_subscribe || false,
    channel_check_date: 'Сегодня',
    methodology_received: botStats.received_methodology || false,
    methodology_date: methodologyDateStr,
    
    core_form: botStats.core_application_submitted ? {
      filled: true,
      updated_at: coreFormUpdatedAt,
      activity: coreReq.activity || '',
      request: coreReq.request || '',
      priorities: coreReq.priorities || [],
      readiness: coreReq.readiness || 'Высокая',
      weekly_time: coreReq.weekly_time || '10 ч.',
      difficulties: coreReq.difficulties || '',
      payment_status: coreReq.payment || 'НЕ ОПЛАЧЕНО',
      feedback: 'Согласен',
      feedback_log: 'лог: 192.168.1.1'
    } : {
      filled: false
    },
    diagnostics: diagnosticsMapped
  }
}

/**
 * Получение списка пользователей с бэкенда с пагинацией и поиском
 */
export async function fetchUsers({ page = 1, limit = 8, search = '' } = {}) {
  const params = {
    page,
    limit
  }
  
  if (search.trim()) {
    params.search = search.trim()
  }
  
  try {
    const response = await apiClient.get('/telegram/users', { params })
    const usersList = Array.isArray(response.data) ? response.data : []
    
    return {
      users: usersList.map(mapBackendUserToList),
      // Если пришло ровно limit записей, считаем, что может быть следующая страница
      hasNext: usersList.length === limit
    }
  } catch (error) {
    console.error('Ошибка при загрузке пользователей с бэкенда:', error)
    throw error
  }
}

/**
 * Обновление профиля пользователя
 */
export async function updateUserProfile(profileId, payload) {
  const response = await apiClient.patch(`/telegram/profile/${profileId}`, payload)
  return response.data
}

/**
 * Обновление внешних метрик UserBotStats
 */
export async function updateUserBotStatsExternal(userId, payload) {
  const response = await apiClient.patch(`/stats/user/external`, payload, {
    params: { user_id: userId }
  })
  return response.data
}

/**
 * Обновление внутренних метрик UserBotStats
 */
export async function updateUserBotStatsInternal(userId, payload) {
  const response = await apiClient.patch(`/stats/user/internal`, payload, {
    params: { user_id: userId }
  })
  return response.data
}

/**
 * Синхронизированное сохранение данных пользователя на бэкенд
 */
export async function saveUser(updatedUser) {
  const profileId = updatedUser.profile_id
  const userId = updatedUser.id

  // Парсинг даты рождения DD.MM.YYYY в ISO-строку
  let parsedBirthDate = null
  if (updatedUser.birth_date) {
    const parts = updatedUser.birth_date.split('.')
    if (parts.length === 3) {
      const day = parts[0].padStart(2, '0')
      const month = parts[1].padStart(2, '0')
      const year = parts[2]
      parsedBirthDate = `${year}-${month}-${day}T00:00:00.000Z`
    } else if (updatedUser.birth_date.includes('-')) {
      parsedBirthDate = `${updatedUser.birth_date}T00:00:00.000Z`
    }
  }

  const profilePayload = {
    full_name: updatedUser.full_name,
    phone: updatedUser.phone,
    city: updatedUser.city,
    email: updatedUser.email,
    timezone: updatedUser.timezone,
    date_of_birth: parsedBirthDate,
    note: updatedUser.notes
  }

  const externalStatsPayload = {
    channel_subscribe: updatedUser.channel_subscribed,
    received_methodology: updatedUser.methodology_received
  }

  const internalStatsPayload = {
    core_application_submitted: updatedUser.in_core
  }

  const promises = []
  if (profileId) {
    promises.push(updateUserProfile(profileId, profilePayload))
  }
  promises.push(updateUserBotStatsExternal(userId, externalStatsPayload))
  promises.push(updateUserBotStatsInternal(userId, internalStatsPayload))

  await Promise.all(promises)

  // Запрашиваем обновленные данные из бэкенда для получения свежего замапленного объекта
  const response = await apiClient.get(`/telegram/users/${userId}`)
  return mapBackendUserToList(response.data)
}

export default {
  fetchUsers,
  mapBackendUserToList,
  updateUserProfile,
  updateUserBotStatsExternal,
  updateUserBotStatsInternal,
  saveUser
}
