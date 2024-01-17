import validators


def validate(url):
    errors = {}
    if url == '':
        errors['url'] = 'URL обязателен'
    if validators.url(url) is False:
        errors['url'] = 'Некорректный URL'
    if len(url) > 255:
        errors['url'] = 'URL не может превышать 255 символов'
    return errors
