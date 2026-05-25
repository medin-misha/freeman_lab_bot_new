export interface Diagnostic {
  id: string;
  name: string;
  status: 'Готово' | 'Прервано' | 'В процессе';
  date: string;
  files: {
    mic?: boolean;
    description?: boolean;
    text_snippet?: boolean;
  };
}

export interface CoreForm {
  id: string;
  isActual: boolean;
  date: string;
  activity: string;
  request: string;
  priorities: string[];
  readiness: string;
  weeklyHours: string;
  difficulties: string;
  isPaid: boolean;
}

export interface User {
  id: string;
  username: string;
  fullName: string;
  status: 'В ядре' | 'Не в ядре' | 'Guest' | 'External';
  lastActive: string;
  activityText: string;
  phone: string;
  city: string;
  email: string;
  timezone: string;
  birthDate: string;
  adminNotes: string;
  registeredDate: string;
  utmSource?: string;
  utmCampaign?: string;
  currentBranch?: string;
  currentStep?: string;
  channelSubscribed: boolean;
  
  // Bot Checklist Status
  bookletReceived: boolean;
  coreFormStatus: 'В процессе' | 'Получена' | 'Не начата';
  consentApproved: boolean;
  
  diagnostics: Diagnostic[];
  coreApplications: CoreForm[];
  analysisDates: string[];
}

export interface Broadcast {
  id: string;
  text: string;
  segment: 'В ядре' | 'Не в ядре' | 'Все';
  diagnosticFilter: string;
  bookletOnly: boolean;
  sentDate: string;
  status: 'sent' | 'scheduled';
  reach: number;
}
