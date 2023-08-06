import base64

open_file = open("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\DevExpress.XtraBars.v22.2\\v4.0_22.2.4.0__b88d1754d700e49a\\DevExpress.XtraBars.v22.2.dll", "rb")
b64str = base64.b64encode(open_file.read())
open_file.close()
write_data = format(b64str)
f = open("output.txt", "w+")
f.write(write_data)  # 生成ASCII码
f.close()