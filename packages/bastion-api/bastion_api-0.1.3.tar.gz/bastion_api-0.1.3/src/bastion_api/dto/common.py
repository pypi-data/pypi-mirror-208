from datetime import datetime
from typing import List

from pydantic import BaseModel

from src.bastion_api.dto.send import PassBriefDto
from src.bastion_api.dto.support import PersonBriefDto, MatValueDto, CarDto


class OrgDto(BaseModel):
    """Тип Org представляет собой данные организации. Используется в методах получения, создания,
редактирования и удаления организаций"""
    orgName: str  # Полное имя организации (включая путь и все дочерние организации, разделенные символом " \ " (отделённым от названий пробелами с обеих сторон)


class DepartDto(BaseModel):
    """Тип Depart представляет собой данные подразделения и используется в методах получения,
создания, редактирования и удаления подразделений"""
    depName: str  # Полное имя подразделения включая путь и все дочерние организации, разделенные символом " \ " (отделённым от названий пробелами с обеих сторон)
    orgName: str  # Полное имя родительской организации включая путь и все дочерние организации, разделенные символом " \ " (отделённым от названий пробелами с обеих сторон)


class MatValuePassDto(BaseModel):
    """Тип MatValuePass представляет собой набор данных материального пропуска или заявки на
пропуск. Объект типа MatValuePass используется в методах создания и редактирования, а также
получения списков материальных пропусков и заявок GetMVPasses, GetMVPassesByPersonPass и
PutMVPass."""

    id: int = None  # Идентификатор пропуска
    passNum: str = None  # Номер пропуска
    createDate: datetime = None  # Дата создания
    matPerson: PersonBriefDto = None  # Материально-ответственное лицо
    toExport: bool  # На вынос
    toImport: bool  # На внос
    status: int = None  # Статус пропуска
    matValues: List[MatValueDto]  # Коллекция материальных ценностей
    Pass: PassBriefDto  # Персональный пропуск
    startDate: str  # Дата начала действия
    endDate: str  # Дата окончания действия
    goalOrganization: str = None  # Организация назначения
    goalDepartment: str = None  # Подразделение назначения


class CarPassDto(BaseModel):
    """Тип CarPass представляет собой набор данных транспортного пропуска или заявки на пропуск.
Объект типа CarPass используется в методах создания и редактирования, а также получения
списков транспортных пропусков и заявок GetCarPasses, GetCarPassesByPersonPass и PutCarPass"""
    id: int = None  # Идентификатор пропуска
    passNum: str = None  # Номер пропуска
    dateCreate: str = None  # Дата создания
    status: int = None  # Статус пропуска
    cars: List[CarDto]  # Коллекция транспорта
    Pass: PassBriefDto  # Персональный пропуск
    startDate: str  # Дата начала действия
    endDate: str  # Дата окончания действия
