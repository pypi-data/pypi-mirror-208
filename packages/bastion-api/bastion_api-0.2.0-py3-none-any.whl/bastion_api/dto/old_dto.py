
# class BastionOperatorDto(BaseModel):
#     """Тип BastionOperator представляет собой набор данных об операторе «Бастион-2 – ИКС», учетные
# данные которого используются для авторизации"""
#     opername: str  # Логин оператора
#     password: str  # Пароль оператора
#

# class GetPersonDto(BaseModel):
#     second_name: str
#     first_name: str
#     middle_name: str
#     birthday: str
#     without_photo: bool


# class PersonForGetPass(BaseModel):
#     second_name: str
#     first_name: str
#     middle_name: str
#     birthday: str

#
# class BastionOperatorDto(BaseModel):
#     """Тип BastionOperator представляет собой набор данных об операторе «Бастион-2 – ИКС», учетные
# данные которого используются для авторизации"""
#     opername: str  # Логин оператора
#     password: str  # Пароль оператора
#
# class GetPersonDto(BaseModel):
#     second_name: str
#     first_name: str
#     middle_name: str
#     birthday: str
#     without_photo: bool
#
#
# class PersonForGetPass(BaseModel):
#     second_name: str
#     first_name: str
#     middle_name: str
#     birthday: str

# class PassDto(BaseModel):
#     """Тип Pass представляет набор данных пропуска или заявки на пропуск.
#      Используется в методе создания/редактирования пропуска/заявки на пропуск
#       и в методе получения списка пропусков."""
#     cardCode: str = ""  # Код карты доступа (может быть пустым в том случае если объект представляет набор данных заявки на пропуск)
#     personData: PersonDto  # Набор персональных данных пропуска
#     passType: int  # Тип пропуска (Постоянный - 1, Временный - 2, Разовый - 4)
#     dateFrom: str = ""  # Дата начала действия пропуска (может быть пустой)
#     dateTo: str = ""  # Дата окончания действия пропуска (может быть пустой)
#     passStatus: int = ""  # Статус пропуска
#     timeInterval: TimeIntervalDto = ""  # Временной интервал
#
#     entryPoints: List[EntryPointDto]  # Массив точек прохода
#     accessLevels: List[AccessLevelDto]  # Массив уровней доступа
#
#     passCat: str  # Категория пропуска
#     createDate: datetime = ""  # Дата создания
#     issueDate: datetime = ""  # Дата выдачи
#     pincode: int  # Pin-код пропуска