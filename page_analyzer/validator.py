import validators


def validate(url):
    errors = {}
    if url == '':
        errors['url'] = 'URL обязателен'
    if not validators.url(url):
        errors['url'] = 'Некорректный URL'
    if len(url) > 255:
        errors['url'] = 'URL не может превышать 255 символов'
    return errors
