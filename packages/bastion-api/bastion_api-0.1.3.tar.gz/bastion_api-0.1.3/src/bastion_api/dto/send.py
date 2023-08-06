from datetime import datetime

from pydantic import BaseModel

from src.bastion_api.dto.support import PersonBriefDto


class BastionOperatorDto(BaseModel):
    """Тип BastionOperator представляет собой набор данных об операторе «Бастион-2 – ИКС», учетные
данные которого используются для авторизации"""
    opername: str  # Логин оператора
    password: str  # Пароль оператора


class CardDto(BaseModel):
    card_code: str = ""  # Код карты доступа, с которой произошли возвращаемые события. Значение параметра может быть пустым, в этом случае будут возвращены события со всеми картами доступа
    date_from: datetime = ""  # Минимальная дата, которую должны иметь возвращаемые события. Значение параметра может быть пустым
    date_to: datetime = ""  # Максимальная дата, которую должны иметь возвращаемые события. Значение параметра может быть пустым.
    with_photo: bool = ""


class GetPassDto(BaseModel):
    card_status: int = ""  # Статус возвращаемых пропусков. Значение параметра может быть пустым, в этом случае будут возвращены пропуска с любым статусом
    pass_type: int = ""  # Тип возвращаемых пропусков. Значение параметра может быть пустым, в этом случае будут возвращены пропуска всех типов (Постоянный - 1, Временный - 2, Разовый - 4)
    without_photo: bool = True  # Флаг, определяющий, нужно ли возвращать фотографии владельцев пропусков (true если фотографии возвращать не нужно).
    start_numer: int = ""  # Порядковый номер, начиная с которого будут возвращены пропуска (постраничный вывод). Значение параметра может быть пустым, в этом случае будут возвращаться пропуска начиная с первого
    max_count: int = ""  # Максимальное количество пропусков, которое будет возвращено методом (постраничный вывод). Значение параметра может быть пустым, в этом случае количество возвращаемых пропусков ограничиваться не будет


class GetPersonDto(BaseModel):
    second_name: str
    first_name: str
    middle_name: str
    birthday: str
    without_photo: bool


class PersonForGetPass(BaseModel):
    second_name: str
    first_name: str
    middle_name: str
    birthday: str


class PassBriefDto(BaseModel):
    """Тип Pass представляет краткий набор данных персонального пропуска или заявки на пропуск."""
    cardCode: str  # Код карты, выданной на пропуск
    personData: PersonBriefDto
    passType: int  # Тип пропуска
    cardStatus: int  # Статус пропуска
