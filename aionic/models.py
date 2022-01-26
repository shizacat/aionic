"""nic_api - classes for entities returned by API."""

import sys
from xml.etree import ElementTree
from xml.etree import ElementTree as ET
from typing import Optional, Union, Any, _GenericAlias, List, Tuple


class GenericXML:
    def __repr__(self):
        return repr(vars(self))

    @staticmethod
    def _str2bool(value: str) -> bool:
        """Converts a string to a bool."""
        return {'true': True, 'false': False}[value.lower()]


# *****************************************************************************
# Model of service
#

class NICService(GenericXML):
    """Model of service object"""

    def __init__(
        self,
        admin: str,
        domains_limit: int,
        domains_num: int,
        enable: bool,
        has_primary: bool,
        name: str,
        payer: str,
        tariff: str,
        rr_limit: Optional[int] = None,
        rr_num: Optional[int] = None
    ):
        self.admin = admin
        self.domains_limit = int(domains_limit)
        self.domains_num = int(domains_num)
        self.enable = enable
        self.has_primary = has_primary
        self.name = name
        self.payer = payer
        self.tariff = tariff
        if rr_limit is not None:
            self.rr_limit = int(rr_limit)
        if rr_num is not None:
            self.rr_num = int(rr_num)

    @classmethod
    def from_xml(cls, obj: ET.Element):
        kwargs = {k.replace('-', '_'): v for k, v in obj.attrib.items()}
        kwargs['enable'] = cls._str2bool(kwargs['enable'])
        kwargs['has_primary'] = cls._str2bool(kwargs['has_primary'])
        return cls(**kwargs)


# *****************************************************************************
# Model of DNS zone
#

class NICZone(GenericXML):
    """Model of zone object."""

    def __init__(
        self,
        admin: str,
        enable: bool,
        has_changes: bool,
        has_primary: bool,
        id_: int,
        idn_name: str,
        name: str,
        payer: str,
        service: str
    ):
        self.admin = admin
        self.enable = enable
        self.has_changes = has_changes
        self.has_primary = has_primary
        self.id = int(id_)
        self.idn_name = idn_name
        self.name = name
        self.payer = payer
        self.service = service

    def to_xml(self):
        # TODO: add implementation if needed
        raise NotImplementedError('Not implemented!')

    @classmethod
    def from_xml(cls, obj: ET.Element):
        kwargs = {k.replace('-', '_'): v for k, v in obj.attrib.items()}

        kwargs['id_'] = kwargs['id']
        kwargs.pop('id')

        kwargs['enable'] = cls._str2bool(kwargs['enable'])
        kwargs['has_changes'] = cls._str2bool(kwargs['has_changes'])
        kwargs['has_primary'] = cls._str2bool(kwargs['has_primary'])
        return cls(**kwargs)


# *****************************************************************************
# Models of DNS records
#
# Each model has __init__() method that loads data into object by direct
# assigning and a class method from_xml() that constructs the object from
# an ElementTree.Element.
#
# Each model has to_xml() method that returns (str) an XML representation
# of the current record.
# *****************************************************************************

class DNSRecord:
    """Base model of NIC.RU DNS record."""

    type_name: str = None

    def __init__(
        self,
        id_:int = None,
        name: str = "",
        idn_name: str = None,
        ttl: str = None,
        **kwargs
    ):
        self.id = int(id_) if id_ is not None else None
        self.name = name
        self.idn_name = idn_name if idn_name is not None else name
        self.ttl = ttl

        if self.id == 0:
            raise ValueError('Invalid record ID!')

    def __repr__(self):
        return repr(vars(self))
    
    def to_xml(self, base_name: str = "rr") -> ET.Element:
        root = ElementTree.Element(base_name)

        if self.id is not None:
            root.attrib['id'] = self.id

        _name = ElementTree.SubElement(root, 'name',)
        _name.text = self.name

        if self.idn_name is not None:
            _idn_name = ElementTree.SubElement(root, 'idn-name')
            _idn_name.text = self.idn_name

        if self.ttl is not None:
            _ttl = ElementTree.SubElement(root, 'ttl')
            _ttl.text = str(self.ttl)

        if self.type_name is not None:
            _type = ET.SubElement(root, 'type')
            _type.text = self.type_name

        return root

    @classmethod
    def from_xml(cls, obj: ET.Element):
        if cls.type_name is not None and obj.find('type').text != cls.type_name:
            raise ValueError(f"Record is not a {cls.type_name} record!")

        return cls(**cls._get_kwargs(obj))
    
    @classmethod
    def _get_kwargs(cls, obj: ET.Element) -> dict:
        kwargs = {}
        kwargs["id"] = obj.attrib.get("id")
        kwargs["name"] = obj.find("name").text
        if obj.find("idn-name") is not None:
            kwargs["idn_name"] = obj.find("idn-name").text
        if obj.find("ttl") is not None:
            kwargs["ttl"] = obj.find("ttl").text
        return kwargs
    
    @classmethod
    def _find_field(cls, obj: ET.Element, path: str, key: str) -> Any:
        el = obj.find(f"{path}{key}")
        if el is None:
            raise ValueError(f"The field {key} not found")
        return el
    
    @classmethod
    def create(cls, obj: ET.Element) -> "DNSRecord":
        """Parses record XML representation to one of DNSRecord subclasses"""
        _type = obj.find('type').text
        for subcls in cls.__subclasses__():
            if subcls.type_name == _type:
                return subcls.from_xml(obj)
        raise TypeError(f"Unknown record type: {_type}")


class SOARecord(DNSRecord):
    """Model of SOA record."""

    type_name: str = "SOA"

    def __init__(
        self,
        serial: int,
        refresh: int,
        retry: int,
        expire: int,
        minimum: int,
        mname: DNSRecord,
        rname: DNSRecord,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.serial = int(serial)
        self.refresh = int(refresh)
        self.retry = int(retry)
        self.expire = int(expire)
        self.minimum = int(minimum)
        self.mname = mname
        self.rname = rname

    @classmethod
    def _get_kwargs(cls, obj: ET.Element) -> dict:
        kwargs = super()._get_kwargs(obj)

        for field in ('serial', 'refresh', 'retry', 'expire', 'minimum'):
            kwargs[field] = cls._find_field(obj, "soa/", field).text
        for field in ("mname", "rname"):
            kwargs[field] = DNSRecord.from_xml(
                cls._find_field(obj, "soa/", field)
            )
        return kwargs
    
    def to_xml(self) -> ET.Element:
        root = super().to_xml()

        _soa = ET.SubElement(root, 'soa')
        _serial = ET.SubElement(_soa, 'serial')
        _serial.text = str(self.serial)
        _refresh = ET.SubElement(_soa, 'refresh')
        _refresh.text = str(self.refresh)
        _retry = ET.SubElement(_soa, 'retry')
        _retry.text = str(self.retry)
        _expire = ET.SubElement(_soa, 'expire')
        _expire.text = str(self.expire)
        _minimum = ET.SubElement(_soa, 'minimum')
        _minimum.text = str(self.minimum)
        _soa.append(self.mname.to_xml("mname"))
        _soa.append(self.rname.to_xml("rname"))

        return root


class NSRecord(DNSRecord):
    """Model of NS record."""

    type_name: str = "NS"

    def __init__(self, ns_name: str, **kwargs):
        super().__init__(**kwargs)
        self.ns_name = ns_name

    @classmethod
    def _get_kwargs(cls, obj: ET.Element) -> dict:
        kwargs = super()._get_kwargs(obj)
        kwargs["ns_name"] = cls._find_field(obj, "ns/", "name").text
        return kwargs
    
    def to_xml(self) -> ET.Element:
        root = super().to_xml()

        _ns = ET.SubElement(root, 'ns')
        _ns_name = ET.SubElement(_ns, 'name')
        _ns_name.text = self.ns_name

        return root


class ARecord(DNSRecord):
    """Model of A record."""

    type_name: str = "A"

    def __init__(self, a: str, **kwargs):
        super().__init__(**kwargs)
        self.a = a

    @classmethod
    def _get_kwargs(cls, obj: ET.Element) -> dict:
        kwargs = super()._get_kwargs(obj)
        kwargs["a"] = cls._find_field(obj, "", "a").text
        return kwargs

    def to_xml(self) -> ET.Element:
        root = super().to_xml()

        _a = ET.SubElement(root, 'a')
        _a.text = self.a

        return root


class AAAARecord(DNSRecord):
    """Model of AAAA record."""

    type_name: str = "AAAA"

    def __init__(self, aaaa: str, **kwargs):
        super().__init__(**kwargs)
        self.aaaa = aaaa

    @classmethod
    def _get_kwargs(cls, obj: ET.Element) -> dict:
        kwargs = super()._get_kwargs(obj)
        kwargs["aaaa"] = cls._find_field(obj, "", "aaaa").text
        return kwargs
    
    def to_xml(self) -> ET.Element:
        root = super().to_xml()

        _aaaa = ET.SubElement(root, 'aaaa')
        _aaaa.text = self.aaaa

        return root


class CNAMERecord(DNSRecord):
    """Model of CNAME record."""

    type_name: str = "CNAME"

    def __init__(self, cname: str, **kwargs):
        super().__init__(**kwargs)
        self.cname = cname

    @classmethod
    def _get_kwargs(cls, obj: ET.Element) -> dict:
        kwargs = super()._get_kwargs(obj)
        kwargs["cname"] = cls._find_field(obj, "cname/", "name").text
        return kwargs
    
    def to_xml(self) -> ET.Element:
        root = super().to_xml()

        _cname = ET.SubElement(root, 'cname')
        _name = ET.SubElement(_cname, 'name')
        _name.text = self.cname

        return root


class MXRecord(DNSRecord):
    """Model of MX record."""

    type_name: str = "MX"

    def __init__(self, preference: int, exchange: str, **kwargs):
        super().__init__(**kwargs)
        self.preference = int(preference)
        self.exchange = exchange
    
    @classmethod
    def _get_kwargs(cls, obj: ET.Element) -> dict:
        kwargs = super()._get_kwargs(obj)
        kwargs["preference"] = cls._find_field(obj, "mx/", "preference").text
        kwargs["exchange"] = cls._find_field(obj, "mx/exchange/", "name").text
        return kwargs
    
    def to_xml(self) -> ET.Element:
        root = super().to_xml()

        _mx = ET.SubElement(root, 'mx')
        _preference = ET.SubElement(_mx, 'preference')
        _preference.text = str(self.preference)
        _exchange = ET.SubElement(_mx, 'exchange')
        _name = ET.SubElement(_exchange, 'name')
        _name.text = self.exchange

        return root


class TXTRecord(DNSRecord):
    """Model of TXT record."""

    type_name: str = "TXT"

    def __init__(self, txt: str, **kwargs):
        super().__init__(**kwargs)
        self.txt = txt

    @classmethod
    def _get_kwargs(cls, obj: ET.Element) -> dict:
        kwargs = super()._get_kwargs(obj)

        txt = [string.text for string in obj.findall("txt/string")]
        if len(txt) == 1:
            kwargs["txt"] = txt[0]

        return kwargs
    
    def to_xml(self) -> ET.Element:
        root = super().to_xml()

        _txt = ET.SubElement(root, 'txt')
        _string = ET.SubElement(_txt, 'string')
        _string.text = self.txt

        return root


class SRVRecord(DNSRecord):
    """Model of TXT record."""

    type_name: str = "SRV"

    def __init__(
        self, priority: int, weight: int, port: int, target: str, **kwargs
    ):
        super().__init__(**kwargs)
        self.priority = int(priority)
        self.weight = int(weight)
        self.port = int(port)
        self.target = target

    @classmethod
    def _get_kwargs(cls, obj: ET.Element) -> dict:
        kwargs = super()._get_kwargs(obj)

        kwargs["priority"] = cls._find_field(obj, "srv/", "priority").text
        kwargs["weight"] = cls._find_field(obj, "srv/", "weight").text
        kwargs["port"] = cls._find_field(obj, "srv/", "port").text
        kwargs["target"] = cls._find_field(obj, "srv/target/", "name").text

        return kwargs
    
    def to_xml(self) -> ET.Element:
        root = super().to_xml()

        _srv = ET.SubElement(root, 'srv')
        _priority = ET.SubElement(_srv, 'priority')
        _priority.text = str(self.priority)
        _weight = ET.SubElement(_srv, 'weight')
        _weight.text = str(self.weight)
        _port = ET.SubElement(_srv, 'port')
        _port.text = str(self.port)
        _target = ET.SubElement(_srv, 'target')
        _name = ET.SubElement(_target, 'name')
        _name.text = self.target

        return root


class PTRRecord(DNSRecord):
    """Model of TXT record."""

    type_name: str = "PTR"

    def __init__(self, ptr_name: str, **kwargs):
        super().__init__(**kwargs)
        self.ptr_name = ptr_name

    @classmethod
    def _get_kwargs(cls, obj: ET.Element) -> dict:
        kwargs = super()._get_kwargs(obj)
        kwargs["ptr_name"] = cls._find_field(obj, "ptr/", "name").text
        return kwargs
    
    def to_xml(self) -> ET.Element:
        root = super().to_xml()

        _ptr = ET.SubElement(root, 'ptr')
        _name = ET.SubElement(_ptr, 'name')
        _name.text = self.ptr_name

        return root
