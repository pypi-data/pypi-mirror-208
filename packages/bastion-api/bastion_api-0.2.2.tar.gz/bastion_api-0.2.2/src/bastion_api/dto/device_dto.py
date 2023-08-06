from __future__ import annotations
from typing import List

from pydantic import BaseModel


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


