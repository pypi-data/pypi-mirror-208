from datetime import datetime

from pydantic import BaseModel


class PersonDto(BaseModel):
    """Объект типа Person представляет собой набор данных о персоне. Объект типа Person является
полем объекта Pass, использующегося в методе создания редактирования пропуска/заявки на
пропуск PutPass и метода получения коллекции пропусков GetPasses"""
    name: str  # Фамилия
    firstName: str  # Имя
    secondName: str = ""   # Отчество
    tableNo: str = ""   # Табельный номер
    personCat: str = ""   # Категория
    org: str  # Организация
    dep: str  # Департамент
    post: str  # Должность
    comments: str = ""  # Комментарии
    docIssueOrgan: str = ""  # Орган, выдавший документ, удостоверяющий личность
    docSer: str = ""  # Серия документа
    docNo: str = ""  # Номер документа
    docIssueDate: datetime = ""  # Дата выдачи документа
    birthDate: str = ""  # Дата рождения
    birthPlace: str = ""  # Место рождения
    address: str = ""  # Адрес прописки
    phone: str = ""  # Телефон
    foto: str = ""  # Фотография в виде Base64-строки
    addField1: str = ""  # Дополнительное поле 1
    addField2: str = ""  # Дополнительное поле 2
    addField3: str = ""  # Дополнительное поле 3
    addField4: str = ""  # Дополнительное поле 4
    addField5: str = ""  # Дополнительное поле 5
    addField6: str = ""  # Дополнительное поле 6
    addField7: str = ""  # Дополнительное поле 7
    addField8: str = ""  # Дополнительное поле 8
    addField9: str = ""  # Дополнительное поле 9
    addField10: str = ""  # Дополнительное поле 10
    addField11: str = ""  # Дополнительное поле 11
    addField12: str = ""  # Дополнительное поле 12
    addField13: str = ""  # Дополнительное поле 13
    addField14: str = ""  # Дополнительное поле 14
    addField15: str = ""  # Дополнительное поле 15
    addField16: str = ""  # Дополнительное поле 16
    addField17: str = ""  # Дополнительное поле 17
    addField18: str = ""  # Дополнительное поле 18
    addField19: str = ""  # Дополнительное поле 19
    addField20: str = ""  # Дополнительное поле 20
    createDate: datetime = ""  # Дата создания
