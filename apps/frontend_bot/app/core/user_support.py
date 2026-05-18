"""Общие helpers для пользовательских системных ошибок."""

from __future__ import annotations


DEVELOPER_CONTACT = "@it_was_i_misha"
_DEVELOPER_CONTACT_RECOMMENDATION = (
    f"Если ошибка повторяется, обратитесь к разработчику {DEVELOPER_CONTACT}."
)


def append_developer_contact_recommendation(text: str) -> str:
    """Дописывает рекомендацию обратиться к разработчику, если её ещё нет."""

    if DEVELOPER_CONTACT in text:
        return text

    return f"{text}\n\n{_DEVELOPER_CONTACT_RECOMMENDATION}"


def apply_developer_contact_to_keys(
    messages: dict[str, str],
    *,
    keys: set[str],
) -> dict[str, str]:
    """Расширяет выбранные user-facing ошибки рекомендацией обратиться к разработчику."""

    for key in keys:
        value = messages.get(key)
        if isinstance(value, str):
            messages[key] = append_developer_contact_recommendation(value)

    return messages
