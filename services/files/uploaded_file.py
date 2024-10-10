import os
from datetime import date
from hashlib import md5


def upload_to(instance, filename):
    """Хэширует имя файла и распределяет
       файлы по приложениям и далее в разные папки
       по дате"""
    today = date.today().isoformat()
    save_folder = today
    ext = os.path.splitext(filename)[1]
    name = str(instance.pk or '') + filename
    filename = md5(name.encode('utf8')).hexdigest() + ext
    if instance.__class__.__name__ == 'PhotoAdvertisement':
        basedir = 'Advertisement'
    else:
        basedir = instance.__class__.__name__
    return os.path.join(basedir, save_folder, filename)
