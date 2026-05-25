import React, { useState, useEffect } from 'react';
import { Broadcast, User } from '../types';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Send, 
  Eye, 
  HelpCircle, 
  Sparkles, 
  Upload, 
  FileText, 
  X, 
  Filter, 
  Bold, 
  Italic, 
  Link2, 
  Smile, 
  CheckCircle,
  FileCheck2,
  Clock, 
  Award,
  ChevronDown,
  Trash2,
  Play
} from 'lucide-react';

interface BroadcastsProps {
  users: User[];
  broadcasts: Broadcast[];
  onAddBroadcast: (broadcast: Broadcast) => void;
  onDeleteBroadcast: (id: string) => void;
}

export default function Broadcasts({ users, broadcasts, onAddBroadcast, onDeleteBroadcast }: BroadcastsProps) {
  // Input fields
  const [msgText, setMsgText] = useState('');
  const [selectedSegment, setSelectedSegment] = useState<'Все' | 'В ядре' | 'Не в ядре'>('Все');
  const [selectedDiagnostic, setSelectedDiagnostic] = useState('Все диагностики');
  const [bookletFilter, setBookletFilter] = useState(false);
  const [userIdFilter, setUserIdFilter] = useState('');
  
  // Appended file simulator
  const [attachedFile, setAttachedFile] = useState<{name: string, size: string} | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Stats
  const [lastSentTime, setLastSentTime] = useState('Сегодня, 10:20');
  const [scheduledCount, setScheduledCount] = useState(3);

  // Interactive toggles
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'composer' | 'history'>('composer');

  // Notification banners
  const [toastMessage, setToastMessage] = useState('');
  const [showToast, setShowToast] = useState(false);

  // Dynamic Reach Counter
  const [reachCount, setReachCount] = useState(12482);

  // Re-calculate estimated reach counting on filters
  useEffect(() => {
    // Basic fun simulator logic representing users filters
    let base = 12482;
    if (selectedSegment === 'В ядре') {
      base = 428;
    } else if (selectedSegment === 'Не в ядре') {
      base = 12054;
    }

    // Multiply by diagnostic choice
    if (selectedDiagnostic !== 'Все диагностики') {
      base = Math.floor(base * 0.35);
    }

    // Interconnect booklet filter
    if (bookletFilter) {
      base = Math.floor(base * 0.72);
    }

    // Interconnect chat search ID
    if (userIdFilter.trim().length > 0) {
      base = 1;
    }

    setReachCount(Math.max(1, base));
  }, [selectedSegment, selectedDiagnostic, bookletFilter, userIdFilter]);

  // Insert emoji or markdown helpers
  const insertTextHelper = (before: string, after: string = '') => {
    const textarea = document.getElementById('broadcast-text') as HTMLTextAreaElement;
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    const selected = text.substring(start, end);
    const replacement = before + (selected || "текст") + after;
    
    setMsgText(text.substring(0, start) + replacement + text.substring(end));
    
    // Focus back
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + before.length, start + before.length + (selected || "текст").length);
    }, 100);
  };

  // Upload simulation
  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    simulateUpload("photo_attachment.jpg");
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      simulateUpload(e.target.files[0].name);
    }
  };

  const simulateUpload = (fileName: string) => {
    setIsUploading(true);
    setUploadProgress(10);
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsUploading(false);
          setAttachedFile({name: fileName, size: "3.2 MB"});
          return 100;
        }
        return prev + 30;
      });
    }, 200);
  };

  const triggerToast = (msg: string) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 4000);
  };

  // Dispatch message submission
  const handleSendMessage = (statusType: 'sent' | 'scheduled') => {
    if (!msgText.trim()) {
      alert("Сначала напишите текст рассылки!");
      return;
    }

    const newBroadcast: Broadcast = {
      id: "BC-" + Math.floor(100 + Math.random() * 900),
      text: msgText,
      segment: selectedSegment,
      diagnosticFilter: selectedDiagnostic,
      bookletOnly: bookletFilter,
      sentDate: statusType === 'sent' ? 'Только что' : 'Запланировано на ' + new Date(Date.now() + 86400000).toLocaleDateString('ru-RU') + ' в 12:00',
      status: statusType,
      reach: reachCount
    };

    onAddBroadcast(newBroadcast);
    
    if (statusType === 'sent') {
      setLastSentTime('Сегодня, ' + new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }));
      triggerToast('Рассылка успешно запущена в Telegram-боте PML!');
    } else {
      setScheduledCount(p => p + 1);
      triggerToast('Рассылка запланирована на отправку!');
    }

    setMsgText('');
    setAttachedFile(null);
  };

  return (
    <div className="space-y-lg relative">
      {/* Toast */}
      <AnimatePresence>
        {showToast && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="fixed top-20 right-6 z-50 bg-[#151c27] border-l-4 border-secondary px-6 py-4 rounded-xl shadow-xl flex items-center gap-3 border border-white/5"
          >
            <div className="w-8 h-8 rounded-full bg-secondary/15 flex items-center justify-center text-secondary">
              <CheckCircle size={16} />
            </div>
            <div>
              <p className="text-body-md font-semibold text-on-surface">{toastMessage}</p>
              <p className="text-[11px] text-on-surface-variant">Все API процессы бота PML синхронизированы</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <section>
        <h2 className="text-3xl font-bold tracking-tight text-primary flex items-center gap-2">
          Конструктор рассылок (Письма & TG Пуши)
        </h2>
        <p className="text-body-md text-on-surface-variant mt-1.5 max-w-3xl">
          Создавайте и отправляйте мгновенные или запланированные сообщения вашей аудитории. Используйте умные фильтры ПМЛ для точечного таргетинга респондентов.
        </p>
      </section>

      {/* Tabs */}
      <div className="flex border-b border-white/5 gap-4">
        <button
          onClick={() => setActiveTab('composer')}
          className={`pb-2.5 font-label-md text-sm transition-all relative ${
            activeTab === 'composer' ? 'text-primary font-bold' : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          Новая рассылка
          {activeTab === 'composer' && (
            <motion.div layoutId="tab-active" className="absolute bottom-0 left-0 w-full h-[2px] bg-primary" />
          )}
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`pb-2.5 font-label-md text-sm transition-all relative ${
            activeTab === 'history' ? 'text-primary font-bold' : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          История и Запланировано ({broadcasts.length})
          {activeTab === 'history' && (
            <motion.div layoutId="tab-active" className="absolute bottom-0 left-0 w-full h-[2px] bg-primary" />
          )}
        </button>
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'composer' ? (
          <motion.div 
            key="composer"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="grid grid-cols-1 lg:grid-cols-12 gap-lg items-start"
          >
            {/* Left Column: Filters & Reach estimated numbers */}
            <div className="lg:col-span-5 space-y-lg">
              
              {/* Reach numbers bento widget */}
              <div className="glass-card rounded-2xl p-lg relative overflow-hidden group border border-white/5">
                <div className="absolute -right-4 -top-4 w-24 h-24 bg-primary/10 rounded-full blur-2xl group-hover:bg-primary/20 transition-all duration-700"></div>
                <div className="relative z-10 space-y-2">
                  <span className="font-label-md text-[11px] text-primary uppercase tracking-widest block font-bold">Ожидаемый охват рассылки</span>
                  
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-black text-on-surface" id="reach-count">
                      {reachCount.toLocaleString('ru-RU')}
                    </span>
                    <span className="font-body-sm text-xs text-on-surface-variant opacity-70">респондентов</span>
                  </div>

                  <div className="w-full bg-surface-container-highest h-1.5 rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: "0%" }}
                      animate={{ width: `${Math.min(100, Math.max(5, (reachCount/12482)*100))}%` }}
                      className="bg-primary h-full shadow-[0_0_15px_rgba(124,58,237,0.4)]"
                    ></motion.div>
                  </div>
                  
                  <p className="font-body-sm text-[11px] text-on-surface-variant italic pt-2">
                    * На основе активных сессий телеграм-бота за последние 30 дней.
                  </p>
                </div>
              </div>

              {/* Filtering forms */}
              <div className="glass-card rounded-2xl p-lg space-y-md border border-white/5">
                <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/5">
                  <span className="material-symbols-outlined text-primary text-[22px]">filter_alt</span>
                  <h3 className="font-bold text-headline-sm text-on-surface">Параметры таргетинга</h3>
                </div>

                {/* Core tab filters */}
                <div className="space-y-1.5">
                  <label className="font-label-md text-xs text-on-surface-variant">Сегмент ядра респондентов</label>
                  <div className="flex p-1 bg-surface-container rounded-xl gap-1 border border-white/5">
                    {(['В ядре', 'Не в ядре', 'Все'] as const).map((seg) => (
                      <button
                        key={seg}
                        onClick={() => setSelectedSegment(seg)}
                        className={`flex-grow py-2 px-1 rounded-lg text-center font-label-md text-xs transition-all cursor-pointer ${
                          selectedSegment === seg
                            ? 'bg-primary-container text-on-primary-container shadow-sm font-semibold'
                            : 'text-on-surface-variant hover:bg-surface-container-highest'
                        }`}
                      >
                        {seg}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Diagnostics filter */}
                <div className="space-y-1.5">
                  <label className="font-label-md text-xs text-on-surface-variant">Участие в диагностике ПМЛ</label>
                  <div className="relative">
                    <select
                      value={selectedDiagnostic}
                      onChange={(e) => setSelectedDiagnostic(e.target.value)}
                      className="w-full bg-surface-container border border-white/10 rounded-xl px-4 py-3 text-sm text-on-surface focus:ring-1 focus:ring-primary focus:border-transparent outline-none cursor-pointer appearance-none"
                    >
                      <option>Все диагностики</option>
                      <option>Личностный масштаб v1.2</option>
                      <option>Эмоциональный интеллект</option>
                      <option>Архетипы власти</option>
                    </select>
                    <ChevronDown size={16} className="absolute right-4 top-4 text-on-surface-variant border-none pointer-events-none" />
                  </div>
                </div>

                {/* Booklet check toggle switch */}
                <div className="flex items-center justify-between p-3.5 rounded-xl bg-surface-container border border-white/5">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-secondary text-[22px]">menu_book</span>
                    <div>
                      <span className="font-semibold text-xs text-on-surface block">Получил методичку ПМЛ</span>
                      <span className="text-[10px] text-on-surface-variant block">Исключить ожидания</span>
                    </div>
                  </div>
                  <button 
                    onClick={() => setBookletFilter(!bookletFilter)}
                    className={`w-11 h-6 rounded-full relative p-0.5 transition-colors cursor-pointer ${
                      bookletFilter ? 'bg-secondary' : 'bg-surface-container-highest'
                    }`}
                  >
                    <div className={`w-5 h-5 bg-white rounded-full shadow transition-all ${
                      bookletFilter ? 'translate-x-[20px]' : 'translate-x-0'
                    }`} />
                  </button>
                </div>

                {/* Specific custom chat ID */}
                <div className="space-y-1.5">
                  <div className="flex justify-between items-center">
                    <label className="font-label-md text-xs text-on-surface-variant">Поиск по chat_id / Telegram ID</label>
                    {userIdFilter && (
                      <button onClick={() => setUserIdFilter('')} className="text-[10px] text-red-400">Сбросить</button>
                    )}
                  </div>
                  <div className="flex items-center bg-surface-container border border-white/10 rounded-xl px-4 py-3 focus-within:ring-1 focus-within:ring-primary focus-within:border-transparent outline-none transition-all">
                    <span className="material-symbols-outlined text-[20px] text-on-surface-variant mr-3">alternate_email</span>
                    <input 
                      className="bg-transparent border-none focus:ring-0 text-sm outline-none w-full text-on-surface placeholder:text-on-surface-variant/40" 
                      placeholder="Введите ID пользователя для точечной отладки..." 
                      type="text"
                      value={userIdFilter}
                      onChange={(e) => setUserIdFilter(e.target.value)}
                    />
                  </div>
                </div>
              </div>

            </div>

            {/* Right Column: Constructor / Message builder */}
            <div className="lg:col-span-7 space-y-lg">
              
              <div className="glass-card rounded-2xl p-lg space-y-lg border border-primary/10 shadow-xl shadow-primary/2">
                <div className="flex items-center justify-between pb-2 border-b border-white/5">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-[22px]">edit_note</span>
                    <h3 className="font-bold text-headline-sm text-on-surface">Конструктор сообщения</h3>
                  </div>
                  <span className="text-[10px] font-bold text-primary bg-primary/10 px-2.5 py-1 rounded">Markdown Support</span>
                </div>

                {/* Macro placeholder details helper info */}
                <div className="bg-primary/5 p-3 rounded-xl border border-primary/10 flex items-start gap-2.5">
                  <Sparkles size={16} className="text-primary mt-0.5 flex-shrink-0" />
                  <p className="text-[11px] text-primary leading-snug">
                    Вы можете вставлять метатег <strong className="bg-[#151c27] px-1 py-0.5 rounded font-mono text-amber-200">{`{name}`}</strong> в тело письма для автоматического обращения к получателю по его Полному Имени в Telegram (например, <em>«Здравствуйте, Иван!»</em>).
                  </p>
                </div>

                {/* Editor Textarea */}
                <div className="space-y-sm">
                  <textarea 
                    id="broadcast-text"
                    value={msgText}
                    onChange={(e) => setMsgText(e.target.value)}
                    className="w-full h-56 bg-surface-container border border-white/10 rounded-xl p-4 text-sm font-normal text-on-surface focus:ring-1 focus:ring-primary outline-none transition-all resize-none placeholder:text-on-surface-variant/20 leading-relaxed font-sans" 
                    placeholder="Введите текст вашего сообщения... Поддерживается стандартное форматирование Markdown."
                  />
                  
                  {/* Editor Toolbars */}
                  <div className="flex items-center justify-between bg-surface-container-low p-2 rounded-xl border border-white/5">
                    <div className="flex gap-1">
                      <button 
                        onClick={() => insertTextHelper('**', '**')}
                        className="p-1.5 hover:bg-surface-container-highest rounded text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" 
                        title="Жирный"
                      >
                        <Bold size={15} />
                      </button>
                      <button 
                        onClick={() => insertTextHelper('*', '*')}
                        className="p-1.5 hover:bg-surface-container-highest rounded text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" 
                        title="Курсив"
                      >
                        <Italic size={15} />
                      </button>
                      <button 
                        onClick={() => insertTextHelper('[Ссылка](', ')') }
                        className="p-1.5 hover:bg-surface-container-highest rounded text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer" 
                        title="Вставить ссылку"
                      >
                        <Link2 size={15} />
                      </button>
                      <button 
                        onClick={() => insertTextHelper('🔥')}
                        className="p-1.5 hover:bg-surface-container-highest rounded text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer text-xs" 
                        title="Эмодзи огонь"
                      >
                        🔥
                      </button>
                      <button 
                        onClick={() => insertTextHelper('📌')}
                        className="p-1.5 hover:bg-surface-container-highest rounded text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer text-xs" 
                        title="Эмодзи пин"
                      >
                        📌
                      </button>
                      <button 
                        onClick={() => insertTextHelper('Здравствуйте, {name}!')}
                        className="p-1 hover:bg-primary/10 rounded text-xs text-primary font-bold px-2 transition-colors cursor-pointer" 
                        title="Добавить тег обращения по имени"
                      >
                        {`+ {name}`}
                      </button>
                    </div>

                    <div className="text-[10px] text-on-surface-variant font-mono pr-2 font-semibold">
                      Символов: <span className={msgText.length > 500 ? 'text-amber-200' : 'text-primary'}>{msgText.length}</span>
                    </div>
                  </div>
                </div>

                {/* Drag and drop file area */}
                <div 
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={handleFileDrop}
                  className="border-2 border-dashed border-white/10 rounded-2xl p-6 flex flex-col items-center justify-center space-y-2 hover:border-primary/40 hover:bg-primary/2 transition-all cursor-pointer group relative"
                >
                  <input 
                    type="file" 
                    id="broadcast-attachments"
                    multiple={false}
                    className="absolute inset-0 opacity-0 cursor-pointer"
                    onChange={handleFileSelect}
                  />
                  
                  {isUploading ? (
                    <div className="w-full text-center space-y-md py-2">
                       <Clock className="mx-auto text-primary animate-spin" size={24} />
                       <div className="text-xs text-on-surface font-semibold">Загрузка вложение в ПМЛ хранилище {uploadProgress}%</div>
                       <div className="w-48 mx-auto bg-surface-container h-1 rounded-full overflow-hidden">
                         <div className="bg-primary h-full" style={{ width: `${uploadProgress}%` }} />
                       </div>
                    </div>
                  ) : attachedFile ? (
                    <div className="flex items-center justify-between w-full bg-surface-container/60 p-3 rounded-xl border border-white/5 relative z-10">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-primary/10 text-primary">
                          <FileText size={18} />
                        </div>
                        <div className="text-left">
                          <p className="text-xs font-semibold text-on-surface">{attachedFile.name}</p>
                          <p className="text-[10px] text-on-surface-variant">{attachedFile.size} • Загружен</p>
                        </div>
                      </div>
                      <button 
                        onClick={(e) => {
                          e.preventDefault();
                          setAttachedFile(null);
                        }}
                        className="p-1 px-1.5 rounded-lg hover:bg-red-400/10 text-red-400 text-xs transition-colors relative z-20 pointer-events-auto"
                      >
                        Удалить
                      </button>
                    </div>
                  ) : (
                    <>
                      <div className="w-12 h-12 rounded-full bg-surface-container-highest flex items-center justify-center text-on-surface-variant group-hover:text-primary transition-colors flex-shrink-0">
                        <Upload size={22} />
                      </div>
                      <div className="text-center font-sans">
                        <p className="font-semibold text-xs text-on-surface">Выберите медиа-файл или перетащите его сюда</p>
                        <p className="text-[10px] text-on-surface-variant mt-1">PNG, JPG, PDF, MP3 (до 10MB)</p>
                      </div>
                    </>
                  )}
                </div>

                {/* Markdown instant preview block */}
                {msgText.trim().length > 0 && (
                  <div className="bg-surface-container-low p-4 rounded-xl border border-white/5 space-y-2">
                    <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">Визуальный Предпросмотр</span>
                    <div className="text-xs text-on-surface-variant leading-relaxed whitespace-pre-wrap select-none italic">
                      {msgText.replace('{name}', 'Александр')}
                    </div>
                  </div>
                )}

                {/* Dispatch actions */}
                <div className="flex flex-col sm:flex-row gap-4 pt-2">
                  <button
                    onClick={() => handleSendMessage('sent')}
                    className="flex-1 bg-primary text-on-primary-fixed font-semibold py-3 px-5 rounded-xl shadow-lg shadow-primary/15 transition-all text-sm flex items-center justify-center gap-2 cursor-pointer border border-[#c4b3f5] hover:brightness-110 active:scale-95"
                  >
                    <Send size={15} />
                    Отправить немедленно
                  </button>
                  <button
                    onClick={() => handleSendMessage('scheduled')}
                    className="px-6 border border-white/10 bg-surface-container-low text-on-surface py-3 rounded-xl hover:bg-surface-container-highest cursor-pointer font-semibold transition-all active:scale-95 text-xs flex items-center justify-center gap-2"
                  >
                    <Clock size={15} />
                    Запланировать на завтра
                  </button>
                </div>
              </div>

              {/* Broadcast state logs / statistics grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-md">
                <div className="glass-card rounded-2xl p-md flex items-center gap-3 border border-white/5">
                  <div className="w-10 h-10 rounded-xl bg-secondary/15 flex items-center justify-center text-secondary">
                    <CheckCircle size={18} />
                  </div>
                  <div>
                    <p className="font-semibold text-[11px] text-on-surface-variant uppercase tracking-wider">Последняя успешная</p>
                    <p className="font-semibold text-sm text-on-surface">{lastSentTime}</p>
                  </div>
                </div>

                <div className="glass-card rounded-2xl p-md flex items-center gap-3 border border-white/5">
                  <div className="w-10 h-10 rounded-xl bg-indigo-400/15 flex items-center justify-center text-indigo-300">
                    <FileCheck2 size={18} />
                  </div>
                  <div>
                    <p className="font-semibold text-[11px] text-on-surface-variant uppercase tracking-wider">Очередь вещания</p>
                    <p className="font-semibold text-sm text-on-surface">{scheduledCount} рассылки запланированы</p>
                  </div>
                </div>
              </div>

            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="history"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="space-y-md"
          >
            <div className="bg-surface-container rounded-2xl border border-white/5 overflow-hidden">
              <div className="p-4 bg-white/2 border-b border-white/5 font-semibold text-xs uppercase tracking-wider text-on-surface-variant">
                Логи отправленных и запланированных пушей
              </div>
              <div className="divide-y divide-white/5">
                {broadcasts.length > 0 ? (
                  broadcasts.map((bc) => (
                    <div key={bc.id} className="p-lg hover:bg-white/2 transition-colors flex flex-col md:flex-row md:items-start justify-between gap-md">
                      <div className="space-y-2 flex-1 max-w-3xl">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold text-primary bg-primary/10 px-2 py-0.5 rounded">{bc.id}</span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                            bc.status === 'sent' ? 'bg-secondary/20 text-secondary' : 'bg-indigo-400/20 text-indigo-300'
                          }`}>
                            {bc.status === 'sent' ? 'Отправлено' : 'Запланировано'}
                          </span>
                          <span className="text-xs text-on-surface-variant">Охват: <strong>{bc.reach.toLocaleString('ru-RU')}</strong> респондентов</span>
                        </div>
                        <p className="text-xs text-on-surface bg-black/10 p-3 rounded-lg leading-relaxed whitespace-pre-wrap font-sans">
                          {bc.text}
                        </p>
                        <div className="flex flex-wrap gap-md text-[11px] text-on-surface-variant font-mono">
                          <span>Сегмент: <strong>{bc.segment}</strong></span>
                          <span>Диагностика: <strong>{bc.diagnosticFilter}</strong></span>
                          <span>Только с методичкой: <strong>{bc.bookletOnly ? 'Да' : 'Нет'}</strong></span>
                        </div>
                      </div>

                      <div className="flex flex-row md:flex-col items-center md:items-end justify-between md:justify-start gap-md flex-shrink-0">
                        <div className="text-right">
                          <p className="text-[10px] text-on-surface-variant font-semibold uppercase tracking-wider">Дата запуска</p>
                          <p className="text-xs font-mono font-bold text-on-surface mt-0.5">{bc.sentDate}</p>
                        </div>
                        <button
                          onClick={() => {
                            onDeleteBroadcast(bc.id);
                            if (bc.status === 'scheduled') {
                              setScheduledCount(p => Math.max(0, p - 1));
                            }
                            triggerToast(`Рассылка ${bc.id} удалена из системы!`);
                          }}
                          className="px-3 py-1.5 rounded-lg bg-red-400/10 text-red-400 hover:bg-red-400/20 text-xs font-semibold flex items-center gap-1 transition-colors cursor-pointer"
                        >
                          <Trash2 size={12} />
                          Удалить
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-12 text-center text-on-surface-variant/60">
                    Истории трансляций пока нет. Напишите текст в конструкторе для пилотного пуша.
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
