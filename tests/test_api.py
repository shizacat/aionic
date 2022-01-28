import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from xml.etree import ElementTree as ET

# import pytest
from aiohttp import web, ClientResponse
from aiohttp.test_utils import AioHTTPTestCase, make_mocked_request, TestServer

from aionic import NICApi, models
from aionic.exceptions import DnsApiException
from tests.common import get_xml, DataFixture

# async def previous(request):
#     return web.Response(body=b'thanks for the data')


# async def test_api(aiohttp_server):
#     app = web.Application()
#     # route table
#     app.router.add_get('/', previous)

#     server = await aiohttp_server(app)
#     obj = NICApi("", "", "", "", base_url=f"https://localhost:{server.port}")
#     await obj._request_data("GET", "/")


class ApiTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.obj = NICApi("", "", "", "", "")

    def test_url_token(self):
        self.obj.url_token

    def test__url_create(self):
        self.obj._url_create("test")

    @patch("aionic.NICApi._request", new_callable=AsyncMock)
    async def test__request_data(self, req):
        req.return_value = get_xml()
        r = await self.obj._request_data()
        self.assertIsInstance(r, ET.Element)

    @patch("aionic.NICApi._request", new_callable=AsyncMock)
    async def test_api_services(self, req):
        req.return_value = get_xml(DataFixture.service)
        r = await self.obj.services()
        self.assertIsInstance(r[0], models.NICService)

    @patch("aionic.NICApi._request", new_callable=AsyncMock)
    async def test_api_zones(self, req):
        req.return_value = get_xml(DataFixture.zones)
        r = await self.obj.zones()
        self.assertIsInstance(r[0], models.NICZone)
    
    @patch("aionic.NICApi._request", new_callable=AsyncMock)
    async def test_api_records(self, req):
        with self.subTest("Success"):
            req.return_value = get_xml(DataFixture.record_soa, is_zone=True)
            r = await self.obj.records("", "example.ru")
            self.assertIsInstance(r[0], models.DNSRecord)
        
        with self.subTest("Error zone"), self.assertRaises(DnsApiException):
            req.return_value = get_xml(DataFixture.record_soa, is_zone=True)
            r = await self.obj.records("", "zone.none")

    @patch("aionic.NICApi._request", new_callable=AsyncMock)
    async def test_api_add_record(self, req):
        req.return_value = get_xml()
        await self.obj.add_record(
            [models.ARecord.from_xml(ET.fromstring(DataFixture.record_a))],
            "",
            ""
        )
    
    @patch("aionic.NICApi._request", new_callable=AsyncMock)
    async def test_api_delete_record(self, req):
        req.return_value = get_xml()
        await self.obj.delete_record(1, "", "")

    @patch("aionic.NICApi._request", new_callable=AsyncMock)
    async def test_api_commit(self, req):
        req.return_value = get_xml()
        await self.obj.commit("", "")

    @patch("aionic.NICApi._request", new_callable=AsyncMock)
    async def test_api_rollback(self, req):
        req.return_value = get_xml()
        await self.obj.rollback("", "")
    
    @patch("aionic.NICApi._request", new_callable=AsyncMock)
    async def test_api_zonefile(self, req):
        req.return_value = ""
        await self.obj.zonefile("", "")

    def test__is_sequence(self):
        """Check _is_sequence"""
        data = [
            ("str", False),
            (["test"], True),
            (("test",), True)
        ]
        for x, y in data:
            r = self.obj._is_sequence(x)
            assert r == y
