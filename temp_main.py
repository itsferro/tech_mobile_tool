import win32print
import win32ui
import win32gui
import win32con
from PIL import Image
import qrcode
import requests
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.diagnostics import DiagnosticsService


def get_idevices_list():
    url = "https://api.ipsw.me/v4/devices"
    headers = {
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error retrieving idevices list: {e}")
        return None


def find_device_name(m_Names_mapping, identifier):
    for device in m_Names_mapping:
        if device.get("identifier") == identifier:
            return device.get("name")
    return None


def bytes_to_gb(bytes_value) -> int:
    #return int(bytes_value / (1024 ** 3))
    return int(bytes_value / (1000 ** 3))



m_Names_mapping = get_idevices_list()


color_mapping = {
    '#3b3b3c': 'Black',
    '#ffffff': 'white',
    '#ff3b30': 'red',
    '#ff9500': 'Orange',
    '#ffcc00': 'Yellow',
    '#4cd964': 'Green',
    '#5ac8fa': 'Blue',
    '#007aff': 'LightBlue',
    '#5856d6': 'Purple',
    '#ff2d55': 'Pink',
    '#8e8e93': 'Gray',
    '#c69c6d': 'Gold',
    '#d0d1d2': 'Silver',
    '1': 'Black',
    '2': 'white',
    '3': 'Gold',
    '4': 'Pink',
    '5': 'Gray',
    '6': 'red',
    '7': 'Yellow',
    '8': 'Orange',
    '9': 'Blue',
    '17': 'Purple',
    '18': 'Green',
    }

class Idevice:
    m_Name = None
    m_Number = None
    imei = None
    color = None
    disk_cap = None
    memory_cap = None
    battery_SOH = None

    def printer_string(self):
        return f"{self.m_Name} - {self.m_Number} - {self.imei} - {self.color} - {self.disk_cap} - {self.memory_cap} - {self.battery_SOH}"

    def __str__(self):
        return f"iDevice INFO:\n- m_Name: {self.m_Name}\n- m_Number: {self.m_Number}\n- imei: {self.imei}\n- color: {self.color}\n- disk_cap: {self.disk_cap}\n- memory_cap: {self.memory_cap}\n- battery_capacity: {self.battery_SOH}%"


lockdown = create_using_usbmux(serial=None, autopair=False)
device_info = lockdown.all_values

total_disk_cap = lockdown.get_value(domain="com.apple.disk_usage", key="TotalDiskCapacity")
print(f"_____________________________")
total_disk_cap_GB = bytes_to_gb(total_disk_cap)

diag = DiagnosticsService(lockdown=lockdown)
battery = diag.get_battery()
battery_SOH = (battery["NominalChargeCapacity"] / battery["DesignCapacity"]) * 100

iDevice = Idevice()
iDevice.m_Name = find_device_name(m_Names_mapping, device_info["ProductType"])
iDevice.m_Number = device_info["ModelNumber"]
iDevice.imei = device_info["InternationalMobileEquipmentIdentity"]
iDevice.color = color_mapping[device_info["DeviceColor"]]
iDevice.disk_cap = f"{total_disk_cap_GB}GB"
iDevice.battery_SOH = f"{round(battery_SOH)}%"

print(iDevice)
print("_______________________")
print(iDevice.printer_string())

#______________print________________

printer_name = win32print.GetDefaultPrinter()
hprinter = win32print.OpenPrinter(printer_name)
printer_info = win32print.GetPrinter(hprinter, 2)
pdc = win32ui.CreateDC()
pdc.CreatePrinterDC(printer_name)
pdc.StartDoc('Label Print')
pdc.StartPage()

font = win32ui.CreateFont({
    "name": "Arial",
    "height": 32,  # Adjust font size to fit in the label
    "weight": 700  # Bold
})
pdc.SelectObject(font)

border = {"left": 10, "top": 10, "right": 460, "bottom": 310}

def print_data_3(iDevice, border):
    pdc.TextOut(border.get("left"), border.get("top"), f"{iDevice.m_Name}")
    #len(iDevice.m_Number)
    pdc.TextOut(border.get("left"), (border.get("top") + 35 * 1), f"{iDevice.color}")
    pdc.TextOut(border.get("left"), (border.get("top") + 35 * 2), f"{iDevice.disk_cap}")
    pdc.TextOut((border.get("left") + (len(iDevice.disk_cap) * 30)), (border.get("top") + 35 * 2), f"{iDevice.battery_SOH}")
    pdc.TextOut(border.get("left"), (border.get("bottom") - 30), f"{iDevice.imei}")



print_data_3(iDevice, border)


def print_logo(w, h, border):
    img = Image.open("tech_mobile_620x620.jpg")
    new_width = w  # Change this to your desired width
    new_height = h  # Change this to your desired height
    img = img.resize((new_width, new_height), Image.LANCZOS)  # Resize smoothly
    img = img.convert("RGB")
    img.save("logo.bmp")

    logo_path = "logo.bmp"
    bitmap = win32gui.LoadImage(0, logo_path, win32gui.IMAGE_BITMAP, 0, 0, win32gui.LR_LOADFROMFILE)

    if not bitmap:
        raise Exception("Failed to load bitmap image!")


    hbm = win32ui.CreateBitmapFromHandle(bitmap)

    # Get image size
    bm_info = hbm.GetInfo()
    width, height = bm_info["bmWidth"], bm_info["bmHeight"]

    # Select the image into the device context and print it
    mem_dc = pdc.CreateCompatibleDC()
    mem_dc.SelectObject(hbm)
    pdc.BitBlt(((border.get("right") - w), (border.get("top"))), (width, height), mem_dc, (0, 0), win32con.SRCCOPY)


def print_battery_icon(w, h, border):
    img = Image.open("ios-battery-full.jpg")
    new_width = w  # Change this to your desired width
    new_height = h  # Change this to your desired height
    img = img.resize((new_width, new_height), Image.LANCZOS)  # Resize smoothly
    img = img.convert("RGB")
    img.save("logo.bmp")

    logo_path = "logo.bmp"
    bitmap = win32gui.LoadImage(0, logo_path, win32gui.IMAGE_BITMAP, 0, 0, win32gui.LR_LOADFROMFILE)

    if not bitmap:
        raise Exception("Failed to load bitmap image!")


    hbm = win32ui.CreateBitmapFromHandle(bitmap)

    # Get image size
    bm_info = hbm.GetInfo()
    width, height = bm_info["bmWidth"], bm_info["bmHeight"]

    # Select the image into the device context and print it
    mem_dc = pdc.CreateCompatibleDC()
    mem_dc.SelectObject(hbm)
    pdc.BitBlt(((border.get("left") + (len(iDevice.disk_cap) * 30) + (len(iDevice.battery_SOH) * 30) - 30), ((border.get("top") + 35 * 2) - 2)), (width, height), mem_dc, (0, 0), win32con.SRCCOPY)


def print_qrcode(imei, size, border):
    # Generate and print QR Code
    qr_data = str(imei)
    qr = qrcode.make(qr_data)
    qr = qr.resize((size, size), Image.LANCZOS)  # Resize QR code
    qr = qr.convert("RGB")
    qr.save("qrcode.bmp")

    bitmap_qr = win32gui.LoadImage(0, "qrcode.bmp", win32gui.IMAGE_BITMAP, 0, 0, win32gui.LR_LOADFROMFILE)
    if not bitmap_qr:
        raise Exception("Failed to load QR code image!")

    hbm_qr = win32ui.CreateBitmapFromHandle(bitmap_qr)
    bm_info_qr = hbm_qr.GetInfo()
    qr_width, qr_height = bm_info_qr["bmWidth"], bm_info_qr["bmHeight"]

    mem_dc_qr = pdc.CreateCompatibleDC()
    mem_dc_qr.SelectObject(hbm_qr)
    pdc.BitBlt(((border.get("left") - 20), (border.get("bottom") - (30 + size))), (qr_width, qr_height), mem_dc_qr, (0, 0), win32con.SRCCOPY)


print_logo(150, 150, border)
print_battery_icon(64, 30, border)
print_qrcode(iDevice.imei, 150, border)

pdc.EndPage()
pdc.EndDoc()
pdc.DeleteDC()
win32print.ClosePrinter(hprinter)

#______________print________________
