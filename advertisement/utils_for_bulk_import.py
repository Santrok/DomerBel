import time
import openpyxl
from zipfile import ZipFile
import os
import xlsxwriter
from django.contrib.auth import get_user_model

from advertisement.models import Advertisement, PhotoAdvertisement, UploadFile, ErrorFile
from related_data.models import Category, Region, Spisok, ElementTwo
from services.files.uploaded_file import upload_to
from utils.validators import validate_words


def check_article(ads, value_author):
    """Функция проверяет артикул на повторение у уже существующих объявлений,
        при наличии ошибки в артикуле отдает ошибку"""
    if "артикул" not in ads:
        return True
    article = str(ads.get("артикул"))
    if len(article) > 255:
        return "Длина артикула превышает допустимое значение"
    if Advertisement.objects.filter(author=value_author, article=article).exists():
        return "У вас уже существует объявление с таким артикулом"
    return True


def check_title(ads):
    """Функция проверяет заголовок объявления,
        при наличии ошибки в заголовке отдает ошибку"""
    if "заголовок" not in ads:
        return "Заголовок является обязательным полем для объявления"
    title = str(ads.get("заголовок"))
    if len(title) > 255:
        return "Длина заголовка объявления не должна превышать 255 символов"
    try:
        validate_words(title)
    except:
        return "В заголовке запрещено использовать ненормативную лексику"
    return True


def check_price(ads):
    # переписать
    """Функция проверяет цену в объявлении,
        при наличии ошибки в цене отдает ошибку"""
    if "цена" in ads:
        price = str(ads.get("цена"))
        check_type_number = price.count('.')
        if check_type_number == 1:
            whole_part, fractional_part = price.split('.')
            if len(price)<= 10 and  whole_part.isdigit() and fractional_part.isdigit() and len(fractional_part) <=2:
                return True
            else:
                return "В объявлении некорректно указана цена"
        elif check_type_number == 0 and price.isdigit() and len(price)<= 10:
            return True
        else:
            return "В объявлении некорректно указана цена"
    else:
        return True


def check_category(ads):
    """Функция проверяет правильно ли указана категория в объявлении,
        при наличии ошибки в категории отдает ошибку"""
    if "категория" not in ads:
        return "Категория является обязательным полем для объявления"
    category = ads.get("категория")
    if Category.objects.filter(title__iexact=category).exists():
        return True
    return "Указано некорректное значение категории"


def check_region(ads):
    """Функция правильно ли указан регион в объявлении,
        при наличии ошибки в регионе отдает ошибку"""
    if "регион" not in ads:
        return "Регион является обязательным полем для объявления"
    region = ads.get("регион")
    if Region.objects.filter(area__iexact=region).exists():
        return True
    return "Указано некорректное значение региона"


def check_additional_information(ads, result_category_check):
    """Функция проверяет дополнительные поля для детальной информации в объявлении и возвращает словарь,
        если нет ошибок, в противном случае возвращает ошибку"""
    data = {}
    if result_category_check is True:
        error_field = []
        category_from_ads = ads.get('категория')
        category = Category.objects.prefetch_related('field_set').get(title=f'{category_from_ads }')
        fields = category.field_set.all() # все поля, связанные с категорией из объявления
        for field_from_ads in ads.keys():
            if (field_from_ads not in ['артикул', 'заголовок', 'категория', 'регион', 'описание'] and
                    not field_from_ads.startswith('фото')):
                value_field_from_ads = ads.get(field_from_ads)
                field_from_db = fields.filter(title__iexact=field_from_ads)
                if field_from_db:
                    for field in field_from_db:
                        if field.error: # в блоке if проверяются обязательные поля
                            if field.spisok_id: # в блоке if проверяются обязательные поля c установленными значениями
                                # a = Element.objects.filter(spisok_id=field.spisok_id).filter(title__iexact=value_field_from_ads)
                                spisok = Spisok.objects.prefetch_related('element_set').get(id=field.spisok_id)
                                elements_from_db = spisok.element_set.all()
                                elements_for_compare = elements_from_db.filter(title__iexact=value_field_from_ads)
                                if elements_for_compare: # в случае, если значение поля состоит из одного элемента
                                    for element in elements_for_compare:
                                        data[field.title] = element.title
                                else:
                                    first_elem_for_find = ads.get(field.title.lower()).split(' ',1)[0]
                                    element_one = elements_from_db.filter(title__istartswith = first_elem_for_find)
                                    id_element_one = [item.id for item in element_one]
                                    element_two = ElementTwo.objects.filter(element_id__in = id_element_one)
                                    if element_two: # если знаачение поля состоит из двух елементов
                                        value_option_for_field = {}
                                        for one in element_one:
                                            for two in element_two:
                                                key = one.title.lower()+' '+two.title.lower()
                                                value = f'{one.title}, {two.title}'
                                                value_option_for_field[key]=value
                                        full_element = value_option_for_field.get(value_field_from_ads.lower())
                                        if full_element:
                                            data[field.title] = full_element
                                        else:
                                            error_field.append(f'Некорректное значение "{value_field_from_ads}"')
                                    else:
                                        error_field.append(f'Некорректное значение "{value_field_from_ads}"')
                            else: # в блоке else записываются обязательные поля без установленного значения
                                data[field.title] = value_field_from_ads
                        else: # в блоке else записываются необязательные поля
                            data[field.title] = value_field_from_ads
                else:
                    error_field.append(f'Некорректное полe "{field_from_ads}"')
        if error_field:
            data['error'] = error_field
        return data
    else:
        data['error'] = ["Указано некорректное значение категории"]
    return data



def check_description(ads):
    """Функция проверяет описание объявления,
        при наличии ошибки в категории отдает ошибку"""
    if "описание" in ads:
        try:
            validate_words(str(ads.get("описание")))
            return True
        except:
            return "В описании запрещено использовать ненормативную лексику"
    else:
        return "Описание является обязательным полем для объявления"



def processing_ads_from_excel_for_saving(upload_file,value_author):
    """Функция достает собъявление из excel файла пользователя и проверяет поля из него.
        Возвращает список словарей с объявлением и ошибками из объявления при их наличии"""
    ads_for_save = []
    book = openpyxl.open(upload_file, read_only=True)
    sheet = book.active
    row_in_excel = 2
    while row_in_excel <= sheet._max_row:
        ads = {}
        for i in range(0, sheet.max_column):
            if sheet[row_in_excel][i].value != None:
                ads[f'{sheet[1][i].value.lower()}'] = sheet[row_in_excel][i].value
        if ads:
            status_ads = []
            result_article_check = check_article(ads, value_author)
            if result_article_check != True:
                status_ads.append(result_article_check)
            result_title_check = check_title(ads)
            if result_title_check != True:
                status_ads.append(result_title_check)
            result_price_check = check_price(ads)
            if result_price_check != True:
                status_ads.append(result_price_check)
            result_category_check = check_category(ads)
            if result_category_check != True:
                status_ads.append(result_category_check)
            result_region_check = check_region(ads)
            if result_region_check != True:
                status_ads.append(result_region_check)
            result_additional_information_check = check_additional_information(ads, result_category_check)
            if "error" in result_additional_information_check:
                for error in result_additional_information_check.get("error"):
                    if error not in status_ads:
                        status_ads.append(error)
            else:
                ads['подробная_информация'] =  result_additional_information_check
            result_description_check = check_description(ads)
            if result_description_check != True:
                status_ads.append(result_description_check)
            if status_ads:
                error_str = ""
                for error in status_ads:
                    error_str = error_str + f'{error}; '
                ads["ошибки"] = error_str
            ads_for_save.append(ads)
        row_in_excel = row_in_excel + 1
    return ads_for_save



def save_processed_ads_from_excel(ads_for_save,value_author,first_name,phone_number,email):
    """Функция сохраняет уже обработанные объявления из excel.
        Возвращает словарь со списком сохраненных объявления и объявлений с ошибками """
    ads_with_error = []
    saved_ads = []
    for ads in ads_for_save:
        if "ошибки" not in ads:
            ads_for_save = Advertisement(author = value_author,
                article = str(ads.get('артикул')),
                title = str(ads.get('заголовок')),
                price = float(ads.get('цена')),
                category = Category.objects.get(title__iexact=ads.get('категория')),
                bearer = 'Компания',
                region = Region.objects.get(area__iexact=ads.get('регион')),
                contact_name = first_name,
                phone_num = phone_number,
                email = email,
                additional_information = ads.get('подробная_информация'),
                description = str(ads.get('описание')))
            try:
                ads_for_save.save()
                saved_ads.append({'saved_ads':ads_for_save,'ads_with_photo':ads})
            except:
                ads["ошибки"] = "Невозможно сохранить объявление"
                ads_with_error.append(ads)
        else:
            ads_with_error.append(ads)
    return {'saved_ads': saved_ads, 'ads_with_error': ads_with_error}


def update_photo(ads,file_name,upload_zip,email):
    """Функция для извлечения фото из электронного архива,
    и функцию upload_to для сохранения фото объявлений в папку"""
    try:
        path = os.path.join('./media/files_for_bulk_import_of_ads', email)
        with ZipFile(upload_zip,'r') as zip:
            image_from_zip = zip.extract(file_name,path)
        new_location_image = upload_to(ads,image_from_zip)
        folder = new_location_image.split('/')[1]
        if not folder in os.listdir('./media/Advertisement/'):
            os.mkdir(f'./media/Advertisement/{folder}')
        os.replace(f'./{image_from_zip}', f'./media/{new_location_image}')
        return f'{new_location_image}'
    except:
        return f"Невозможно извлечь фото {file_name}"



def adding_photo_to_saved_ads(saved_ads,upload_zip, email):
    """Функция добавляет фото к объявлению и сохроняет их. Возвращает список объявлений с ошибками"""
    ads_with_error = []
    for advertisement in saved_ads:
        ads = advertisement.get('saved_ads')
        photos = advertisement.get('ads_with_photo')
        preview_image = update_photo(ads, photos.get('фото1'), upload_zip, email)
        if preview_image != f"Невозможно извлечь фото {photos.get('фото1')}":
            ads.preview_image = preview_image
            ads.save(update_fields=["preview_image"])
            photo_ads = []
            photo_save = PhotoAdvertisement(
                photo=preview_image,
                advertisement=ads)
            photo_save.save()
            photo_ads.append(photo_save)
            for key in photos.keys():
                if key.startswith('фото') and key != 'фото1':
                    photo = update_photo(ads, photos.get(key), upload_zip, email)
                    if photo != f"Невозможно извлечь фото {photos.get(key)}" and len(photo_ads) <= 30:
                        photo_save = PhotoAdvertisement(
                            photo=photo,
                            advertisement=ads)
                        photo_save.save()
                        photo_ads.append(photo_save)
                    elif photo == f"Невозможно извлечь фото {photos.get(key)}":
                        for photo in photo_ads:
                            os.remove(f'./media/{photo.photo}')
                        ads.delete()
                        photos["ошибки"] = f"Невозможно извлечь фото {photos.get(key)}"
                        ads_with_error.append(photos)
                        break
        else:
            ads.delete()
            photos["ошибки"] = f"Невозможно извлечь фото {photos.get('фото1')}"
            ads_with_error.append(photos)
    return ads_with_error



def write_file_with_error_ads(ads_with_error,email, value_author, upload_file):
    """Функция записывает ecxel-файл обявления с ошибкаи. Отдает ссылку на файл"""
    file = upload_file.replace('./media/','')
    upload_file= UploadFile.objects.filter(file=file)
    path = f'./media/files_for_bulk_import_of_ads/{email}/error_{email}_{time.time()}.xlsx'
    book = xlsxwriter.Workbook(path)
    sheet = book.add_worksheet()
    field = {}
    for row in range(0, len(ads_with_error) + 1):
        if row == 0:
            values = ads_with_error[0]
            values.pop('подробная_информация', None)
            colum = 0
            for title in values.keys():
                sheet.write(row, colum, title)
                field[title] = colum
                colum = colum + 1
        elif row == 1:
            values = ads_with_error[0]
            for title in values.keys():
                colum = field.get(title)
                sheet.write(row, colum, values.get(title))
        else:
            values = ads_with_error[row - 1]
            values.pop('подробная_информация', None)
            for title in values.keys():
                if title in field.keys():
                    colum = field.get(title)
                    sheet.write(row, colum, values.get(title))
                else:
                    field[title] = len(field)
                    colum = field.get(title)
                    sheet.write(0, colum, title)
                    sheet.write(row, colum, values.get(title))
    book.close()
    file_error = ErrorFile(file=path,
                           user= value_author,
                           upload_file=upload_file[0])
    file_error.save()
    UploadFile.objects.filter(file=file).update(status=True)
    return file_error



def save_many_ads_from_excel(upload_file,id,first_name,phone_number,email):
    '''Функция сохраняет объявления из ecxel-файла пользователя. Возвращает или True, в случае, если
        все правильно, или ссылку на файл с ошибками'''
    value_author = get_user_model().objects.get(id=id)
    ads_for_save = processing_ads_from_excel_for_saving(upload_file, value_author)
    result_saving_ads = save_processed_ads_from_excel(ads_for_save,value_author,first_name,phone_number,email)
    ads_with_error = result_saving_ads.get('ads_with_error')
    if ads_with_error:
        file_with_ads_error = write_file_with_error_ads(ads_with_error,email, value_author, upload_file)
        return {'file': file_with_ads_error.file}
    else:
        file = upload_file.replace('./media/', '')
        UploadFile.objects.filter(file=file).update(status=True)
        return True



def save_many_ads_from_zip(upload_zip,id,first_name,phone_number,email):
    '''Функция сохраняет объявления из zip-архива пользователя. Возвращает или True, в случае, если
        все правильно, или ссылку на файл с ошибками'''
    value_author = get_user_model().objects.get(id=id)
    with ZipFile(upload_zip,'r') as zip:
        for file in zip.namelist():
            if file.endswith('.xlsx'):
                excel = zip.extract(file,path=f'./media/files_for_bulk_import_of_ads/{email}/')
    ads_for_save = processing_ads_from_excel_for_saving(excel, value_author)
    result_saving_ads = save_processed_ads_from_excel(ads_for_save, value_author, first_name, phone_number, email)
    ads_with_error = result_saving_ads.get('ads_with_error')
    saved_ads = result_saving_ads.get('saved_ads')
    result_adding_photo = adding_photo_to_saved_ads(saved_ads,upload_zip, email)
    if result_adding_photo:
        for ads in result_adding_photo:
            ads_with_error.append(ads)
    if ads_with_error:
        file_with_ads_error = write_file_with_error_ads(ads_with_error,email,value_author,upload_zip)
        return {'file': file_with_ads_error.file}
    else:
        file = upload_zip.replace('./media/', '')
        UploadFile.objects.filter(file=file).update(status=True)
        return True


