import validators


def validate(url):
    if not url:
        return 'URL обязателен'
    if len(url) > 255:
        return 'URL не может превышать 255 символов'
    if not validators.url(url):
        return 'Некорректный URL'
