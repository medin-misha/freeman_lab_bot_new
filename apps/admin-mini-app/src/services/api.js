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
  
  return {
    id: backendUser.id,
    telegram_id: String(backendUser.telegram_id),
    username: backendUser.username || '',
    full_name: profile.full_name || 'Без имени',
    phone: profile.phone || '',
    city: profile.city || '',
    email: profile.email || '',
    timezone: profile.timezone || 'UTC+3 (MSK)',
    birth_date: profile.date_of_birth ? formatDate(profile.date_of_birth) : '',
    registration_date: formatDate(backendUser.created_at),
    last_active: backendUser.last_seen_at ? formatDate(backendUser.last_seen_at, true) : '—',
    
    // Временные поля до полной интеграции модуля статистики в следующих шагах
    in_core: false,
    current_step: 'Шаг 1: Приветствие',
    step_status: 'Не начата',
    notes: profile.note || '',
    source: 'Органический трафик',
    channel_subscribed: false,
    methodology_received: false,
    
    core_form: {
      filled: false
    },
    diagnostics: []
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

export default {
  fetchUsers,
  mapBackendUserToList
}
