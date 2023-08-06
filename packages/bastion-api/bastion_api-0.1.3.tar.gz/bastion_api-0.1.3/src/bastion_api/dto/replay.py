from __future__ import annotations
from datetime import datetime
from typing import List
from pydantic import BaseModel

from src.bastion_api.dto.support import PersonDto, TimeIntervalDto


class EntryPointDto(BaseModel):
    """Представляет точку прохода в СКУД АПК «Бастион-2»"""
    servID: str  # Идентификатор сервера – владельца точки прохода
    subDeviceNo: int  # Идентификатор устройства на сервере
    subDeviceName: str  # Имя точки прохода


class AccessLevelDto(BaseModel):
    """Тип AccessLevel представляет собой набор данных уровня доступа. Объект типа AccessLevel
    используется в методе создания/редактирования пропуска/заявки на пропуск PutPass, в методе
    получения списка пропусков GetPasses, также в методе получения списка уровней доступа
    GetAccessLevels """
    servID: str  # Идентификатор сервера – владельца точки прохода
    id: int  # Идентификатор уровня доступа
    name: str  # Имя уровня доступа


class DictValDto(BaseModel):
    """Тип DictVal представляет данные словарного значения. Используется в методе запроса словарных
        значений GetDictVals"""
    category: int  # Категория словарного значения
    value: str  # Текст словарного значения


class CardEventDto(BaseModel):
    """Тип CardEvent представляет собой набор данных о событии, произошедшем с картой доступа.
        Используется в методе получения события с картой GetCardEvents"""
    cardCode: str  # Код карты, с которой произошло событие
    entryPoint: EntryPointDto  # Точка прохода, на которой произошло событие с картой
    dateTime: datetime  # Дата и время возникновения события
    msgText: str  # Текст события
    msgCode: int  # Код события
    msgType: int  # Тип события
    comments: str  # Комментарий
    photo: str  # Фотография, прикреплённая к событию


class AttendanceDto(BaseModel):
    """представляет собой данные о посещении с картой доступа"""
    cardCode: str  # Код карты, с которой произошло посещение
    isEntrance: bool  # Флаг, определяющий, является ли посещение входом (true), либо выходом (false)
    dateTime: datetime  # Дата и время возникновения посещения
    comments: str  # Комментарий
    ctrlArea: str  # Зона контроля
    tableno: str  # Табельный номер персоны


class PassDto(BaseModel):
    """Тип Pass представляет набор данных пропуска или заявки на пропуск.
     Используется в методе создания/редактирования пропуска/заявки на пропуск
      и в методе получения списка пропусков."""
    cardCode: str | None = None  # Код карты доступа (может быть пустым в том случае если объект представляет набор данных заявки на пропуск)
    personData: PersonDto  # Набор персональных данных пропуска
    passType: int  # Тип пропуска (Постоянный - 1, Временный - 2, Разовый - 4)
    dateFrom: str | None = None  # Дата начала действия пропуска (может быть пустой)
    dateTo: str | None = None  # Дата окончания действия пропуска (может быть пустой)
    passStatus: int | None   # Статус пропуска
    timeInterval: TimeIntervalDto | None  # Временной интервал
    entryPoints: List[EntryPointDto]  # Массив точек прохода
    accessLevels: List[AccessLevelDto]  # Массив уровней доступа
    passCat: str  # Категория пропуска
    createDate: datetime | None=""  # Дата создания
    issueDate: datetime | None ="" # Дата выдачи
    pincode: int  # Pin-код пропуска


class DeviceDto(BaseModel):
    """Тип Device представляет собой набор данных устройства. Объект типа Device используется в методе
получения набора устройств GetDevices"""
    sdn: int  # Идентификатор устройства
    parentSdn: int | None  # Идентификатор родительского устройства
    driverId: int  # Идентификатор типа драйвера, которому принадлежит устройство
    name: str  # Наименование устройства
    deviceType: int  # Код типа устройства
    deviceTypeName: str  # Текстовое имя типа устройства
    childs: List[DeviceDto]  # Коллекция дочерних устройств


class ControlAreaDto(BaseModel):
    """Тип ControlArea представляет собой набор данных областей контроля. Используется в качестве
выходного параметра метода GetControlAreas, возвращающего коллекцию областей контроля, а
также является полем типа данных Attendance."""
    servId: str  # Идентификатор сервера – владельца области контроля
    id: int  # Идентификатор области контроля на сервере
    name: str  # Имя области контроля


class AccessPointDto(BaseModel):
    """AccessPoint – объект, представляющий точку доступа (дверь, ворота, турникет) в СКУД АПК
    «Бастион-2». Используется в качестве выходного параметра в методе GetAccessPoints,
    возвращающем коллекцию точек доступа."""
    sServID: str  # Идентификатор сервера – владельца точки прохода
    sSubDeviceNo: int  # Идентификатор устройства на сервере
    sSubDeviceName: str  # Имя точки прохода
