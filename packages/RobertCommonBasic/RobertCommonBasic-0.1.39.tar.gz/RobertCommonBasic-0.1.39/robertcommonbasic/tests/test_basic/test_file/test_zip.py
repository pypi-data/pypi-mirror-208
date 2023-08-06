from robertcommonbasic.basic.file.zip import *
from io import BytesIO

def test_zip_files():
    files = [r'E:\RNB\JK\raofeng\7d30e594-f86c-49ee-a2c3-425ff1133774_20230228131305_power_station.csv', r'E:\RNB\JK\raofeng\94408f5b-6a1c-4930-850b-be095dd008a9_20230228132505_power_station.csv']
    zip_files(r"E:\text.zip", files)
    print()


def test_zip_files1():
    datas = BytesIO()
    with pyzipper.AESZipFile(datas, 'a', compression=pyzipper.ZIP_DEFLATED) as zip_file:
        zip_file.write(r'E:\RNB\JK\raofeng\7d30e594-f86c-49ee-a2c3-425ff1133774_20230228131305_power_station.csv', 'aa.csv')

    open(r'E:/test.zip', 'wb').write(datas.getvalue())
    print()


test_zip_files1()