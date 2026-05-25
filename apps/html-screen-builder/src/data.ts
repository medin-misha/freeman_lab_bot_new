import { User, Broadcast } from './types';

export const INITIAL_USERS: User[] = [
  {
    id: "123456789",
    username: "@johndoe",
    fullName: "Иван Иванов",
    status: "В ядре",
    lastActive: "12.10.2023 14:20",
    activityText: "Сегодня, 10:05",
    phone: "+7 999 123 45 67",
    city: "Москва",
    email: "john.doe@example.com",
    timezone: "GMT+3",
    birthDate: "01.01.1990",
    adminNotes: "Лояльный клиент, проходил 3 курса. Интересуется темой масштабирования команды.",
    registeredDate: "12.03.2024",
    utmSource: "Yandex_Direct_Scale",
    utmCampaign: "spring_promo",
    currentBranch: "Core_Application_V2",
    currentStep: "Шаг 4: Мотивация",
    channelSubscribed: true,
    bookletReceived: true,
    coreFormStatus: "В процессе",
    consentApproved: true,
    diagnostics: [
      {
        id: "D-9921",
        name: "Личностный масштаб v1.2",
        status: "Готово",
        date: "15.03.2024",
        files: { mic: true, description: true, text_snippet: true }
      },
      {
        id: "D-9840",
        name: "Эмоциональный интеллект",
        status: "Прервано",
        date: "10.03.2024",
        files: {}
      }
    ],
    coreApplications: [
      {
        id: "Заявка #3",
        isActual: true,
        date: "14.03.2024 в 18:45",
        activity: "CEO IT-компании, разработка финтех-решений для малого бизнеса.",
        request: "Хочу вырасти в 5 раз за год. Сейчас уперся в потолок, операционка съедает всё время.",
        priorities: ["Масштабирование", "Делегирование", "Мышление"],
        readiness: "Высокая",
        weeklyHours: "10-15 ч.",
        difficulties: "Боюсь потерять контроль над качеством продукта при быстром росте команды.",
        isPaid: true
      }
    ],
    analysisDates: ["12.03.2024 18:00", "05.02.2024 12:30", "20.01.2024 14:00"]
  },
  {
    id: "87654321",
    username: "@mary_psy",
    fullName: "Мария Соколова",
    status: "Не в ядре",
    lastActive: "11.10.2023 09:15",
    activityText: "Вчера, 23:45",
    phone: "+7 911 445 22 11",
    city: "Санкт-Петербург",
    email: "mary.psy@example.com",
    timezone: "GMT+3",
    birthDate: "14.10.1988",
    adminNotes: "Психолог, хочет внедрить методику масштабирования в свои психологические сессии и коучинг программы.",
    registeredDate: "11.03.2024",
    utmSource: "Telegram_Group",
    utmCampaign: "autumn_launch",
    currentBranch: "Onboarding_V1",
    currentStep: "Шаг 1: Приветствие",
    channelSubscribed: false,
    bookletReceived: false,
    coreFormStatus: "Не начата",
    consentApproved: true,
    diagnostics: [
      {
        id: "D-9730",
        name: "Эмоциональный интеллект",
        status: "Готово",
        date: "11.03.2024",
        files: { mic: true, description: true }
      }
    ],
    coreApplications: [],
    analysisDates: ["11.03.2024 19:30"]
  },
  {
    id: "44556677",
    username: "@alex_scale",
    fullName: "Александр Громов",
    status: "В ядре",
    lastActive: "10.10.2023 18:30",
    activityText: "Сегодня, 08:22",
    phone: "+7 905 222 11 33",
    city: "Екатеринбург",
    email: "alex.scale@example.com",
    timezone: "GMT+5",
    birthDate: "05.05.1992",
    adminNotes: "Строит агентство недвижимости. Быстро отвечает, заинтересован в масштабировании своего отдела продаж и делегировании звонков.",
    registeredDate: "10.03.2024",
    utmSource: "VK_Ads_Business",
    utmCampaign: "gromov_retarget",
    currentBranch: "Core_Application_V2",
    currentStep: "Шаг 2: Диагностика",
    channelSubscribed: true,
    bookletReceived: true,
    coreFormStatus: "Получена",
    consentApproved: true,
    diagnostics: [
      {
        id: "D-9512",
        name: "Личностный масштаб v1.2",
        status: "Готово",
        date: "12.03.2024",
        files: { mic: true, description: true, text_snippet: true }
      },
      {
        id: "D-9610",
        name: "Архетипы власти",
        status: "Готово",
        date: "10.03.2024",
        files: { description: true }
      }
    ],
    coreApplications: [
      {
        id: "Заявка #1",
        isActual: false,
        date: "10.03.2024 в 12:15",
        activity: "Основатель агентства недвижимости в Екатеринбурге (штат 25 человек).",
        request: "Хочу отойти от операционки, так как контролирую каждую сделку самостоятельно.",
        priorities: ["Делегирование", "Систематизация"],
        readiness: "Высокая",
        weeklyHours: "8-10 ч.",
        difficulties: "Сотрудники не умеют продавать без моего личного вовлечения.",
        isPaid: true
      }
    ],
    analysisDates: ["10.03.2024 15:00"]
  },
  {
    id: "10293847",
    username: "@elena_mark",
    fullName: "Елена Маркова",
    status: "External",
    lastActive: "Yesterday, 09:45",
    activityText: "1д назад",
    phone: "+7 903 555 12 34",
    city: "Казань",
    email: "elena.m@example.com",
    timezone: "GMT+3",
    birthDate: "23.07.1995",
    adminNotes: "Представитель консалтинговой компании, вошла через партнерский вебинар.",
    registeredDate: "05.03.2024",
    utmSource: "Partner_Webinar",
    utmCampaign: "cons_promo",
    currentBranch: "External_Link_Flow",
    currentStep: "Шаг 3: Соглашение",
    channelSubscribed: true,
    bookletReceived: true,
    coreFormStatus: "Не начата",
    consentApproved: true,
    diagnostics: [],
    coreApplications: [],
    analysisDates: []
  },
  {
    id: "99018273",
    username: "@petrov_igor",
    fullName: "Игорь Петров",
    status: "Guest",
    lastActive: "12 Oct, 11:30",
    activityText: "4д назад",
    phone: "+7 925 888 77 66",
    city: "Новосибирск",
    email: "igor.p@example.com",
    timezone: "GMT+7",
    birthDate: "12.12.1985",
    adminNotes: "Зарегистрировался в боте из любопытства. Информацией о бизнесе пока не делился.",
    registeredDate: "01.03.2024",
    utmSource: "Direct_Search",
    utmCampaign: "untracked",
    currentBranch: "Guest_Welcoming",
    currentStep: "Шаг 1",
    channelSubscribed: false,
    bookletReceived: false,
    coreFormStatus: "Не начата",
    consentApproved: false,
    diagnostics: [],
    coreApplications: [],
    analysisDates: []
  },
  {
    id: "34829102",
    username: "@wolf_alex",
    fullName: "Александр Вольф",
    status: "В ядре",
    lastActive: "Today, 14:20",
    activityText: "2м назад",
    phone: "+7 912 334 55 66",
    city: "Сочи",
    email: "wolf@example.com",
    timezone: "GMT+3",
    birthDate: "15.02.1991",
    adminNotes: "Серийный предприниматель, имеет несколько бизнесов.",
    registeredDate: "14.03.2024",
    utmSource: "Instagram_Ref",
    utmCampaign: "wolf_blog",
    currentBranch: "Core_Application_V2",
    currentStep: "Шаг 5: Итоги",
    channelSubscribed: true,
    bookletReceived: true,
    coreFormStatus: "Получена",
    consentApproved: true,
    diagnostics: [
      {
        id: "D-9400",
        name: "Архетипы власти",
        status: "Готово",
        date: "14.03.2024",
        files: { mic: true, description: true }
      }
    ],
    coreApplications: [
      {
        id: "Заявка #2",
        isActual: true,
        date: "14.03.2024 в 10:00",
        activity: "Производство эко-упаковки.",
        request: "Интересует построение совета директоров и выход из ежедневной рутины.",
        priorities: ["Делегирование", "Совет директоров"],
        readiness: "Высокая",
        weeklyHours: "15+ ч.",
        difficulties: "Некому передать ключевой бизнес-процесс.",
        isPaid: true
      }
    ],
    analysisDates: ["14.03.2024 16:00"]
  },
  {
    id: "55432109",
    username: "@dmitry_kuz",
    fullName: "Дмитрий Кузнецов",
    status: "В ядре",
    lastActive: "15 Oct, 22:10",
    activityText: "15м назад",
    phone: "+7 960 111 22 33",
    city: "Краснодар",
    email: "dmitry.k@example.com",
    timezone: "GMT+3",
    birthDate: "18.06.1987",
    adminNotes: "Строительная компания. Высокий средний чек, хочет масштабироваться по франшизе.",
    registeredDate: "10.03.2024",
    utmSource: "Yandex_Direct_Scale",
    utmCampaign: "scale_franchise",
    currentBranch: "Core_Application_V2",
    currentStep: "Шаг 3: Франшиза",
    channelSubscribed: true,
    bookletReceived: true,
    coreFormStatus: "Получена",
    consentApproved: true,
    diagnostics: [
      {
        id: "D-9311",
        name: "Личностный масштаб v1.2",
        status: "Готово",
        date: "11.03.2024",
        files: { text_snippet: true, description: true }
      }
    ],
    coreApplications: [
      {
        id: "Заявка #4",
        isActual: true,
        date: "11.03.2024 в 14:00",
        activity: "Малоэтажное строительство в ЮФО.",
        request: "Цель — упаковать франшизу и продать 10 точек за первый год.",
        priorities: ["Франшиза", "Систематизация"],
        readiness: "Высокая",
        weeklyHours: "12-15 ч.",
        difficulties: "Сложно описать стандарты качества строительных работ в регионах.",
        isPaid: true
      }
    ],
    analysisDates: ["11.03.2024 17:00"]
  }
];

export const INITIAL_BROADCASTS: Broadcast[] = [
  {
    id: "BC-001",
    text: "Приветствую! Мы обновили нашу главную методичку по психологии масштаба.\nСкачать ее в PDF вы можете, нажав на кнопку ниже.\nЖелаем продуктивного дня!",
    segment: "Все",
    diagnosticFilter: "Все диагностики",
    bookletOnly: true,
    sentDate: "Сегодня, 10:20",
    status: "sent",
    reach: 12482
  },
  {
    id: "BC-002",
    text: "Внимание участников Ядра!\nСегодня в 19:00 по МСК состоится закрытая онлайн-диагностика Личностного Масштаба.\nСсылка на Zoom придет за 10 минут до старта.",
    segment: "В ядре",
    diagnosticFilter: "Личностный масштаб v1.2",
    bookletOnly: false,
    sentDate: "Вчера, 18:00",
    status: "sent",
    reach: 428
  },
  {
    id: "BC-003",
    text: "[Авто-напоминание] Вы зарегистрировались на разбор, но не завершили диагностику Архетипов Власти.\n\nПожалуйста, пройдите опрос до конца, чтобы психолог получил репрезентативную картину.",
    segment: "Все",
    diagnosticFilter: "Архетипы власти",
    bookletOnly: false,
    sentDate: "Завтра, 12:00",
    status: "scheduled",
    reach: 125
  }
];
