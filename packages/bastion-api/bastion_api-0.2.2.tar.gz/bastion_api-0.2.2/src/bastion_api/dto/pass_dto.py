from datetime import datetime
from typing import List

from pydantic import BaseModel

from src.bastion_api.dto.person_dto import PersonDto
from src.bastion_api.dto.points_dto import EntryPointDto, AccessLevelDto
from src.bastion_api.dto.support import TimeIntervalDto, PersonBriefDto, MatValueDto, CarDto, PassBriefDto


class PassDto:
    class NewPassPerson(BaseModel):
        """create_or_update_pass"""
        personData: PersonDto  # Набор персональных данных пропуска
        entryPoints: List[EntryPointDto] = ""  # Массив точек прохода
        accessLevels: List[AccessLevelDto] = ""  # Массив уровней доступа
        passCat: str  # Категория пропуска
        pincode: int  # Pin-код пропуска
        dateFrom: str = ""  # Дата начала действия пропуска (может быть пустой)
        dateTo: str = ""  # Дата окончания действия пропуска (может быть пустой)
        passStatus: int = ""  # Статус пропуска
        passType: int  # Тип пропуска (Постоянный - 1, Временный - 2, Разовый - 4)
        timeInterval: TimeIntervalDto = ""  # Временной интервал
        createDate: datetime = ""  # Дата создания
        issueDate: datetime = ""  # Дата выдачи

    class ReturnPassForCardCode(BaseModel):
        """return_pass_for_card"""
        cardCode: str = ""  # Код карты доступа (может быть пустым в том случае если объект представляет набор данных заявки на пропуск)
        personData: PersonDto  # Набор персональных данных пропуска
        pincode: int  # Pin-код пропуска
        passCat: str  # Категория пропуска


    class ReturnPass(BaseModel):
        """get_pass"""
        card_status: int = ""  # Статус возвращаемых пропусков. Значение параметра может быть пустым, в этом случае будут возвращены пропуска с любым статусом
        pass_type: int = ""  # Тип возвращаемых пропусков. Значение параметра может быть пустым, в этом случае будут возвращены пропуска всех типов (Постоянный - 1, Временный - 2, Разовый - 4)
        without_photo: bool = ""  # Флаг, определяющий, нужно ли возвращать фотографии владельцев пропусков (true если фотографии возвращать не нужно).
        start_numer: int = ""  # Порядковый номер, начиная с которого будут возвращены пропуска (постраничный вывод). Значение параметра может быть пустым, в этом случае будут возвращаться пропуска начиная с первого
        max_count: int = ""  # Максимальное количество пропусков, которое будет возвращено методом (постраничный вывод). Значение параметра может быть пустым, в этом случае количество возвращаемых пропусков ограничиваться не будет



class GetPassByPersonDto(BaseModel):
    """Тип Pass представляет краткий набор данных персонального пропуска или заявки на пропуск.
    get_material_pass_by_person
    get_car_pass_by_person_pass
    """
    cardCode: str  # Код карты, выданной на пропуск
    personData: PersonBriefDto
    passType: int  # Тип пропуска
    cardStatus: int  # Статус пропуска


class CardDto(BaseModel):
    card_code: str = ""  # Код карты доступа, с которой произошли возвращаемые события. Значение параметра может быть пустым, в этом случае будут возвращены события со всеми картами доступа
    date_from: datetime = ""  # Минимальная дата, которую должны иметь возвращаемые события. Значение параметра может быть пустым
    date_to: datetime = ""  # Максимальная дата, которую должны иметь возвращаемые события. Значение параметра может быть пустым.
    with_photo: bool = ""


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



