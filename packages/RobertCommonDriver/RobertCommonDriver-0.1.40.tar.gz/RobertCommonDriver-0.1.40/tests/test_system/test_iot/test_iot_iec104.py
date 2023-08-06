import time
from robertcommondriver.system.iot.iot_iec104 import IOTIEC104


def logging_print(**kwargs):
    print(kwargs)


def test_read():
    dict_config = {'host': '192.168.1.184', 'port': 2404, 'timeout': 4}
    dict_point = {}
    dict_point['iec1'] = {'point_writable': True, 'point_name': 'iec1', 'point_type': 1, 'point_address': 1, 'point_scale': '1'}
    dict_point['iec2'] = {'point_writable': True, 'point_name': 'iec2', 'point_type': 13, 'point_address': 16386, 'point_scale': '1'}

    client = IOTIEC104(configs = dict_config, points= dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            result = client.read(names=list(dict_point.keys()))
            print(result)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(1)


def test_parse():
    #r = IOTIEC104.APDU(bytes.fromhex('68 0E 06 00 08 00 64 01 06 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'))
    r = IOTIEC104.APDU(bytes.fromhex('68 0E 02 00 02 00 01 82 14 00 01 00 01 00 00 01 68 0E 04 00 02 00 64 01 0A 00 01 00 00 00 00 14'))
    #r = IOTIEC104.APDU(bytes.fromhex('68 0E 02 00 02 00 01 82 14 00 01 00 01 00 00 01'))
    print(r.info())


test_read()