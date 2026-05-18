# System Error Support Contact Design

## Goal

При user-facing системных ошибках, на которые пользователь не может повлиять сам,
`frontend_bot` должен дополнительно рекомендовать обратиться к разработчику
`@it_was_i_misha`.

## Approach

1. Вынести общий helper в `app/core/user_support.py`.
2. Применять его только к message keys, которые соответствуют
   инфраструктурным/backend/auth ошибкам.
3. Не добавлять рекомендацию к ошибкам, которые пользователь может исправить сам
   (`request_context_missing`, `subscription_still_missing` и т.д.).
4. Сохранить совместимость с уже существующими текстами и не дублировать контакт,
   если он уже встроен в сообщение.

## Affected Areas

- `system` auth error messages
- `menu_module` subscription check failure
- `products_module` request submission failures
- `analysis_module` registration failures
- already existing diagnostic submission failures

## Verification

- unit-тесты на message loaders
- проверка, что контакт не дублируется в diagnostic error messages
