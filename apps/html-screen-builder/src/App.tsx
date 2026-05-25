import React, { useState, useEffect } from 'react';
import { INITIAL_USERS, INITIAL_BROADCASTS } from './data';
import { User, Broadcast } from './types';
import UsersList from './components/UsersList';
import UserDetail from './components/UserDetail';
import Broadcasts from './components/Broadcasts';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Users, 
  Send, 
  Layout, 
  ShieldCheck, 
  Clock, 
  Database,
  ArrowRightLeft,
  ChevronRight,
  TrendingUp,
  Sliders,
  LogOut,
  AppWindow,
  FileBadge
} from 'lucide-react';

export default function App() {
  const [users, setUsers] = useState<User[]>(INITIAL_USERS);
  const [broadcasts, setBroadcasts] = useState<Broadcast[]>(INITIAL_BROADCASTS);
  const [selectedTab, setSelectedTab] = useState<'users' | 'broadcasts'>('users');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [currentTime, setCurrentTime] = useState('');

  // Continuous Clock ticks in GMT+3 (Moscow)
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      // Format as Moscow Time (GMT+3)
      const options: Intl.DateTimeFormatOptions = {
        timeZone: 'Europe/Moscow',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      };
      setCurrentTime(now.toLocaleTimeString('ru-RU', options));
    };
    
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Update specific user details
  const handleUpdateUser = (updatedUser: User) => {
    setUsers(prev => prev.map(u => u.id === updatedUser.id ? updatedUser : u));
    setSelectedUser(updatedUser);
  };

  // Add manually created user
  const handleAddUser = (newUser: User) => {
    setUsers(prev => [newUser, ...prev]);
  };

  // Append composed broadcasts
  const handleAddBroadcast = (newBc: Broadcast) => {
    setBroadcasts(prev => [newBc, ...prev]);
  };

  // Delete broadcast item
  const handleDeleteBroadcast = (id: string) => {
    setBroadcasts(prev => prev.filter(bc => bc.id !== id));
  };

  return (
    <div className="flex h-screen w-full bg-[#0c141f] text-[#dce2f3] overflow-hidden font-sans select-none">
      
      {/* Sidebar Navigation */}
      <aside className="hidden lg:flex flex-col w-72 bg-[#090e15] border-r border-white/5 flex-shrink-0 z-20">
        
        {/* Core logotype & Brand identifier */}
        <div className="p-lg border-b border-white/5 space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-secondary flex items-center justify-center font-black text-on-primary-fixed select-none text-sm shadow-md shadow-primary/20">
              П
            </div>
            <div>
              <h1 className="font-bold text-headline-sm text-sm tracking-wide text-on-surface uppercase pr-1">
                Психология Масштаба
              </h1>
              <span className="text-[10px] font-bold text-primary tracking-widest block uppercase">
                Админ-Консоль PML
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-1.5 pt-1">
            <span className="inline-flex w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
            <span className="text-[10px] text-on-surface-variant font-mono font-bold uppercase tracking-wider">
              Сервер: Активен (Port 3000)
            </span>
          </div>
        </div>

        {/* Tab links section */}
        <nav className="p-md flex-1 space-y-1.5 overflow-y-auto">
          <button
            onClick={() => {
              setSelectedTab('users');
              setSelectedUser(null);
            }}
            className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all cursor-pointer ${
              selectedTab === 'users' && !selectedUser
                ? 'bg-primary-container text-on-primary-container font-semibold shadow-sm'
                : 'text-on-surface-variant hover:bg-white/5 hover:text-on-surface'
            }`}
          >
            <div className="flex items-center gap-3">
              <Users size={18} className={selectedTab === 'users' ? 'text-primary' : 'text-on-surface-variant'} />
              <span className="text-sm font-label-md">Пользователи бота</span>
            </div>
            <span className="text-[10px] font-semibold font-mono bg-white/5 px-2 py-0.5 rounded-full text-on-surface-variant">
              {users.length}
            </span>
          </button>

          <button
            onClick={() => {
              setSelectedTab('broadcasts');
              setSelectedUser(null);
            }}
            className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all cursor-pointer ${
              selectedTab === 'broadcasts'
                ? 'bg-primary-container text-on-primary-container font-semibold shadow-sm'
                : 'text-on-surface-variant hover:bg-white/5 hover:text-on-surface'
            }`}
          >
            <div className="flex items-center gap-3">
              <Send size={18} className={selectedTab === 'broadcasts' ? 'text-primary' : 'text-on-surface-variant'} />
              <span className="text-sm font-label-md">Конструктор рассылок</span>
            </div>
            <span className="text-[10px] font-semibold font-mono bg-white/5 px-2 py-0.5 rounded-full text-on-surface-variant">
              {broadcasts.length}
            </span>
          </button>

          {/* Collapsible details shortcut */}
          {selectedUser && (
            <motion.div 
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="pt-4 border-t border-white/5 mt-4 space-y-md"
            >
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider px-4 block">Текущий участник</span>
              <div 
                onClick={() => setSelectedTab('users')}
                className="mx-2 p-2 bg-primary/10 border border-primary/20 rounded-xl flex items-center justify-between cursor-pointer group"
              >
                <div className="truncate pr-2">
                  <p className="text-xs font-semibold text-on-surface truncate">{selectedUser.fullName}</p>
                  <p className="text-[10px] font-mono text-primary truncate">{selectedUser.username}</p>
                </div>
                <ChevronRight size={14} className="text-primary group-hover:translate-x-1 transition-transform flex-shrink-0" />
              </div>
            </motion.div>
          )}
        </nav>

        {/* Sidebar Footer admin summary info */}
        <div className="p-lg border-t border-white/5 space-y-3 bg-white/2">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-surface-container-highest border border-white/10 flex items-center justify-center font-bold text-xs text-primary shadow">
              AD
            </div>
            <div>
              <p className="text-xs font-semibold text-on-surface leading-tight">Администратор PML</p>
              <p className="text-[10px] text-on-surface-variant">access_level: superadmin</p>
            </div>
          </div>
          
          <div className="flex gap-2">
            <div className="flex-grow p-2 rounded bg-surface-container-low text-center border border-white/5">
              <span className="text-[9px] text-on-surface-variant block uppercase font-bold tracking-wider">БД статус</span>
              <span className="text-xs font-bold text-secondary flex items-center justify-center gap-1 mt-0.5 font-mono">
                <Database size={10} /> Sync (OK)
              </span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Workspace viewport */}
      <div className="flex-grow flex flex-col min-w-0 bg-[#0c141f] overflow-hidden">
        
        {/* Dynamic header row metadata */}
        <header className="h-16 border-b border-white/5 bg-[#090e15]/40 backdrop-blur-xl flex items-center justify-between px-lg z-10 flex-shrink-0">
          
          {/* Mobile responsive sidebar tab anchors drawer triggers */}
          <div className="flex items-center gap-md lg:hidden">
            <div className="w-7 h-7 rounded bg-gradient-to-tr from-primary to-secondary flex items-center justify-center font-black text-on-primary-fixed text-xs select-none shadow">
              П
            </div>
            <div className="flex bg-surface-container border border-white/5 p-1 rounded-xl">
              <button
                onClick={() => {
                  setSelectedTab('users');
                  setSelectedUser(null);
                }}
                className={`py-1.5 px-3 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  selectedTab === 'users' ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant'
                }`}
              >
                Пользователи
              </button>
              <button
                onClick={() => {
                  setSelectedTab('broadcasts');
                  setSelectedUser(null);
                }}
                className={`py-1.5 px-3 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  selectedTab === 'broadcasts' ? 'bg-primary-container text-on-primary-container' : 'text-on-surface-variant'
                }`}
              >
                Рассылки
              </button>
            </div>
          </div>

          <div className="hidden lg:flex items-center gap-2 font-mono text-[11px] text-on-surface-variant">
            <span className="bg-surface-container-highest text-[#65bdff]/90 px-2 py-0.5 rounded font-bold uppercase border border-white/5">
              dev-preview
            </span>
            <span className="text-on-surface-variant/40">|</span>
            <span className="flex items-center gap-1 select-all cursor-pointer">
              <span className="material-symbols-outlined text-[14px]">link</span>
              pml-bot-production
            </span>
          </div>

          {/* Moscow time real clock widget */}
          <div className="flex items-center gap-3">
            <div className="bg-primary/5 border border-primary/20 px-3.5 py-1.5 rounded-xl flex items-center gap-2 font-mono text-xs text-primary shadow-inner">
              <Clock size={13} className="text-primary" />
              <span>МСК (GMT+3):</span>
              <strong className="tracking-widest tabular-nums">{currentTime || "00:00:00"}</strong>
            </div>
          </div>
        </header>

        {/* Scrollable primary card viewport body */}
        <main className="flex-1 overflow-y-auto px-lg py-lg custom-scrollbar">
          <AnimatePresence mode="wait">
            {selectedTab === 'users' ? (
              selectedUser ? (
                <motion.div
                  key="detail"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.2 }}
                >
                  <UserDetail 
                    user={selectedUser} 
                    onBack={() => setSelectedUser(null)} 
                    onUpdateUser={handleUpdateUser}
                  />
                </motion.div>
              ) : (
                <motion.div
                  key="list"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.15 }}
                >
                  <UsersList 
                    users={users} 
                    onSelectUser={(u) => setSelectedUser(u)} 
                    onAddUser={handleAddUser}
                  />
                </motion.div>
              )
            ) : (
              <motion.div
                key="broadcasts"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -15 }}
                transition={{ duration: 0.2 }}
              >
                <Broadcasts 
                  users={users}
                  broadcasts={broadcasts}
                  onAddBroadcast={handleAddBroadcast}
                  onDeleteBroadcast={handleDeleteBroadcast}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
