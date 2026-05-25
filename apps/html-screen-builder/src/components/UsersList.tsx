import React, { useState } from 'react';
import { User } from '../types';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Users, 
  Search, 
  Filter, 
  TrendingUp, 
  HelpCircle,
  Plus, 
  ChevronRight, 
  ChevronLeft, 
  UserPlus, 
  CheckCircle2, 
  Clock, 
  MoreVertical,
  X,
  Sparkles,
  Award
} from 'lucide-react';

interface UsersListProps {
  users: User[];
  onSelectUser: (user: User) => void;
  onAddUser: (user: User) => void;
}

export default function UsersList({ users, onSelectUser, onAddUser }: UsersListProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'Все' | 'В ядре' | 'Не в ядре' | 'Guest' | 'External'>('Все');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;

  // New User Form State
  const [newUser, setNewUser] = useState({
    username: '',
    fullName: '',
    status: 'Не в ядре' as User['status'],
    phone: '',
    city: '',
    email: '',
    adminNotes: ''
  });

  // Calculate stats from dynamic users array
  const totalRawCount = 12412 + users.length; // baseline simulator
  const activeToday = 1198 + Math.floor(users.length * 0.4);
  const coreCount = users.filter(u => u.status === 'В ядре').length;
  const newCount = 82 + users.length;

  // Filter users
  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.id.includes(searchTerm);
    
    if (statusFilter === 'Все') {
      return matchesSearch;
    }
    return matchesSearch && user.status === statusFilter;
  });

  // Pagination helper
  const totalPages = Math.ceil(filteredUsers.length / itemsPerPage);
  const paginatedUsers = filteredUsers.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUser.fullName || !newUser.username) {
      alert("Пожалуйста, заполните Полное имя и Username!");
      return;
    }

    const randomID = Math.floor(10000000 + Math.random() * 90000000).toString();
    const created: User = {
      id: randomID,
      username: newUser.username.startsWith('@') ? newUser.username : `@${newUser.username}`,
      fullName: newUser.fullName,
      status: newUser.status,
      lastActive: "Today, " + new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }),
      activityText: "Только что",
      phone: newUser.phone || "+7 (995) 000-00-00",
      city: newUser.city || "Москва",
      email: newUser.email || "user@example.com",
      timezone: "GMT+3",
      birthDate: "01.01.1995",
      adminNotes: newUser.adminNotes || "Добавлен вручную администратором.",
      registeredDate: new Date().toLocaleDateString('ru-RU'),
      channelSubscribed: true,
      bookletReceived: false,
      coreFormStatus: "Не начата",
      consentApproved: true,
      diagnostics: [],
      coreApplications: [],
      analysisDates: []
    };

    onAddUser(created);
    setIsAddModalOpen(false);
    // Reset form
    setNewUser({
      username: '',
      fullName: '',
      status: 'Не в ядре',
      phone: '',
      city: '',
      email: '',
      adminNotes: ''
    });
  };

  return (
    <div className="space-y-lg">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-md">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-[#dce2f3] flex items-center gap-2">
            Управление пользователями
          </h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Мониторинг активности, сегментация аудитории и детальный анализ психологических диагностик ПМЛ.
          </p>
        </div>
        <motion.button 
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setIsAddModalOpen(true)}
          className="bg-primary text-on-primary-fixed hover:bg-opacity-95 px-6 py-2.5 rounded-full font-label-md font-semibold flex items-center gap-2 shadow-lg shadow-primary/15 self-start md:self-auto cursor-pointer"
        >
          <span className="material-symbols-outlined text-[20px] font-bold">person_add</span>
          Добавить вручную
        </motion.button>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-md">
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="glass-card p-md rounded-2xl border border-white/5 space-y-2 flex flex-col justify-between"
        >
          <span className="font-label-md text-on-surface-variant uppercase tracking-wider text-[11px]">Всего пользователей</span>
          <div className="text-2xl font-bold text-primary">{totalRawCount.toLocaleString('ru-RU')}</div>
          <div className="flex items-center gap-1 text-secondary text-label-sm">
            <TrendingUp size={12} />
            <span>+5% за неделю</span>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.05 }}
          className="glass-card p-md rounded-2xl border border-white/5 space-y-2 flex flex-col justify-between"
        >
          <span className="font-label-md text-on-surface-variant uppercase tracking-wider text-[11px]">В ядре группы</span>
          <div className="text-2xl font-bold text-secondary">{428 + coreCount}</div>
          <div className="flex items-center gap-1 text-secondary text-label-sm">
            <CheckCircle2 size={12} className="text-secondary" />
            <span>Стабильный рост</span>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="glass-card p-md rounded-2xl border border-white/5 space-y-2 flex flex-col justify-between"
        >
          <span className="font-label-md text-on-surface-variant uppercase tracking-wider text-[11px]">Активны сегодня</span>
          <div className="text-2xl font-bold text-on-surface">{activeToday.toLocaleString('ru-RU')}</div>
          <div className="flex items-center gap-1 text-on-surface-variant text-label-sm">
            <Clock size={12} />
            <span>Пик: 14:00</span>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.15 }}
          className="glass-card p-md rounded-2xl border border-white/5 space-y-2 flex flex-col justify-between"
        >
          <span className="font-label-md text-on-surface-variant uppercase tracking-wider text-[11px]">Новых (24ч)</span>
          <div className="text-2xl font-bold text-tertiary">{newCount}</div>
          <div className="flex items-center gap-1 text-error text-label-sm">
            <TrendingUp size={12} className="rotate-180 text-error" />
            <span>-2% vs вчер.</span>
          </div>
        </motion.div>
      </div>

      {/* Search & filters row */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-md">
        <div className="md:col-span-7 relative">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant">
            <Search size={18} />
          </span>
          <input 
            className="w-full bg-surface-container border border-white/10 rounded-xl py-3 pl-12 pr-4 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all font-body-md text-on-surface placeholder:text-on-surface-variant/40" 
            placeholder="Поиск по username, имени или ID..." 
            type="text"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
          />
        </div>
        <div className="md:col-span-5 flex p-1 bg-surface-container rounded-xl gap-1 border border-white/5">
          {(['Все', 'В ядре', 'Не в ядре', 'Guest', 'External'] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => {
                setStatusFilter(filter);
                setCurrentPage(1);
              }}
              className={`flex-1 py-2 px-1 rounded-lg text-center font-label-md text-[11px] lg:text-[12px] transition-all cursor-pointer ${
                statusFilter === filter
                  ? 'bg-primary-container text-on-primary-container shadow-sm font-semibold'
                  : 'text-on-surface-variant hover:bg-surface-container-highest hover:text-on-surface'
              }`}
            >
              {filter}
            </button>
          ))}
        </div>
      </div>

      {/* Main Table for Desktops / Responsive Desktop List */}
      <div className="bg-surface-container rounded-3xl border border-white/5 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/5 bg-white/2">
                <th className="px-6 py-4 font-label-md text-on-surface-variant text-[11px] uppercase tracking-wider">Username / ID</th>
                <th className="px-6 py-4 font-label-md text-on-surface-variant text-[11px] uppercase tracking-wider">Полное имя</th>
                <th className="px-6 py-4 font-label-md text-on-surface-variant text-[11px] uppercase tracking-wider">Статус</th>
                <th className="px-6 py-4 font-label-md text-on-surface-variant text-[11px] uppercase tracking-wider">Последний вход</th>
                <th className="px-6 py-4 font-label-md text-on-surface-variant text-[11px] uppercase tracking-wider">Активность в боте</th>
                <th className="px-6 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 font-body-md text-on-surface">
              <AnimatePresence mode="popLayout">
                {paginatedUsers.length > 0 ? (
                  paginatedUsers.map((user) => (
                    <motion.tr 
                      key={user.id}
                      layout
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      onClick={() => onSelectUser(user)}
                      className="hover:bg-white/5 transition-all group cursor-pointer duration-150 relative"
                    >
                      <td className="px-6 py-5">
                        <div className="flex flex-col">
                          <span className="font-semibold text-primary group-hover:text-amber-200 transition-colors">
                            {user.username}
                          </span>
                          <span className="text-[11px] text-on-surface-variant font-mono">
                            {user.id}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-5 font-semibold text-on-surface">{user.fullName}</td>
                      <td className="px-6 py-5">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${
                          user.status === 'В ядре' 
                            ? 'bg-secondary/10 text-secondary border-secondary/20' 
                            : user.status === 'Не в ядре' 
                            ? 'bg-on-surface-variant/10 text-on-surface-variant border-on-surface-variant/20'
                            : user.status === 'Guest'
                            ? 'bg-amber-400/10 text-amber-200 border-amber-400/20'
                            : 'bg-indigo-400/10 text-indigo-200 border-indigo-400/20'
                        }`}>
                          {user.status}
                        </span>
                      </td>
                      <td className="px-6 py-5 text-on-surface-variant/80 text-xs font-mono">{user.lastActive}</td>
                      <td className="px-6 py-5">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container-highest text-xs">
                          {user.status === 'В ядре' && <span className="w-1.5 h-1.5 rounded-full bg-secondary"></span>}
                          {user.activityText}
                        </span>
                      </td>
                      <td className="px-6 py-5 text-right">
                        <motion.button 
                          whileHover={{ scale: 1.1 }}
                          className="text-on-surface-variant hover:text-primary transition-colors p-1 rounded-lg hover:bg-white/5"
                        >
                          <ChevronRight size={18} />
                        </motion.button>
                      </td>
                    </motion.tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-on-surface-variant/60">
                      Пользователи не найдены. Попробуйте изменить параметры поиска или фильтров.
                    </td>
                  </tr>
                )}
              </AnimatePresence>
            </tbody>
          </table>
        </div>

        {/* Pagination bar */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-white/5 flex items-center justify-between bg-white/2">
            <span className="text-xs text-on-surface-variant">
              Показано {(currentPage - 1) * itemsPerPage + 1}–{Math.min(currentPage * itemsPerPage, filteredUsers.length)} из {filteredUsers.length}
            </span>
            <div className="flex items-center gap-1">
              <button 
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="p-1.5 rounded-lg hover:bg-white/5 text-on-surface-variant disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft size={16} />
              </button>
              
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((idx) => (
                <button
                  key={idx}
                  onClick={() => handlePageChange(idx)}
                  className={`px-3 py-1 rounded-lg font-label-md text-xs transition-all ${
                    currentPage === idx
                      ? 'bg-primary/20 text-primary font-bold'
                      : 'hover:bg-white/5 text-on-surface-variant'
                  }`}
                >
                  {idx}
                </button>
              ))}

              <button 
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="p-1.5 rounded-lg hover:bg-white/5 text-on-surface-variant disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Manual Addition Modal */}
      <AnimatePresence>
        {isAddModalOpen && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-md bg-black/60 backdrop-blur-sm">
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="glass-card w-full max-w-lg rounded-3xl border border-white/15 overflow-hidden shadow-2xl z-50 flex flex-col max-h-[90vh]"
            >
              {/* Modal header */}
              <div className="px-lg py-md border-b border-white/5 flex items-center justify-between bg-white/2">
                <div className="flex items-center gap-2">
                  <UserPlus className="text-primary" size={20} />
                  <h3 className="font-headline-sm text-lg font-bold">Добавить пользователя в БД</h3>
                </div>
                <button 
                  onClick={() => setIsAddModalOpen(false)}
                  className="p-1 hover:bg-white/10 rounded-full transition-colors"
                >
                  <X size={18} />
                </button>
              </div>

              {/* Modal form */}
              <form onSubmit={handleFormSubmit} className="p-lg space-y-md overflow-y-auto flex-1 custom-scrollbar">
                <div className="space-y-sm">
                  <label className="text-xs text-on-surface-variant uppercase tracking-wider block font-medium">Username в Telegram *</label>
                  <input 
                    required
                    type="text" 
                    placeholder="@username (например @alex)"
                    value={newUser.username}
                    onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                    className="w-full bg-surface-container-low border border-white/10 rounded-xl px-4 py-2.5 text-body-md text-on-surface focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                  />
                </div>

                <div className="space-y-sm">
                  <label className="text-xs text-on-surface-variant uppercase tracking-wider block font-medium">Полное имя *</label>
                  <input 
                    required
                    type="text" 
                    placeholder="Иван Иванов"
                    value={newUser.fullName}
                    onChange={(e) => setNewUser({...newUser, fullName: e.target.value})}
                    className="w-full bg-surface-container-low border border-white/10 rounded-xl px-4 py-2.5 text-body-md text-on-surface focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-md">
                  <div className="space-y-sm">
                    <label className="text-xs text-on-surface-variant uppercase tracking-wider block font-medium">Телефон</label>
                    <input 
                      type="text" 
                      placeholder="+7 999 123-45-67"
                      value={newUser.phone}
                      onChange={(e) => setNewUser({...newUser, phone: e.target.value})}
                      className="w-full bg-surface-container-low border border-white/10 rounded-xl px-4 py-2.5 text-body-md text-on-surface focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                    />
                  </div>
                  <div className="space-y-sm">
                    <label className="text-xs text-on-surface-variant uppercase tracking-wider block font-medium">Город</label>
                    <input 
                      type="text" 
                      placeholder="Москва"
                      value={newUser.city}
                      onChange={(e) => setNewUser({...newUser, city: e.target.value})}
                      className="w-full bg-surface-container-low border border-white/10 rounded-xl px-4 py-2.5 text-body-md text-on-surface focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-md">
                  <div className="space-y-sm">
                    <label className="text-xs text-on-surface-variant uppercase tracking-wider block font-medium">Email</label>
                    <input 
                      type="email" 
                      placeholder="user@example.com"
                      value={newUser.email}
                      onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                      className="w-full bg-surface-container-low border border-white/10 rounded-xl px-4 py-2.5 text-body-md text-on-surface focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                    />
                  </div>
                  <div className="space-y-sm">
                    <label className="text-xs text-on-surface-variant uppercase tracking-wider block font-medium">Группа / Сегмент</label>
                    <select 
                      value={newUser.status}
                      onChange={(e) => setNewUser({...newUser, status: e.target.value as User['status']})}
                      className="w-full bg-surface-container-low border border-white/10 rounded-xl px-4 py-2.5 text-body-md text-on-surface focus:ring-2 focus:ring-primary focus:border-transparent outline-none cursor-pointer"
                    >
                      <option value="В ядре">В ядре (Core)</option>
                      <option value="Не в ядре">Не в ядре</option>
                      <option value="Guest">Guest</option>
                      <option value="External">External</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-sm">
                  <label className="text-xs text-on-surface-variant uppercase tracking-wider block font-medium">Заметка администратора</label>
                  <textarea 
                    rows={3}
                    placeholder="Добавьте важную информацию о пользователе..."
                    value={newUser.adminNotes}
                    onChange={(e) => setNewUser({...newUser, adminNotes: e.target.value})}
                    className="w-full bg-surface-container-low border border-white/10 rounded-xl p-4 text-body-md text-on-surface focus:ring-2 focus:ring-primary focus:border-transparent outline-none resize-none"
                  />
                </div>

                <div className="flex gap-md pt-3">
                  <button 
                    type="button"
                    onClick={() => setIsAddModalOpen(false)}
                    className="flex-1 border border-white/10 bg-surface-container-low text-on-surface py-2.5 rounded-xl hover:bg-surface-container-highest cursor-pointer font-semibold"
                  >
                    Отмена
                  </button>
                  <button 
                    type="submit"
                    className="flex-1 bg-primary text-on-primary-fixed py-2.5 rounded-xl hover:bg-opacity-95 font-semibold cursor-pointer shadow-lg shadow-primary/10"
                  >
                    Сохранить
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
