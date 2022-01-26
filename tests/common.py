

def get_xml(data: str = "", is_zone: bool = False) -> str:
    zone_name = "example.ru"
    if is_zone:
        data = f"""
        <zone admin="123/NIC-REG" enable="true" has-changes="false"
            has-primary="true" id="227642"
            idn-name="{zone_name}" name="{zone_name}"
            payer="123/NIC-REG" service="myservice"
        >
            {data}
        </zone>
        """
    base = f"""
    <?xml version="1.0" encoding="UTF-8" ?>
    <response>
        <status>success</status>
        <data>
            {data}
        </data>
    </response>
    """
    return base


class DataFixture:
    service = """
        <service admin="123/NIC-REG" domains-limit="12" domains-num="5"
            enable="true" has-primary="false" name="testservice"
            payer="123/NIC-REG" tariff="Secondary L" rr_num="49"
        />
    """ 

    zones = """
        <zone admin="123/NIC-REG" enable="true" has-changes="false"
            has-primary="true" id="227642" idn-name="example.ru"
            name="example.ru" payer="123/NIC-REG" service="myservice"
        />
    """

    dns_record = """
        <rr id="210074">
            <name>@</name><idn-name>@</idn-name>
        </rr>
    """

    record_soa = """
        <rr id="210074">
            <name>@</name>
            <idn-name>@</idn-name>
            <type>SOA</type>
            <soa>
                <mname>
                    <name>ns3-l2.nic.ru.</name>
                    <idn-name>ns3-l2.nic.ru.</idn-name>
                </mname>
                <rname>
                    <name>dns.nic.ru.</name>
                    <idn-name>dns.nic.ru.</idn-name>
                </rname>
                <serial>2011112002</serial>
                <refresh>1440</refresh>
                <retry>3600</retry>
                <expire>2592000</expire>
                <minimum>600</minimum>
            </soa>
        </rr>
    """

    record_ns = """
        <rr>
            <name>name</name>
            <ttl>ttl</ttl>
            <type>NS</type>
            <ns>
                <name>ns-name-uuu</name>
            </ns>
        </rr>
    """

    record_a = """
        <rr>
            <name>name</name>
            <ttl>ttl</ttl>
            <type>A</type>
            <a>IP</a>
        </rr>
    """