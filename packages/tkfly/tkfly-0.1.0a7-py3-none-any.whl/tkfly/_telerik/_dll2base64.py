import base64

open_file = open("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.RadToastNotification\\v4.0_2023.1.314.40__5bb2a467cbec794e\\Telerik.WinControls.RadToastNotification.dll", "rb")
b64str = base64.b64encode(open_file.read())
open_file.close()
write_data = format(b64str)
f = open("output.txt", "w+")
f.write(write_data)  # 生成ASCII码
f.close()