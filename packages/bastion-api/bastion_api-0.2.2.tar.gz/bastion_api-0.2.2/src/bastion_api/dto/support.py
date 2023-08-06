from pydantic import BaseModel


class DictValDto(BaseModel):
    """Тип DictVal представляет данные словарного значения. Используется в методе запроса словарных
        значений GetDictVals"""
    category: int  # Категория словарного значения
    value: str  # Текст словарного значения


class TimeIntervalDto(BaseModel):
    """Объект типа TimeInterval представляет собой временной промежуток, фигурирующий в уровне
доступа, привязанному к пропуску в СКУД АПК «Бастион-2». Объект типа TimeInterval является
полем в типе данных Pass, использующемся в методе создания/редактирования пропуска/заявки
на пропуск PutPass и в методе получения коллекции пропусков GetPasses"""
    timeStart: str  # Время начала действия пропуска в течение дня HH:MM:SS
    timeEnd: str  # Время окончания действия пропуска в течение дня HH:MM:SS
    inSaturday: int  # 1/0 – Разрешение/запрет прохода в субботу
    inSunday: int  # 1/0 – Разрешение/запрет прохода в воскресение
    inHolidays: int  # 1/0 – Разрешение/запрет прохода в праздники и


class MatValueDto(BaseModel):
    """Тип MatValue представляет собой набор данных материальной ценности. Объект типа MatValue
является полем объекта MatValuePass, использующегося в методах создания и редактирования, а
также получения списков материальных пропусков и заявок GetMVPasses,
GetMVPassesByPersonPass и PutMVPass"""
    type: str  # Тип материальной ценности
    valFld1: str = None  # Количество
    valFld2: str = None  # Вес
    valFld3: str = None  # Объем
    valFld4: str = None  # Номер доверенности
    valFld5: str = None  # Кем выдана доверенность
    valFld6: str = None  # Номер накладной
    valFld7: str = None  # Кем выдана накладная
    valFld8: str = None  # No вет. Свидетельства
    valFld9: str = None  # Номер разнарядки
    valFld10: str = None  # Куда предназначается
    valFld11: str = None  # Дополнительное поле
    valFld12: str = None  # Дополнительное поле
    valFld13: str = None  # Дополнительное поле
    valFld14: str = None  # Дополнительное поле
    valFld15: str = None  # Дополнительное поле
    valFld16: str = None  # Дополнительное поле
    valFld17: str = None  # Дополнительное поле
    valFld18: str = None  # Дополнительное поле
    valFld19: str = None  # Дополнительное поле
    valFld20: str = None  # Дополнительное поле
    orderNum: int = None  # Порядковый номер


class CarDto(BaseModel):
    """Тип Car представляет собой набор данных транспортного средства. Объект типа Car является полем
объекта CarPass, использующегося в методах создания и редактирования, а так же получения
списков транспортных пропусков и заявок GetCarPasses, GetCarPassesByPersonPass и PutCarPass"""
    regNo: str  # Регистрационный номер
    carModel: str = None  # Модель
    carDescription: str = None  # Описание
    carPhoto: str = None  # Фотография
    carYear: int = None  # Год выпуска
    carColorStr: str = None  # Цвет
    carWeight: str = None  # Вес
    carVolume: str = None  # Версия
    carOwnerStr: str = None  # Владелец
    carTypeStr: str = None  # Тип


class PersonBriefDto(BaseModel):
    """представляет собой краткий набор данных персоны"""
    name: str
    firstName: str = None
    secondName: str = None
    birthDate: str = None


class PassBriefDto(BaseModel):
    """Тип Pass представляет краткий набор данных персонального пропуска или заявки на пропуск."""
    CardCode: str
    PersonData: PersonBriefDto
    PassType: int
    CardStatus: int
