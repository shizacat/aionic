import unittest
import xml.etree.ElementTree as ET

import aionic.models as models

from tests.common import DataFixture


class TestModels(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_NICService(self):
        with self.subTest("create"):
            obj = models.NICService("", 1, 1, True, True, "", "", "")
            print(obj)

        with self.subTest("create from ET"):
            element = ET.fromstring(DataFixture.service)
            obj = models.NICService.from_xml(element)
            print(obj)
    
    def test_NICZone(self):
        with self.subTest("create from ET"):
            element = ET.fromstring(DataFixture.zones)
            obj = models.NICZone.from_xml(element)
            print(obj)

    def test_DNSRecord(self):
        with self.subTest("create from ET"):
            element = ET.fromstring(DataFixture.dns_record)
            obj = models.DNSRecord.from_xml(element)
            print("DNSRecord", obj)
        
        with self.subTest("To xml"):
            s = ET.tostring(obj.to_xml())
            print("xml", s)

    def test_SOARecord(self):
        with self.subTest("create from ET"):
            element = ET.fromstring(DataFixture.record_soa)
            obj = models.SOARecord.from_xml(element)
            print("SOARecord", obj)

        with self.subTest("To xml"):
            s = ET.tostring(obj.to_xml())
            print("xml", s)

    def test_NSRecord(self):
        with self.subTest("create from ET"):
            obj = models.NSRecord.from_xml(ET.fromstring(DataFixture.record_ns))
            print("NSRecord", obj)

        with self.subTest("To xml"):
            s = ET.tostring(obj.to_xml())
            print("xml", s)
    
    def test_ARecord(self):
        with self.subTest("create from ET"):
            obj = models.ARecord.from_xml(ET.fromstring(DataFixture.record_a))
            self.assertEqual(obj.id, DataFixture.record_a_answer["id"])
            self.assertEqual(obj.name, DataFixture.record_a_answer["name"])
            self.assertEqual(obj.ttl, DataFixture.record_a_answer["ttl"])
            self.assertEqual(obj.a, DataFixture.record_a_answer["a"])
            print("ARecord", obj)
        
        with self.subTest("To xml"):
            s = ET.tostring(obj.to_xml())
            print("xml", s)
    
    def test_AAAARecord(self):
        with self.subTest("create from ET"):
            data_service = """
                <rr>
                    <name>name</name>
                    <ttl>ttl</ttl>
                    <type>AAAA</type>
                    <aaaa>ipv6</aaaa> 
                </rr>
            """
            obj = models.AAAARecord.from_xml(ET.fromstring(data_service))
            print("AAAARecord", obj)
        
        with self.subTest("To xml"):
            s = ET.tostring(obj.to_xml())
            print("xml", s)
    
    def test_CNAMERecord(self):
        with self.subTest("create from ET"):
            data_service = """
                <rr>
                    <name>name</name>
                    <ttl>ttl</ttl>
                    <type>CNAME</type>
                    <cname>
                        <name>canonical</name>
                    </cname>
                </rr>
            """
            obj = models.CNAMERecord.from_xml(ET.fromstring(data_service))
            print("CNAMERecord", obj)
        
        with self.subTest("To xml"):
            s = ET.tostring(obj.to_xml())
            print("xml", s)
    
    def test_MXRecord(self):
        with self.subTest("create from ET"):
            data_service = """
                <rr>
                    <name>name</name>
                    <ttl>ttl</ttl>
                    <type>MX</type>
                    <mx>
                        <preference>10</preference>
                        <exchange>
                            <name>mail.test.ru.</name>
                        </exchange>
                    </mx>
                </rr>
            """
            obj = models.MXRecord.from_xml(ET.fromstring(data_service))
            print("MXRecord", obj)
        
        with self.subTest("To xml"):
            s = ET.tostring(obj.to_xml())
            print("xml", s)
    
    def test_TXTRecord(self):
        with self.subTest("create from ET"):
            data_service = """
                <rr>
                    <name>name</name>
                    <ttl>ttl</ttl>
                    <type>TXT</type>
                    <txt>
                        <string>Location this machine: City</string>
                    </txt>
                </rr>
            """
            obj = models.TXTRecord.from_xml(ET.fromstring(data_service))
            print("TXTRecord", obj)
        
        with self.subTest("To xml"):
            s = ET.tostring(obj.to_xml())
            print("xml", s)
    
    def test_SRVRecord(self):
        with self.subTest("create from ET"):
            data_service = """
                <rr>
                    <name>name</name>
                    <ttl>ttl</ttl>
                    <type>SRV</type>
                    <srv>
                        <priority>10</priority>
                        <weight>40</weight>
                        <port>5060</port>
                        <target>
                            <name>target</name>
                        </target>
                    </srv> 
                </rr>
            """
            obj = models.SRVRecord.from_xml(ET.fromstring(data_service))
            print("SRVRecord", obj)
        
        with self.subTest("To xml"):
            s = ET.tostring(obj.to_xml())
            print("xml", s)
    
    def test_PTRRecord(self):
        with self.subTest("create from ET"):
            data_service = """
                <rr>
                    <name>1.0.168.192.in-addr</name>
                    <ttl>86400</ttl>
                    <type>PTR</type>
                    <ptr>
                        <name>www.test.ru.</name>
                    </ptr> 
                </rr>
            """
            obj = models.PTRRecord.from_xml(ET.fromstring(data_service))
            print("PTRRecord", obj)
        
        with self.subTest("To xml"):
            s = ET.tostring(obj.to_xml())
            print("xml", s)
    
    def test_create(self):
         with self.subTest("create from ET"):
            data_service = """
                <rr>
                    <name>1.0.168.192.in-addr</name>
                    <ttl>86400</ttl>
                    <type>PTR</type>
                    <ptr>
                        <name>www.test.ru.</name>
                    </ptr> 
                </rr>
            """
            obj = models.DNSRecord.create(ET.fromstring(data_service))
            self.assertIsInstance(obj, models.PTRRecord)
