import logging
from django.template.loader import render_to_string

from config.settings import env_keys
from services.email.tasks import send_email_task

# настройка логов
logger = logging.getLogger('services')

def run_send_email_task_celery(title, html, recipient, **kwargs):
    """
    Функция запускающая отправку Email средствами Celery
    """
    try:
        content = _build_content_to_message(html, **kwargs)
    except Exception as e:
        logger.warning(f'Ошибка при отправки email: {str(e)}', exc_info=True)
    else:
        send_email_task.delay(chat_title=title,
                              recipient=recipient,
                              **content)


def _build_content_to_message(html, **kwargs):
    """
    Функция формирующая контент для отправки Email
    """
    html_content = render_to_string(html,
                                    context={"url": env_keys.get("URL"),
                                             **kwargs},
                                    )
    text_content = render_to_string(html,
                                    context={"url": env_keys.get("URL"),
                                             **kwargs},
                                    )
    return {"text_content": text_content, "html_content": html_content}

