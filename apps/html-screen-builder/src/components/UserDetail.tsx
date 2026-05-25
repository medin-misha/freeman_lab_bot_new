import React, { useState } from 'react';
import { User, Diagnostic } from '../types';
import { motion, AnimatePresence } from 'motion/react';
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
} from 'lucide-react';

interface UserDetailProps {
  user: User;
  onBack: () => void;
  onUpdateUser: (updatedUser: User) => void;
}

export default function UserDetail({ user, onBack, onUpdateUser }: UserDetailProps) {
  // Local edit states for profile forms
  const [fullName, setFullName] = useState(user.fullName);
  const [phone, setPhone] = useState(user.phone);
  const [city, setCity] = useState(user.city);
  const [email, setEmail] = useState(user.email);
  const [timezone, setTimezone] = useState(user.timezone);
  const [birthDate, setBirthDate] = useState(user.birthDate);
  const [adminNotes, setAdminNotes] = useState(user.adminNotes);
  const [channelSubscribed, setChannelSubscribed] = useState(user.channelSubscribed);
  const [status, setStatus] = useState<User['status']>(user.status);
  const [bookletReceived, setBookletReceived] = useState(user.bookletReceived);
  
  // Interactivity states
  const [isAccordionOpen, setIsAccordionOpen] = useState(true);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMsg, setNotificationMsg] = useState('');
  const [copiedId, setCopiedId] = useState(false);

  const handleCopyId = () => {
    navigator.clipboard.writeText(user.id);
    setCopiedId(true);
    setTimeout(() => setCopiedId(false), 2000);
  };

  const handleTelegramClick = () => {
    // Simulated TG launching message
    setNotificationMsg(`Открываем чат Telegram для пользователя ${user.username}...`);
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 3000);
  };

  const handleSave = () => {
    const updatedUser: User = {
      ...user,
      fullName,
      phone,
      city,
      email,
      timezone,
      birthDate,
      adminNotes,
      channelSubscribed,
      status,
      bookletReceived
    };
    onUpdateUser(updatedUser);
    setNotificationMsg('Изменения профиля успешно сохранены в базе ПМЛ!');
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 3000);
  };

  return (
    <div className="space-y-lg relative">
      {/* Toast Notification Banner */}
      <AnimatePresence>
        {showNotification && (
          <motion.div 
            initial={{ opacity: 0, y: -40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -40 }}
            className="fixed top-20 right-6 z-50 bg-[#19202b] border-l-4 border-secondary px-6 py-4 rounded-xl shadow-xl flex items-center gap-3 border border-white/5"
          >
            <div className="w-8 h-8 rounded-full bg-secondary/15 flex items-center justify-center text-secondary">
              <Check size={16} />
            </div>
            <div>
              <p className="text-body-md font-semibold text-on-surface">{notificationMsg}</p>
              <p className="text-[11px] text-on-surface-variant">База данных обновлена в реальном времени</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Breadcrumbs & Actions Header */}
      <div className="mb-lg flex flex-col md:flex-row md:items-end justify-between gap-md">
        <div>
          <nav className="flex items-center gap-2 text-on-surface-variant font-label-md text-xs mb-3">
            <span 
              onClick={onBack}
              className="hover:text-primary cursor-pointer flex items-center gap-1 transition-colors"
            >
              <ArrowLeft size={12} />
              Пользователи
            </span>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            <span className="text-primary font-bold">{user.username}</span>
          </nav>
          
          <div className="flex flax-col sm:flex-row sm:items-center gap-3">
            <h2 className="text-2xl lg:text-3xl font-bold text-on-surface">
              {fullName || user.fullName}
            </h2>
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border self-start sm:self-auto ${
              user.status === 'В ядре' 
                ? 'bg-secondary/10 text-secondary border-secondary/20' 
                : 'bg-on-surface-variant/10 text-on-surface-variant border-on-surface-variant/20'
            }`}>
              {status === 'В ядре' ? 'Ядро группы' : status}
            </span>
            <span className="bg-secondary/10 text-secondary text-xs px-2.5 py-0.5 rounded-full border border-secondary/20 font-semibold self-start sm:self-auto">
              Активен
            </span>
          </div>
        </div>

        <div className="flex gap-2 self-start md:self-auto">
          <button 
            onClick={handleTelegramClick}
            className="bg-surface-container-highest text-on-surface hover:bg-surface-bright px-4 py-2.5 rounded-xl font-label-md text-xs flex items-center gap-2 border border-white/5 transition-all active:scale-95 cursor-pointer"
          >
            <Send size={14} className="text-primary" />
            Написать в ТГ
          </button>
          <button 
            onClick={handleSave}
            className="bg-primary text-on-primary-fixed hover:bg-opacity-95 px-5 py-2.5 rounded-xl font-label-md text-xs flex items-center gap-2 font-semibold shadow-lg shadow-primary/10 transition-all active:scale-95 cursor-pointer"
          >
            <Save size={14} />
            Сохранить изменения
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-lg items-start">
        {/* Left Column: Primary User Cards */}
        <div className="lg:col-span-4 space-y-lg">
          
          {/* Identification card */}
          <section className="glass-card rounded-2xl p-lg space-y-md border border-white/5">
            <div className="flex items-center gap-2.5 pb-2 border-b border-white/5">
              <Fingerprint className="text-primary" size={20} />
              <h3 className="font-semibold text-headline-sm text-on-surface">Идентификация</h3>
            </div>
            
            <div className="space-y-3 font-body-md text-sm">
              <div className="flex justify-between items-center">
                <span className="text-on-surface-variant text-xs">Telegram ID</span>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-on-surface font-semibold bg-white/5 px-2 py-0.5 rounded select-all cursor-pointer" onClick={handleCopyId}>
                    {user.id}
                  </span>
                  <button 
                    onClick={handleCopyId}
                    className="text-primary hover:text-white transition-colors text-[10px]"
                  >
                    {copiedId ? 'Скопировано!' : 'Копировать'}
                  </button>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-on-surface-variant text-xs">Username</span>
                <span className="text-primary font-semibold">{user.username}</span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-on-surface-variant text-xs">Язык интерфейса</span>
                <span className="bg-surface-container-highest text-on-surface px-2 py-0.5 rounded font-mono text-xs">RU</span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-on-surface-variant text-xs">Был в сети</span>
                <span className="text-on-surface font-mono text-xs font-semibold">{user.lastActive}</span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-on-surface-variant text-xs">Дата регистрации</span>
                <span className="text-on-surface font-mono text-xs">{user.registeredDate}</span>
              </div>
            </div>
          </section>

          {/* Profile details editable card */}
          <section className="glass-card rounded-2xl p-lg space-y-md border border-white/5">
            <div className="flex items-center gap-2.5 pb-2 border-b border-white/5">
              <UserIcon className="text-primary" size={20} />
              <h3 className="font-semibold text-headline-sm text-on-surface">Профиль участника</h3>
            </div>

            <div className="space-y-md">
              <div className="space-y-1">
                <label className="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Полное имя</label>
                <div className="relative">
                  <span className="absolute left-3 top-2.5 text-on-surface-variant/50"><UserIcon size={14} /></span>
                  <input 
                    type="text" 
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full bg-surface-container-low border border-white/10 rounded-xl py-2 pl-9 pr-3 text-sm focus:ring-1 focus:ring-primary focus:border-transparent outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-md">
                <div className="space-y-1">
                  <label className="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Телефон</label>
                  <div className="relative">
                    <span className="absolute left-3 top-2.5 text-on-surface-variant/50"><Smartphone size={14} /></span>
                    <input 
                      type="text" 
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="w-full text-xs bg-surface-container-low border border-white/10 rounded-xl py-2 pl-8 pr-2 focus:ring-1 focus:ring-primary focus:border-transparent outline-none"
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Город</label>
                  <div className="relative">
                    <span className="absolute left-3 top-2.5 text-on-surface-variant/50"><MapPin size={14} /></span>
                    <input 
                      type="text" 
                      value={city || ''}
                      onChange={(e) => setCity(e.target.value)}
                      className="w-full text-xs bg-surface-container-low border border-white/10 rounded-xl py-2 pl-8 pr-2 focus:ring-1 focus:ring-primary focus:border-transparent outline-none"
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Электронная почта</label>
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-surface-container-low border border-white/10 rounded-xl py-2 px-3 text-xs focus:ring-1 focus:ring-primary focus:border-transparent outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-md">
                <div className="space-y-1">
                  <label className="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Часовой пояс</label>
                  <input 
                    type="text" 
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="w-full bg-surface-container-low border border-white/10 rounded-xl py-2 px-3 text-xs focus:ring-1 focus:ring-primary focus:border-transparent outline-none font-mono"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Дата рождения</label>
                  <div className="relative">
                    <span className="absolute left-3 top-2.5 text-on-surface-variant/50"><Calendar size={12} /></span>
                    <input 
                      type="text" 
                      value={birthDate}
                      onChange={(e) => setBirthDate(e.target.value)}
                      className="w-full text-xs bg-surface-container-low border border-white/10 rounded-xl py-2 pl-8 pr-2 focus:ring-1 focus:ring-primary"
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-1 pt-2">
                <label className="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Сегмент / Статус доступа</label>
                <select 
                  value={status}
                  onChange={(e) => setStatus(e.target.value as User['status'])}
                  className="w-full bg-surface-container-low border border-white/10 rounded-xl py-2 px-3 text-xs focus:ring-1 focus:ring-primary focus:border-transparent outline-none cursor-pointer"
                >
                  <option value="В ядре">В ядре (Core)</option>
                  <option value="Не в ядре">Не в ядре</option>
                  <option value="Guest">Guest</option>
                  <option value="External">External</option>
                </select>
              </div>

              <div className="space-y-1.5 pt-2">
                <label className="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">Заметка админа</label>
                <textarea 
                  value={adminNotes}
                  onChange={(e) => setAdminNotes(e.target.value)}
                  className="w-full bg-surface-container-lowest border border-white/10 rounded-xl p-3 text-xs focus:ring-1 focus:ring-primary outline-none min-h-[100px] resize-none"
                  placeholder="Добавьте важную информацию о пользователе..."
                />
              </div>
            </div>
          </section>
        </div>

        {/* Right Column: UTM marketing statistics & checklist audits */}
        <div className="lg:col-span-8 space-y-lg">
          
          {/* UTM marketing stats row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-md">
            <section className="glass-card rounded-2xl p-md border border-white/5 relative overflow-hidden flex flex-col justify-between">
              <div className="flex items-center gap-2 mb-2 text-on-surface-variant/70">
                <Tag size={14} className="text-primary" />
                <span className="font-label-md text-xs">Источник (UTM)</span>
              </div>
              <div className="font-semibold text-lg text-primary truncate">
                {user.utmSource || "Yandex_Direct_Scale"}
              </div>
              <div className="text-[11px] text-on-surface-variant font-mono mt-1">
                Campaign: {user.utmCampaign || "spring_promo"}
              </div>
            </section>

            <section className="glass-card rounded-2xl p-md border border-white/5 relative overflow-hidden flex flex-col justify-between">
              <div className="flex items-center gap-1.5 mb-2 text-on-surface-variant/70">
                <Network size={14} className="text-secondary" />
                <span className="font-label-md text-xs">Текущая ветка</span>
              </div>
              <div className="font-semibold text-lg text-on-surface truncate">
                {user.currentBranch || "Core_Application_V2"}
              </div>
              <div className="text-[11px] text-on-surface-variant mt-1 font-semibold text-secondary flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-secondary"></span>
                {user.currentStep || "Шаг 4: Мотивация"}
              </div>
            </section>

            <section className="glass-card rounded-2xl p-md border border-white/5 flex flex-col justify-between">
              <div className="flex items-center justify-between pointer-events-none">
                <div className="flex items-center gap-1.5 text-on-surface-variant/70">
                  <ToggleLeft size={14} className={channelSubscribed ? 'text-secondary' : 'text-on-surface-variant'} />
                  <span className="font-label-md text-xs">Подписка на канал</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between mt-2">
                <span className={`font-semibold text-lg ${channelSubscribed ? "text-secondary" : "text-on-surface-variant"}`}>
                  {channelSubscribed ? "Да" : "Нет"}
                </span>
                
                {/* Simulated dynamic switcher */}
                <button 
                  onClick={() => setChannelSubscribed(!channelSubscribed)}
                  className={`w-9 h-5 rounded-full relative p-0.5 transition-colors cursor-pointer ${
                    channelSubscribed ? 'bg-secondary' : 'bg-surface-container-highest'
                  }`}
                >
                  <div className={`w-4 h-4 bg-white rounded-full shadow transition-all ${
                    channelSubscribed ? 'translate-x-[16px]' : 'translate-x-0'
                  }`} />
                </button>
              </div>
              <div className="text-[11px] text-on-surface-variant font-mono mt-1">
                Дата проверки: сегодня
              </div>
            </section>
          </div>

          {/* Bot statuses row */}
          <section className="glass-card rounded-2xl p-lg border border-white/5">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-lg text-center sm:text-left">
              <div className="space-y-1">
                <div className="text-on-surface-variant font-label-md text-xs uppercase tracking-wider">Методичка</div>
                <div className="flex items-center gap-2 justify-center sm:justify-start">
                  <button 
                    onClick={() => setBookletReceived(!bookletReceived)}
                    className="focus:outline-none cursor-pointer"
                  >
                    {bookletReceived ? (
                      <span className="material-symbols-outlined text-secondary font-bold text-[22px]">check_circle</span>
                    ) : (
                      <span className="material-symbols-outlined text-on-surface-variant/40 text-[22px]">pending</span>
                    )}
                  </button>
                  <span className="font-semibold text-headline-sm">
                    {bookletReceived ? "Получена" : "Ожидает"}
                  </span>
                </div>
                <p className="text-[11px] text-on-surface-variant">
                  {bookletReceived ? "Выдана 13.03.2024 в 14:20" : "Линк отправлен в бот"}
                </p>
              </div>

              <div className="border-t sm:border-t-0 sm:border-l border-white/5 pt-lg sm:pt-0 sm:pl-lg space-y-1">
                <div className="text-on-surface-variant font-label-md text-xs uppercase tracking-wider">Анкета Ядра</div>
                <div className="flex items-center gap-2 justify-center sm:justify-start text-primary">
                  <span className="material-symbols-outlined text-[22px]">pending</span>
                  <span className="font-semibold text-headline-sm text-primary">В процессе</span>
                </div>
                <p className="text-[11px] text-on-surface-variant">Обновлено 2 часа назад</p>
              </div>

              <div className="border-t sm:border-t-0 sm:border-l border-white/5 pt-lg sm:pt-0 sm:pl-lg space-y-1">
                <div className="text-on-surface-variant font-label-md text-xs uppercase tracking-wider">Отзывы & Согласие</div>
                <div className="flex items-center gap-2 justify-center sm:justify-start">
                  <span className="material-symbols-outlined text-secondary text-[22px] font-bold">check_circle</span>
                  <span className="font-semibold text-headline-sm">Согласен / Ок</span>
                </div>
                <p className="text-[11px] text-on-surface-variant">IP лог: 192.168.1.5</p>
              </div>
            </div>
          </section>

          {/* Diagnostics list */}
          <section className="glass-card rounded-2xl p-lg border border-white/5">
            <div className="flex items-center justify-between mb-lg border-b border-white/5 pb-2">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[22px]" style={{ fontVariationSettings: "'FILL' 1" }}>query_stats</span>
                <h3 className="font-semibold text-headline-sm text-on-surface">Результаты диагностик</h3>
              </div>
              
              <div className="flex gap-md font-mono">
                <div className="flex flex-col items-end">
                  <span className="text-[11px] text-on-surface-variant">Пройдено</span>
                  <span className="text-sm font-bold text-primary">
                    {user.diagnostics?.filter(d => d.status === 'Готово').length || 0}
                  </span>
                </div>
                <div className="w-[1px] h-8 bg-white/10" />
                <div className="flex flex-col items-end">
                  <span className="text-[11px] text-on-surface-variant font-semibold text-secondary">Всего</span>
                  <span className="text-sm font-bold text-secondary">
                    {user.diagnostics?.length || 0}
                  </span>
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="text-on-surface-variant font-label-md text-xs border-b border-white/5">
                  <tr>
                    <th className="pb-2 font-medium">Код</th>
                    <th className="pb-2 font-medium">Диагностика</th>
                    <th className="pb-2 font-medium">Статус опроса</th>
                    <th className="pb-2 font-medium">Дата завершения</th>
                    <th className="pb-2 font-medium text-right">Материалы респондента</th>
                  </tr>
                </thead>
                <tbody className="font-body-md text-xs text-on-surface divide-y divide-white/5">
                  {user.diagnostics && user.diagnostics.length > 0 ? (
                    user.diagnostics.map((diag) => (
                      <tr key={diag.id} className="hover:bg-white/2 transition-colors">
                        <td className="py-3 font-mono font-semibold text-primary">{diag.id}</td>
                        <td className="py-3 font-semibold">{diag.name}</td>
                        <td className="py-3">
                          {diag.status === 'Готово' ? (
                            <span className="text-secondary flex items-center gap-1 font-semibold">
                              <span className="w-1.5 h-1.5 bg-secondary rounded-full animate-pulse"></span>
                              Готово
                            </span>
                          ) : (
                            <span className="text-on-surface-variant/60">Прервано</span>
                          )}
                        </td>
                        <td className="py-3 text-on-surface-variant font-mono">{diag.date}</td>
                        <td className="py-3 text-right">
                          <div className="flex justify-end gap-2">
                            <button 
                              disabled={!diag.files.mic}
                              className={`p-1.5 rounded-lg transition-colors ${
                                diag.files.mic 
                                  ? 'text-primary hover:bg-primary/10' 
                                  : 'text-on-surface-variant/20 cursor-not-allowed'
                              }`}
                              title={diag.files.mic ? "Прослушать голосовой ответ" : "Голосовой ответ отсутствует"}
                            >
                              <Mic size={14} />
                            </button>
                            <button 
                              disabled={!diag.files.description}
                              className={`p-1.5 rounded-lg transition-colors ${
                                diag.files.description 
                                  ? 'text-primary hover:bg-primary/10' 
                                  : 'text-on-surface-variant/20 cursor-not-allowed'
                              }`}
                              title={diag.files.description ? "Скачать PDF отчет" : "Отчет не сгенерирован"}
                            >
                              <FileText size={14} />
                            </button>
                            <button 
                              disabled={!diag.files.text_snippet}
                              className={`p-1.5 rounded-lg transition-colors ${
                                diag.files.text_snippet 
                                  ? 'text-primary hover:bg-primary/10' 
                                  : 'text-on-surface-variant/20 cursor-not-allowed'
                              }`}
                              title={diag.files.text_snippet ? "Посмотреть транскрибацию" : "Транскрипт отсутствует"}
                            >
                              <FileSpreadsheet size={14} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} className="py-6 text-center text-on-surface-variant/60">
                        Пользователь еще не запускал психологические диагностики в боте PML.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Expandable Core Questionnaire Applications detail */}
          <section className="space-y-sm">
            <div className="flex items-center gap-1.5 px-1">
              <span className="material-symbols-outlined text-primary text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>assignment</span>
              <h3 className="font-semibold text-headline-sm text-on-surface">Анкеты Ядра (Core)</h3>
            </div>

            {user.coreApplications && user.coreApplications.length > 0 ? (
              user.coreApplications.map((app) => (
                <div 
                  key={app.id} 
                  className={`glass-card rounded-2xl overflow-hidden border border-white/5 transition-all ${
                    app.isActual ? 'border-l-4 border-l-primary' : 'border-l-4 border-l-white/10'
                  }`}
                >
                  {/* Accordion Trigger */}
                  <div 
                    onClick={() => setIsAccordionOpen(!isAccordionOpen)}
                    className="p-lg bg-primary/2 hover:bg-primary/5 cursor-pointer flex justify-between items-center group transition-colors"
                  >
                    <div>
                      <h4 className="font-bold text-headline-sm text-primary mb-0.5 flex items-center gap-2">
                        {app.id} 
                        {app.isActual ? (
                          <span className="text-[10px] bg-primary/20 text-primary uppercase font-bold px-2 py-0.5 rounded tracking-wide">Актуальная</span>
                        ) : (
                          <span className="text-[10px] bg-white/5 text-on-surface-variant uppercase font-bold px-2.5 py-0.5 rounded tracking-wide">Архив</span>
                        )}
                      </h4>
                      <p className="text-xs text-on-surface-variant">Подана {app.date}</p>
                    </div>
                    
                    <motion.div
                      animate={{ rotate: isAccordionOpen ? 180 : 0 }}
                      className="text-primary"
                    >
                      <ChevronDown size={20} />
                    </motion.div>
                  </div>

                  {/* Accordion Body */}
                  <AnimatePresence initial={false}>
                    {isAccordionOpen && (
                      <motion.div 
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden border-t border-white/5"
                      >
                        <div className="p-lg space-y-md font-body-md text-xs">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
                            <div className="space-y-md">
                              <div>
                                <label className="block text-on-surface-variant text-[10px] font-semibold uppercase tracking-wider mb-2">Деятельность</label>
                                <p className="bg-surface-container p-3 rounded-xl border border-white/5 text-on-surface">
                                  {app.activity}
                                </p>
                              </div>

                              <div>
                                <label className="block text-on-surface-variant text-[10px] font-semibold uppercase tracking-wider mb-2">Глубинный Запрос</label>
                                <p className="bg-surface-container p-3 rounded-xl border border-white/5 text-on-surface">
                                  {app.request}
                                </p>
                              </div>

                              <div>
                                <label className="block text-on-surface-variant text-[10px] font-semibold uppercase tracking-wider mb-2">Приоритеты масштабирования</label>
                                <div className="flex flex-wrap gap-1.5 mt-1">
                                  {app.priorities.map((item, idx) => (
                                    <span 
                                      key={idx} 
                                      className="bg-primary-container/20 text-on-primary-container px-3 py-1 rounded-full border border-primary/20 hover:bg-primary/20 transition-all font-semibold"
                                    >
                                      {item}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            </div>

                            <div className="space-y-md">
                              <div className="grid grid-cols-2 gap-md">
                                <div className="bg-surface-container p-3 rounded-xl border border-white/5 text-center">
                                  <span className="text-[10px] font-semibold text-on-surface-variant block mb-1 uppercase tracking-wider">Готовность к изменениям</span>
                                  <span className="font-bold text-headline-sm text-secondary">{app.readiness}</span>
                                </div>
                                <div className="bg-surface-container p-3 rounded-xl border border-white/5 text-center">
                                  <span className="text-[10px] font-semibold text-on-surface-variant block mb-1 uppercase tracking-wider">Время в неделю</span>
                                  <span className="font-bold text-headline-sm text-on-surface">{app.weeklyHours}</span>
                                </div>
                              </div>

                              <div>
                                <label className="block text-on-surface-variant text-[10px] font-semibold uppercase tracking-wider mb-2">Трудности</label>
                                <p className="text-on-surface italic p-3 bg-surface-container rounded-xl border border-white/5">
                                  &ldquo;{app.difficulties}&rdquo;
                                </p>
                              </div>

                              <div className="flex items-center justify-between p-3 bg-surface-container rounded-xl border border-white/5 font-semibold">
                                <span className="text-on-surface">Статус оплаты участия</span>
                                {app.isPaid ? (
                                  <span className="bg-secondary text-on-secondary px-3 py-1 rounded-full text-[10px] tracking-wide font-black">
                                    ОПЛАЧЕНО
                                  </span>
                                ) : (
                                  <span className="bg-error text-on-error px-3 py-1 rounded-full text-[10px] tracking-wide font-black">
                                    НЕ ОПЛАЧЕНО
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ))
            ) : (
              <div className="glass-card rounded-2xl p-lg text-center text-on-surface-variant/60 border border-white/5">
                Анкета отбора в Ядро группы еще не заполнена пользователем.
              </div>
            )}
          </section>

          {/* Analysis timeline session registrations */}
          <section className="glass-card rounded-2xl p-lg border border-white/5">
            <div className="flex items-center gap-2 mb-lg border-b border-white/5 pb-2">
              <History className="text-primary animate-spin" style={{ animationDuration: '6s' }} size={20} />
              <h3 className="font-semibold text-headline-sm text-on-surface">Регистрация на разборы</h3>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-md font-mono">
              {user.analysisDates && user.analysisDates.length > 0 ? (
                user.analysisDates.map((dateStr, idx) => {
                  const [date, time] = dateStr.split(' ');
                  const isOld = idx > 1; // simulation of past vs present status
                  return (
                    <div 
                      key={idx} 
                      className={`p-2 rounded-xl text-center border transition-all ${
                        isOld 
                          ? 'bg-surface-container-highest border-white/5 opacity-40' 
                          : 'bg-primary/5 border-primary/20 text-on-surface hover:shadow-lg hover:shadow-primary/5'
                      }`}
                    >
                      <span className="text-[10px] text-on-surface-variant block font-semibold">{date}</span>
                      <span className="text-xs font-bold block mt-1">{time}</span>
                    </div>
                  );
                })
              ) : (
                <p className="text-xs text-on-surface-variant col-span-full py-2">
                  Нет запланированных сессий разбора.
                </p>
              )}
            </div>
          </section>

        </div>
      </div>
    </div>
  );
}
