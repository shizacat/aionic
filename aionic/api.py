import logging
from typing import Callable, List, Tuple, Optional
from xml.etree import ElementTree as ET

import aiohttp
from aiohttp_oauthlib import OAuth2Session
from oauthlib.oauth2 import (
    LegacyApplicationClient, TokenExpiredError, InvalidGrantError
)

from .exceptions import DnsApiException
from .models import (
    parse_record,
    NICService,
    NICZone,
    DNSRecord,
    SOARecord,
    NSRecord,
    ARecord,
    AAAARecord,
    CNAMERecord,
    MXRecord,
    TXTRecord,
)

"""
requrements.txt:
- aiohttp-oauthlib
oauthlib-3.1.1
"""

_RECORD_CLASSES_CAN_ADD = (
    ARecord,
    AAAARecord,
    CNAMERecord,
    TXTRecord,
)


class NICApi:
    """Async REST api library for nic.ru"""

    base_url_default = "https://api.nic.ru"

    __slots__ = (
        "_client_id",
        "_client_secret",
        "_username",
        "_password",
        "_scope",
        "_token",
        "_base_url",
        "_offline",
        "_token_updater_clb",
        "_timeout",
        "_default_service",
        "_default_zone",
        "logger",
        "_session",
    )

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        username: str = None,
        password: str = None,
        scope: str = None,
        token: str = None,
        default_service: str = None,
        default_zone: str = None,
        token_updater: Callable[[dict], None] = None,
        timeout: int = 600,
        base_url: str = None,
        offline: int = 3600,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._username = username
        self._password = password
        self._scope = scope
        self._token = token
        self._base_url = self.base_url_default if base_url is None else base_url
        self._offline = offline
        self._token_updater_clb = token_updater
        self._timeout = timeout
        self._default_service = default_service
        self._default_zone = default_zone

        # Logging setup
        self.logger = logging.getLogger(__name__)

        self._session = None

        # Setup
        self._setup()

    def _setup(self):
        self._session = OAuth2Session(
            client=LegacyApplicationClient(
                client_id=self._client_id, scope=self._scope
            ),
            auto_refresh_url=self.url_token,
            auto_refresh_kwargs={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "offline": self._offline,
            },
            token_updater=self._token_updater,
            token=self._token,
        )

    @property
    def url_token(self):
        return f"{self._base_url}/oauth/token"

    def _is_sequence(self, arg):
        """Returns if argument is list/tuple/etc. or not."""
        return (not hasattr(arg, 'strip') and
                hasattr(arg, '__getitem__') or
                hasattr(arg, '__iter__'))

    def _token_updater(self, token: dict):
        self._token = token
        if self._token_updater_clb is not None:
            self._token_updater_clb(token)

    def _url_create(self, rpath: str) -> str:
        return f"{self._base_url}/dns-master{rpath}"

    async def _request_data(
        self,
        *args,
        data_as_list: bool = False,
        data_none_except: bool = False,
        **kwargs
    ) -> ET.Element:
        response = await self._request(*args, **kwargs)
        status, error, data = self._parse_answer(await response.text())
        if status != "success":
            raise DnsApiException(error)
        if data_as_list:
            data = [] if data is None else data
        if data_none_except and data is None:
            raise DnsApiException(
                "Can't find <data> in response: {}".format(
                    await response.text()
                )
            )
        return data

    async def _request(
        self,
        method: str,
        rpath: str,
        check_status: bool = False,
        **kwargs
    ) -> aiohttp.ClientResponse:
        response = await self._session.request(
            method, self._url_create(rpath), timeout=self._timeout, **kwargs)

        # Check http error
        if check_status and not response.ok:
            raise DnsApiException(
                "HTTP Error. Body: {}".format(await response.text()))
        
        return response
   
    def _parse_answer(
            self, body: str
        ) -> Tuple[str, str, Optional[ET.Element]]:
        """Gets <data> from XML response.

        Arguments:
            body - xml as text

        Returns:
            (xml.etree.ElementTree.Element) <data> tag of response.
        """
        root = ET.fromstring(body)
        data = root.find('data')

        status = root.find('status')
        if status is None:
            raise DnsApiException(f"Can't find <status> in response: {body}")
        status = status.text

        error = ""
        for item in root.findall('errors/error'):
            error += " Code: {}. {}".format(
                item.attrib.get("code", ""), item.text)

        return status, error.strip(), data

    async def get_token(self):
        """Get token"""
        try:
            token = await self._session.fetch_token(
                token_url=self.url_token,
                username=self._username,
                password=self._password,
                client_id=self._client_id,
                client_secret=self._client_secret,
                offline=self._offline
            )
        except InvalidGrantError as e:
            raise DnsApiException(str(e))
        self._token_updater(token)

    async def services(self) -> List[NICService]:
        """Get services available for management.

        Returns:
            a list of NICService objects.
        """
        data = await self._request_data("GET", "/services", data_as_list=True)
        return [NICService.from_xml(service) for service in data]

    async def zones(self, service: str = None) -> List[NICZone]:
        """Get zones in service.

        Returns:
            a list of NICZone objects.
        """
        service = self._default_service if service is None else service
        if service is None:
            rpath = "/zones"
        else:
            rpath = f"/services/{service}/zones"
        data = await self._request_data("GET", rpath, data_as_list=True)
        return [NICZone.from_xml(zone) for zone in data]

    async def zonefile(self, service: str = None, zone: str = None) -> str:
        """Get zone file for single zone.

        Returns:
            a string with zonefile content.
        """
        service = self._default_service if service is None else service
        zone = self._default_zone if zone is None else zone
        response = await self._request(
            "GET", f"/services/{service}/zones/{zone}", check_status=True)
        return await response.text()

    async def records(
        self, service: str = None, zone: str = None
    ) -> List[DNSRecord]:
        """Get all records for single zone.

        Returns:
            a list with DNSRecord subclasses objects.
        """
        service = self._default_service if service is None else service
        zone = self._default_zone if zone is None else zone
        data = await self._request_data(
            "GET",
            f"/services/{service}/zones/{zone}/records",
            data_none_except=True
        )
        _zone = data.find('zone')
        assert _zone.attrib['name'] == zone
        return [parse_record(rr) for rr in _zone.findall('rr')]

    async def add_record(self, records, service: str = None, zone: str = None):
        """Adds records."""
        service = self._default_service if service is None else service
        zone = self._default_zone if zone is None else zone
        _records = list(records) if self._is_sequence(records) else [records]

        rr_list = []  # for XML representations

        for record in _records:
            if not isinstance(record, _RECORD_CLASSES_CAN_ADD):
                raise TypeError('{} is not a valid DNS record!'.format(record))
            record_xml = record.to_xml()
            rr_list.append(record_xml)
            self.logger.debug('Prepared for addition new record on service %s'
                              ' zone %s: %s', service, zone, record_xml)

        _xml = textwrap.dedent(
            """\
            <?xml version="1.0" encoding="UTF-8" ?>
            <request><rr-list>
            {}
            </rr-list></request>"""
        ).format('\n'.join(rr_list))

        await self._request_data(
            "PUT",
            f"/services/{service}/zones/{zone}/records",
            data=_xml
        )
        self.logger.debug('Successfully added %s records', len(rr_list))

    async def delete_record(
        self,
        record_id: int,
        service: str = None,
        zone: str = None
    ):
        """Deletes record by id."""
        service = self._default_service if service is None else service
        zone = self._default_zone if zone is None else zone

        self.logger.debug(
            'Deleting record #%s on service %s zone %s',
            record_id,
            service,
            zone
        )

        await self._request_data(
            "DELETE", f"/services/{service}/zones/{zone}/records/{record_id}")

        self.logger.debug('Record #%s deleted!', record_id)

    async def commit(self, service: str = None, zone: str = None):
        """Commits changes in zone."""
        service = self._default_service if service is None else service
        zone = self._default_zone if zone is None else zone
        await self._request_data(
            "POST", f"/services/{service}/zones/{zone}/commit")
        self.logger.debug('Changes committed!')

    async def rollback(self, service: str = None, zone: str = None):
        """Rolls back changes in zone."""
        service = self._default_service if service is None else service
        zone = self._default_zone if zone is None else zone
        await self._request_data(
            "POST", f"/services/{service}/zones/{zone}/rollback")
        self.logger.debug('Changes are rolled back!')