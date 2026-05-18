# Products Module

`app/modules/products_module` отвечает за пользовательский сценарий просмотра
услуг и отправки заявок в backend.

## Responsibility

Модуль:

- показывает меню услуг по кнопке `Посмотреть услуги`
- отправляет описания трёх направлений:
  - `Консультации`
  - `Регрессии`
  - `Наставничество`
- даёт кнопку `Оставить заявку` на экране каждой услуги
- ищет backend user через `GET /api/telegram/users`
- создаёт заявку через `POST /api/products`

## Backend Contract

На отправке заявки модуль выполняет такой flow:

1. ищет пользователя по `telegram_id` через `GET /api/telegram/users`
2. если пользователь не найден, регистрирует его через `POST /api/telegram/users`
3. повторно получает `user_id`
4. отправляет `POST /api/products`

Текущие product code:

- `Консультации` -> `Counseling`
- `Регрессии` -> `Regression`
- `Наставничество` -> `Mentoring`

## File Map

- `handlers.py`
  Пользовательские хендлеры и FSM-состояния модуля.
- `service.py`
  Backend orchestration для поиска пользователя и создания заявки.
- `keyboards.py`
  Reply-клавиатуры меню услуг и экрана конкретной услуги.
- `messages.py` и `messages.json`
  Пользовательские тексты модуля.

## Notes

- модуль построен поверх общего backend client из `system`
- навигация обратно в главное меню остаётся через `send_main_menu(...)`
- продуктовая логика не уходит в `menu_module`, чтобы onboarding и services
  оставались изолированными

