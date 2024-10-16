from config.settings import env_keys


def get_context_data(request):
    context = {
        "public_key": env_keys.get('RECAPTCHA_PUBLIC_KEY'),
        "url": env_keys.get('URL'),
    }
    return context
