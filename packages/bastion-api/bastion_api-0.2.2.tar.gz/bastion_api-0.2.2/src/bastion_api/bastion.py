from typing import Dict, List
from datetime import datetime as dt, timedelta as td
from pydantic import BaseModel
from aiohttp import ClientResponse, ClientSession
from loguru import logger

from src.bastion_api.dto.device_dto import DeviceDto
from src.bastion_api.dto.organization_dto import OrgDto, DepartDto
from src.bastion_api.dto.pass_dto import CardEventDto, CardDto, AttendanceDto, PassDto, MatValuePassDto, CarPassDto
from src.bastion_api.dto.person_dto import PersonDto
from src.bastion_api.dto.points_dto import EntryPointDto, AccessLevelDto, ControlAreaDto, AccessPointDto
from src.bastion_api.dto.support import DictValDto, PassBriefDto
from src.bastion_api.handlers import BastionIntegrationError, _handle_response
from src.bastion_api.dto.config import IntegrationConfig


class Bastion:
    session: ClientSession
    config: BaseModel
    bastion_servers: []
    _code_for_url: str = ""
    config: IntegrationConfig

    async def _wrap_response(self, method: str, url: str, data: BaseModel | None | Dict = None) -> ClientResponse:
        logger.warning(url)
        if self.session:
            async with self.session.request(method.upper(),
                                            url=f"http://{self.config.iks_host}:{self.config.iks_port}{url}",
                                            json=data.dict() if isinstance(data, BaseModel) else data if isinstance(
                                                data, Dict) else None) as response:
                await response.read()

                if "debug" in self.config.log:
                    logger.debug(
                        f"\nurl: {url}\nresponse_body: {bytes(await response.read()).decode()}\nresponse: {response}")

                if response.cookies:
                    for cook in response.cookies.values():
                        cook["expires"] = (dt.now() + td(days=1)).strftime("%a, %d %b %Y %H:%M:%S GMT")
                    self.session.cookie_jar.update_cookies(response.cookies)
                if response.status != 200:
                    raise BastionIntegrationError(message=f"Bad response status:  {response.status}")

        return response

    # ________________________________________________________________________________________________________

    async def connect_to_bastion_iks(self, search_servers: str = None):
        """Функция осуществляет подключение к Бастион ИКС согласно файлу конфигурации"""

        response = await(await self._wrap_response(method="POST", url="/api/Login",
                                                   data={"opername": f"{self.config.iks_operator_login}",
                                                         "password": f"{self.config.iks_operator_password}"})).text()
        if "info" in self.config.log:
            logger.info(response)

        self.bastion_servers = (await (await self._wrap_response(method="GET", url="/api/GetServers")).json())
        if search_servers:
            if search_servers.lower() in self.bastion_servers.servers_code:
                self.bastion_servers.servers_code = search_servers.lower()
            else:
                raise BastionIntegrationError(message="Some server not found")

        for server_code in (
                self.bastion_servers if self.bastion_servers.__class__ == "list" else [
                    self.bastion_servers]):
            self._code_for_url = self._code_for_url + f"srvCode={server_code}&"

    # ________________________________________________________________________________________________________

    async def logout(self):
        await self._wrap_response(method="POST", url="/api/LogOff")

    # ________________________________________________________________________________________________________

    async def get_version(self) -> str:
        """Метод, возвращающий строку с версией модуля"""
        response = await (await self._wrap_response(method="GET", url="/api/GetVersion")).text()
        if "info" in self.config.log:
            logger.info(response)
        return response

    async def check_connection(self) -> str:
        """Метод предназначен для проверки связи с одним или несколькими серверами."""
        response = await (
            await self._wrap_response(method="GET", url=f"/api/CheckConnection?{self._code_for_url}")).text()
        if "info" in self.config.log:
            logger.info(response)
        return response

    # ________________________________________________________________________________________________________

    async def get_entity_points(self) -> List[EntryPointDto]:
        """Метод, предназначенный для получения информации о точках прохода"""
        response = await (
            await self._wrap_response(method="GET", url=f"/api/GetEntryPoints?{self._code_for_url}")).json()
        model_list = await _handle_response(response, EntryPointDto)
        if "info" in self.config.log:
            logger.info(response)
        return model_list

    async def get_access_level(self) -> List[AccessLevelDto]:
        """Метод, предназначенный для получения информации об уровнях доступа"""
        response = await (
            await self._wrap_response(method="GET", url=f"/api/GetAccessLevels?{self._code_for_url}")).json()
        model_list = await _handle_response(response, AccessLevelDto)
        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    # ________________________________________________________________________________________________________

    async def get_dict_value(self, category: int = "") -> List[DictValDto]:
        """Метод предназначен для запроса списка словарных значений с фильтрацией
        по категории.
        category = Категория словарных значений, информацию о которых требуется получить
        """
        response = await (await self._wrap_response(method="GET", url=f"/api/GetDictVals?{self._code_for_url}"
                                                                      f"category={category}")).json()
        model_list = await _handle_response(response, DictValDto)
        if "info" in self.config.log:
            logger.info(response)
        return model_list

    async def get_card_events(self, card_info: CardDto) -> List[CardEventDto]:
        """Метод предназначен для получения списка событий, произошедших с конкретной картой доступа"""

        response = await(await self._wrap_response(method="GET",
                                                   url=f"/api/GetCardEvents?{self._code_for_url}"
                                                       f"cardCode={card_info.card_code}&"
                                                       f"dateFrom={card_info.date_from}&"
                                                       f"dateTo={card_info.date_to}")).json()
        model_list = await _handle_response(response, CardEventDto)
        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    async def get_attendance(self, card_info: CardDto) -> List[AttendanceDto]:
        """Метод предназначен для получения списка посещений с конкретной картой доступа,
         либо со всеми катами доступа с сервера"""

        response = await (await self._wrap_response(method="GET",
                                                    url=f"/api/GetAttendance?{self._code_for_url}"
                                                        f"cardCode={card_info.card_code}&"
                                                        f"dateFrom={card_info.date_from}&"
                                                        f"dateTo={card_info.date_to}")).json()
        model_list = await _handle_response(response, AttendanceDto)
        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    # ________________________________________________________________________________________________________

    async def create_or_update_pass(self, new_pass_card: PassDto.NewPassPerson, use_access_level: bool = ''):
        """
        Метод предназначен для создания или редактирования КД
        :param new_pass_card:
        :param use_access_level:
        :return: str

          use_access_level: bool - Флаг, при выставлении которого в значение true
         при создании пропуска учитываются данные поля AccessLevels.
                                 По умолчанию значение флага – false,
                                  в этом случае используются данные поля EntryPoints модели Pass.
                                  стр. 29 документации пп 5.14
        """
        if not new_pass_card.entryPoints and not new_pass_card.accessLevels:
            raise BastionIntegrationError(message="Please input access level or entry points")

        response = await (await self._wrap_response(method="PUT",
                                                    url=f"/api/PutPass?{self._code_for_url}"
                                                        f"useAccessLevelsInsteadOfEntryPoints={use_access_level}",
                                                    data=new_pass_card)).text()
        if "info" in self.config.log:
            logger.info(response)
        return response

    async def return_pass_for_card(self, _pass: PassDto.ReturnPassForCardCode, ) -> str:
        """Метод предназначен для создания или редактирования КД,
         а также для создания/редактирования заявки на пропуск"""

        response = await (await self._wrap_response(method="PUT",
                                                    url=f"/api/PutPass?{self._code_for_url}"
                                                        f"useAccessLevelsInsteadOfEntryPoints=",
                                                    data=_pass)).text()
        if "info" in self.config.log:
            logger.info(response)
        return response

    async def get_pass(self, get_pass_info: PassDto.ReturnPass) -> List[PassDto]:
        """Метод предназначен для получения списка пропусков
        с фильтрацией по их статусу и типу с сервера"""
        response = await (await self._wrap_response(method="GET",
                                                    url=f"/api/GetPasses?{self._code_for_url}"
                                                        f"cardStatus={get_pass_info.card_status}&"
                                                        f"passType={get_pass_info.pass_type}&"
                                                        f"withoutPhoto={get_pass_info.without_photo}&"
                                                        f"startFrom={get_pass_info.start_numer}&"
                                                        f"maxCount={get_pass_info.max_count}")).json()
        model_list = await _handle_response(response, PassDto)
        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    async def get_passes_by_person(self, person_info: PersonDto, without_photo: bool) -> List[PassDto]:
        """Метод предназначен для получения списка пропусков любых статусов"""

        response = await (await self._wrap_response(method="GET",  # Dont change url parameters
                                                    url=f"/api/GetPassesByPerson?{self._code_for_url}"
                                                        f"name={person_info.name}&"
                                                        f"firstname={person_info.firstName}&"
                                                        f"secondname={person_info.secondName}&"
                                                        f"birthDate={person_info.birthDate}&"
                                                        f"withoutPhoto={without_photo}")).json()

        model_list = await _handle_response(response, PassDto)
        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    async def get_pass_by_card(self, card_code: str, without_photo: bool = "") -> List[PassDto]:
        """Метод предназначен для получения списка пропусков любых статусов, по которым когда-либо выдавалась карта
        without_photo: bool - true если фотографии возвращать не нужно"""
        response = await (await self._wrap_response(method="GET",
                                                    url=f"/api/GetPassesByCardCode?{self._code_for_url}"
                                                        f"cardCode={card_code}&"
                                                        f"withoutPhoto={without_photo}")).json()
        model_list = await _handle_response(response, PassDto)
        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    async def get_pass_count(self, card_status: int = "", pass_type: int = "") -> str:
        """Метод предназначен для получения общего количества пропусков"""
        response = await (await self._wrap_response(method="GET",
                                                    url=f"/api/GetPassCount?{self._code_for_url}"
                                                        f"cardStatus={card_status}&"
                                                        f"passType={pass_type}")).text()

        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>  <srvN> – код сервера, а <resultN> – результат выполнения операции.

    async def block_pass(self, card_code: str, block_reason: str) -> str:
        """Метод предназначен для блокировки КД"""
        response = await (await self._wrap_response(method="GET",
                                                    url=f"/api/BlockPass?{self._code_for_url}"
                                                        f"cardCode={card_code}&"
                                                        f"blockReason={block_reason}")).text()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>  <srvN> – код сервера, а <resultN> – результат выполнения операции.

    async def unblock_pass(self, card_code: str) -> str:
        """Метод предназначен для разблокировки КД"""
        response = await (await self._wrap_response(method="GET", url=f"/api/UnblockPass?{self._code_for_url}"
                                                                      f"cardCode={card_code}")).text()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>  <srvN> – код сервера, а <resultN> – результат выполнения операции.

    async def archive_pass(self, card_code: str) -> str:
        """Метод предназначен для переноса в архив карты доступа"""
        response = await (await self._wrap_response(method="GET", url=f"/api/ReturnPass?{self._code_for_url}"
                                                                      f"cardCode={card_code}")).text()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>  <srvN> – код сервера, а <resultN> – результат выполнения операции.

    async def issue_pass(self, person_info: PersonDto, pass_type: int, card_code: str) -> str:
        """Метод предназначен для выдачи КД по ранее созданной заявке на пропуск"""
        response = await (await self._wrap_response(method="GET",
                                                    url=f"/api/IssuePass?{self._code_for_url}"
                                                        f"name={person_info.name}&"
                                                        f"firstname={person_info.firstName}&"
                                                        f"secondname={person_info.secondName}&"
                                                        f"birthDate={person_info.birthDate}&"
                                                        f"passType={pass_type}&"
                                                        f"cardCode={card_code}")).text()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>  <srvN> – код сервера, а <resultN> – результат выполнения операции.

    async def get_material_pass_by_pass(self, pass_id: int) -> str:
        """Метод предназначен для выдачи материального пропуска по ранее созданной заявке на сервере"""
        response = await (
            await self._wrap_response(method="GET",
                                      url=f"/api/IssueMVPass?{self._code_for_url}passid={pass_id}")).json()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>

    async def ban_material_pass(self, pass_id: int) -> str:
        """Метод предназначен для изъятия материального пропуска на сервере"""
        response = await (await self._wrap_response(method="GET",
                                                    url=f"/api/WithdrawMVPass?{self._code_for_url}passid={pass_id}")).json()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>

    # ________________________________________________________________________________________________________

    async def get_organisation(self, org_filter: str = "") -> List[OrgDto]:
        """Метод предназначен для получения списка организаций"""
        response = await (await self._wrap_response(method="GET", url=f"/api/GetOrgs?{self._code_for_url}"
                                                                      f"filter={org_filter}")).json()
        model_list = await _handle_response(response, OrgDto)

        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    async def create_organization(self, organization: OrgDto) -> str:
        """Метод предназначен для добавления организации """
        response = await (
            await self._wrap_response(method="PUT", url=f"/api/PutOrg?{self._code_for_url}", data=organization)).text()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>

    async def update_organization(self, organization: OrgDto, organization_new_name: str) -> str:
        """Метод предназначен для переименования организации на всех серверах, добавленных в схему интеграции, либо на одном сервере, код которого передан в качестве входного параметра."""
        response = await (await self._wrap_response(method="POST",
                                                    url=f"/api/UpdateOrg?{self._code_for_url}"
                                                        f"orgNewName={organization_new_name}",
                                                    data=organization)).text()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>

    async def delete_organization(self, organization: OrgDto) -> str:
        """Метод предназначен для удаления организации (вместе со всеми дочерними организациями и подразделениями) на всех серверах, добавленных в схему интеграции, либо на одном сервере, код которого передан в качестве входного параметра."""
        response = await (
            await self._wrap_response(method="POST", url=f"/api/DeleteOrg?{self._code_for_url}",
                                      data=organization)).text()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>

    # ________________________________________________________________________________________________________

    async def get_department(self, department_name: str = "") -> List[DepartDto]:
        """Метод предназначен для получения списка подразделений (всех, либо принадлежащих организации, имя которой передано в качестве входного параметра)"""
        response = await (await self._wrap_response(method="GET",
                                                    url=f"/api/GetDeparts?{self._code_for_url}parentOrgName={department_name}")).json()
        model_list = await _handle_response(response, DepartDto)

        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    async def create_department(self, department: DepartDto) -> str:
        """Метод предназначен для добавления подразделения"""
        response = await (
            await self._wrap_response(method="PUT", url=f"/api/PutDepart?{self._code_for_url}", data=department)).text()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>

    async def update_department(self, department: DepartDto, new_department_name: str) -> str:
        """Метод предназначен для переименования подразделения"""
        response = await (await self._wrap_response(method="POST",
                                                    url=f"/api/UpdateDepart?{self._code_for_url}departNewName={new_department_name}",
                                                    data=department)).text()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>

    async def delete_department(self, department: DepartDto) -> str:
        """Метод предназначен для удаления подразделения"""
        response = await (await self._wrap_response(method="POST", url=f"/api/DeleteDepart?{self._code_for_url}",
                                                    data=department)).text()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>

    # ________________________________________________________________________________________________________

    async def put_material_pass(self, mat_value: MatValuePassDto, claim: bool = "", ) -> str:
        """Метод предназначен для создания или редактирования материального пропуска, а также для создания/редактирования заявки на материальный пропуск
        claim - Флаг, определяющий, будет создан выданный материальный пропуск, либо же будет создана заявка на пропуск
            """
        response = await (
            await self._wrap_response(method="PUT", url=f"/api/PutMVPass?{self._code_for_url}issuePass={claim}",
                                      data=mat_value)).text()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>

    async def get_material_pass(self, status: int = "") -> List[MatValuePassDto]:
        """Метод предназначен для получения списка материальных пропусков с фильтрацией по их статусу с сервера
        status: int - Статус возвращаемых материальных пропусков. Значение параметра может быть пустым, в этом случае будут возвращены пропуска с любым статусом
        """
        response = await(await self._wrap_response(method="GET",
                                                   url=f"/api/GetMVPasses?{self._code_for_url}status={status}")).json()
        model_list = await _handle_response(response, MatValuePassDto)

        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    async def get_material_pass_by_person(self, pass_dto: PassBriefDto) -> List[MatValuePassDto]:
        """Метод предназначен для получения списка материальных пропусков с фильтрацией по персональному пропуску с сервера, код которого передан в качестве входного параметра"""

        response = await (
            await self._wrap_response(method="POST", url=f"/api/GetMVPassesByPersonPass?{self._code_for_url}",
                                      data=pass_dto)).json()

        model_list = await _handle_response(response, MatValuePassDto)

        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    # ________________________________________________________________________________________________________

    async def put_car_pass(self, car_pass: CarPassDto, claim: bool = "") -> str:
        """Метод предназначен для создания или редактирования транспортного пропуска, а также для создания/редактирования заявки на транспортный пропуск"""
        response = await (
            await self._wrap_response(method="PUT", url=f"/api/PutCarPass?{self._code_for_url}issuePass={claim}",
                                      data=car_pass)).json()

        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>

    async def get_car_pass(self, status: int = "") -> List[CarPassDto]:
        """Метод предназначен для получения списка транспортных пропусков с фильтрацией по их статусу
        status: int - Статус возвращаемых транспортных пропусков. Значение параметра может быть пустым, в этом случае будут возвращены пропуска с любым статусом"""

        response = await (
            await self._wrap_response(method="GET",
                                      url=f"/api/GetCarPasses?{self._code_for_url}status={status}")).json()

        model_list = await _handle_response(response, CarPassDto)

        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    async def get_car_pass_by_person_pass(self, pass_dto: PassBriefDto) -> List[CarPassDto]:
        """Метод предназначен для получения списка транспортных пропусков с фильтрацией по персональному пропуску"""

        response = await (
            await self._wrap_response(method="POST", url=f"/api/GetCarPassesByPersonPass?{self._code_for_url}",
                                      data=pass_dto)).json()

        model_list = await _handle_response(response, CarPassDto)

        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    async def get_car_pass_by_claim(self, pass_id: int) -> str:
        """Метод предназначен для выдачи транспортного пропуска по ранее созданной заявке"""
        response = await (
            await self._wrap_response(method="GET",
                                      url=f"/api/IssueCarPass?{self._code_for_url}passid={pass_id}")).json()
        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>

    async def banned_car_pass(self, pass_id: int) -> str:
        """Метод предназначен для изъятия транспортного пропуска на сервере, код которого передан в качестве входного параметра."""
        response = await (await self._wrap_response(method="GET",
                                                    url=f"/api/WithdrawCarPass?{self._code_for_url}passid={pass_id}")).json()

        if "info" in self.config.log:
            logger.info(response)
        return response  # Метод возвращает строку в следующем формате: <srvN>:<resultN>

    # ________________________________________________________________________________________________________

    async def get_devices(self, driver_id: int = "", device_type: int = "") -> List[DeviceDto]:
        """Метод предназначен для получения набора устройств, добавленных в систему на сервере
        driver_id: int - Код типа драйвера, устройства которого необходимо получить. Значение параметра может быть пустым, в таком случае будут возвращены устройства всех драйверов
        device_type: int - Код типа устройства. В случае передачи непустого значения параметра будут возвращены устройства только данного типа. Значение параметра может быть пустым."""
        response = await ((await self._wrap_response(method="GET",
                                                     url=f"/api/GetDevices?{self._code_for_url}driverId={driver_id}&deviceType={device_type}"))).json()

        model_list = await _handle_response(response, DeviceDto)

        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    async def get_control_area(self) -> List[ControlAreaDto]:
        """Метод, предназначенный для получения информации об областях контроля"""
        response = await (
            await self._wrap_response(method="GET", url=f"/api/GetControlAreas?{self._code_for_url}")).json()
        model_list = await _handle_response(response, ControlAreaDto)

        if "info" in self.config.log:
            logger.info(model_list)
        return model_list

    async def get_access_point(self) -> List[AccessPointDto]:
        """Метод, предназначенный для получения информации об точках доступа"""
        response = await (
            await self._wrap_response(method="GET", url=f"/api/GetAccessPoints?{self._code_for_url}")).json()
        model_list = await _handle_response(response, AccessPointDto)

        if "info" in self.config.log:
            logger.info(model_list)
        return model_list
