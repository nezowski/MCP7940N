import serial
import time
from time import strftime
import tkinter as tk
from tkinter import ttk

serial_port = 'COM4'
baud_rate = 9600
interval = 250  #  time between packets of data

RTCSEC = 0
RTCMIN = 0
RTCHOUR = 0
RTCWKDAY = 0
RTCDATE = 0
RTCMTH = 0
RTCYEAR = 0
CONTROL = 0
OSCTRIM = 0
ALM0SEC = 0
ALM0MIN = 0
ALM0HOUR = 0
ALM0WKDAY = 0
ALM0DATE = 0
ALM0MTH = 0
ALM1SEC = 0
ALM1MIN = 0
ALM1HOUR = 0
ALM1WKDAY = 0
ALM1DATE = 0
ALM1MTH = 0
PWRDNMIN = 0
PWRDNHOUR = 0
PWRDNDATE = 0
PWRDNMTH = 0
PWRUPMIN = 0
PWRUPHOUR = 0
PWRUPDATE = 0
PWRUPMTH = 0

st = False
second = 0
minute = 0
hour = 0
ampm = 0 # 0 - 24h ,1 - am , 2 - pm
oscrun = False
pwrfail = False
vbaten = False
wkday = 0
weekdays = {0: "NONE", 1: "MON", 2: "TUE", 3: "WED", 4: "THU", 5: "FRI", 6: "SAT", 7: "SUN"}
inv_weekdays = {"NONE": 0, "MON": 1,"TUE": 2, "WED": 3, "THU": 4, "FRI": 5, "SAT": 6, "SUN": 7}
date = 0
month = 0
year = 0
squarewave = 0 #0, 1, 4, 8, 32
out = False
externalosc = False
coarsetrim = False
control = 0
osctrim = 0
osctrim_sign = False
almpol = False

alm0second = 0
alm0minute = 0
alm0hour = 0
alm0mask = 0
alm0flag = False
alm0wkday = 0
alm0date = 0
alm0month = 0
alm0en = False

alm1second = 0
alm1minute = 0
alm1hour = 0
alm1mask = 0
alm1flag = False
alm1wkday = 0
alm1date = 0
alm1month = 0
alm1en = False

pwrdnminute = 0
pwrdnhour = 0
pwrdnampm = 0
pwrdndate = 0
pwrdnwkday = 0
pwrdnmonth = 0

pwrupminute = 0
pwruphour = 0
pwrupampm = 0
pwrupdate = 0
pwrupwkday = 0
pwrupmonth = 0

clock = {0: "Turned off", 1: "1 Hz", 4: "4.096 kHz", 8: "8.192 kHz", 32: "32.768 kHz"}
mask = {0: "Seconds", 1: "Minutes", 2: "Hours", 3: "Day of week", 4: "Date", 7: "All"}

gotData = False
updatedGui = False


def is_bit_set(number, bit_position):
    mask = 1 << bit_position
    return (int(number) & mask) != 0

def safe_int_conversion(entry, default=-1):
    try:
        return int(entry.get())
    except ValueError:
        return default

def change_clock_speed(selection):
    clock_speed_var.set(selection)
    if ((CONTROL & 64) >> 6) == 1:
        if CONTROL & 3 == 0:
            clock_value = clock[1]
        if CONTROL & 3 == 1:
            clock_value = clock[4]
        if CONTROL & 3 == 2:
            clock_value = clock[8]
        if CONTROL & 3 == 3:
            clock_value = clock[32]
    else:
        clock_value = clock[0] 
    message = None
    if clock_value == clock_speed_var.get():
        return
    if clock_speed_var.get() == "Turned off":
        message = CONTROL & 191
    if clock_speed_var.get() in ["1 Hz", "4.096 kHz", "8.192 kHz", "32.768 kHz"]:
        message = CONTROL | 64
        message = message & 252
    if clock_speed_var.get() == "4.096 kHz":
        message = message | 1
    if clock_speed_var.get() == "8.192 kHz":
        message = message | 2
    if clock_speed_var.get() == "32.768 kHz":
        message = message | 3
    if message is not None:    
        message = "07_" + str(message) + "\n"
        ser.write(bytes(message, 'utf-8'))

def change_alm0mask(selection):
    alm0mask_var.set(selection)
    mask_value = (ALM0WKDAY & 112) >> 4
    if mask[mask_value] == alm0mask_var.get():
        return
    message = ALM0WKDAY & 143
    if alm0mask_var.get() == "Minutes":
        message = message | 16
    if alm0mask_var.get() == "Hours":
        message = message | 32
    if alm0mask_var.get() == "Day of week":
        message = message | 48
    if alm0mask_var.get() == "Date":
        message = message | 64
    if alm0mask_var.get() == "All":
        message = message | 112   
    message = "0D_" + str(message) + "\n"
    ser.write(bytes(message, 'utf-8'))

def change_alm1mask(selection):
    alm1mask_var.set(selection)
    mask_value = (ALM1WKDAY & 112) >> 4
    if mask[mask_value] == alm1mask_var.get():
        return
    message = ALM1WKDAY & 143
    if alm1mask_var.get() == "Minutes":
        message = message | 16
    if alm1mask_var.get() == "Hours":
        message = message | 32
    if alm1mask_var.get() == "Day of week":
        message = message | 48
    if alm1mask_var.get() == "Date":
        message = message | 64
    if alm1mask_var.get() == "All":
        message = message | 112   
    message = "14_" + str(message) + "\n"
    ser.write(bytes(message, 'utf-8'))

def change_startbit():
    message = None
    checkbox_value = startbit_var.get()
    if st == True and checkbox_value == False:
        message = RTCSEC & 127
    if st== False and checkbox_value == True:
        message = RTCSEC | 128
    if message is not None:
        message = "00_" + str(message) + "\n"
        ser.write(bytes(message, 'utf-8'))

def change_coarse_trim():
    message = None
    checkbox_value = coarsetrim_var.get()
    if coarsetrim == True and checkbox_value == False:
        message = CONTROL & 251
    if coarsetrim == False and checkbox_value == True:
        message = CONTROL | 4
    if message is not None:
        message = "07_" + str(message) + "\n"
        ser.write(bytes(message, 'utf-8'))

def change_externalosc():
    message = None
    checkbox_value = externalosc_var.get()
    if externalosc == True and checkbox_value == False:
        message = CONTROL & 247
    if externalosc == False and checkbox_value == True:
        message = CONTROL | 8
    if message is not None:
        message = "07_" + str(message) + "\n"
        ser.write(bytes(message, 'utf-8'))

def change_vbaten():
    message = None
    checkbox_value = vbaten_var.get()
    if vbaten == True and checkbox_value == False:
        message = RTCWKDAY & 247
    if vbaten == False and checkbox_value == True:
        message = RTCWKDAY | 8
    if message is not None:
        message = "03_" + str(message) + "\n"
        ser.write(bytes(message, 'utf-8'))

def change_almpol():
    message = None
    checkbox_value = almpol_var.get()
    if almpol == True and checkbox_value == False:
        message = CONTROL & 127
    if almpol == False and checkbox_value == True:
        message = CONTROL | 128
    if message is not None:
        message = "0D_" + str(message) + "\n"
        ser.write(bytes(message, 'utf-8'))

def change_alm0en():
    message = None
    checkbox_value = alm0en_var.get()
    if alm0en == True and checkbox_value == False:
        message = CONTROL & 239
    if alm0en == False and checkbox_value == True:
        message = CONTROL | 16
    if message is not None:
        message = "07_" + str(message) + "\n"
        ser.write(bytes(message, 'utf-8'))

def change_alm1en():
    message = None
    checkbox_value = alm1en_var.get()
    if alm1en == True and checkbox_value == False:
        message = CONTROL & 223
    if alm1en == False and checkbox_value == True:
        message = CONTROL | 32
    if message is not None:
        message = "07_" + str(message) + "\n"
        ser.write(bytes(message, 'utf-8'))

def clear_alm0flag():
    if alm0flag == True:
        message = ALM0WKDAY &  247
        message = "0D_" + str(message) + "\n"
        ser.write(bytes(message, 'utf-8'))

def clear_alm1flag():
    if alm1flag == True:
        message = ALM1WKDAY &  247
        message = "14_" + str(message) + "\n"
        ser.write(bytes(message, 'utf-8'))

def clear_power():
    if pwrfail == True:
        message = RTCWKDAY &  247
        message = "03_" + str(message) + "\n"
        ser.write(bytes(message, 'utf-8'))

def send_RTC():
    message = ""
    sec = safe_int_conversion(RTCsecond_entry)
    min = safe_int_conversion(RTCminutes_entry)
    h = safe_int_conversion(RTChours_entry)
    wk = RTCwkday_entry.get().upper()
    dat = safe_int_conversion(RTCdate_entry)
    mo = safe_int_conversion(RTCmonth_entry)
    y = safe_int_conversion(RTCyear_entry)
    if sec >= 0 and sec <= 60:
        if len(str(sec)) == 2:
            sec = str(sec)
            sec = (int(sec[0]) << 4) + int(sec[1])
            if st == True:
                sec |= 128
        message = "00_" + str(sec) + "\n" + message
    if min >= 0 and min <= 60:
        if len(str(min)) == 2:
            min = str(min)
            min = (int(min[0]) << 4) + int(min[1])
        message = "01_" + str(min) + "\n" + message
    if h >= 0 and h <= 23:
        if len(str(h)) == 2:
            h = str(h)
            h = (int(h[0]) << 4) + int(h[1])
        message = "02_" + str(h) + "\n" + message
    if wk in weekdays.values():
        wk = inv_weekdays[wk]
        wk = wk | (ALM0WKDAY & 248)
        message = "03_" + str(wk) + "\n" + message
    if dat >= 0 and dat <= 31:
        if len(str(dat)) == 2:
            dat = str(dat)
            dat = (int(dat[0]) << 4) + int(dat[1])
        message = "04_" + str(dat) + "\n" + message
    if mo >= 0 and mo <= 12:
        if len(str(mo)) == 2:
            mo = str(mo)
            mo = (int(mo[0]) << 4) + int(mo[1])
        message = "05_" + str(mo) + "\n" + message
    if y >= 0 and y <= 99:
        if len(str(y)) == 2:
            y = str(y)
            y = (int(y[0]) << 4) + int(y[1])
        message = "06_" + str(y) + "\n" + message
    ser.write(bytes(message, 'utf-8'))

def send_autoRTC():
    if int(strftime('%S')) < 56:
        sec = int(strftime('%S')) + 1
    else:
        time.sleep(4)
        sec = int(strftime('%S')) + 1
    sec = str(sec)
    if len(sec) < 2:
        sec = "0" + sec
    sec = (int(sec[0]) << 4) + int(sec[1])
    if st == True:
        sec |= 128
    message = "00_" + str(sec) + "\n"
    min = strftime('%M')
    min = (int(min[0]) << 4) + int(min[1])
    message = "01_" + str(min) + "\n" + message
    h = strftime('%H')
    h = (int(h[0]) << 4) + int(h[1])
    message = "02_" + str(h) + "\n" + message
    wk = (strftime('%a')).upper()
    wk = inv_weekdays[wk]
    wk = str((RTCWKDAY & 56) | wk)
    message = "03_" + wk + "\n" + message
    dat = strftime('%d')
    dat = (int(dat[0]) << 4) + int(dat[1])
    message = "04_" + str(dat) + "\n" + message
    mon = strftime('%m')
    mon = (int(mon[0]) << 4) + int(mon[1])
    message = "05_" + str(mon) + "\n" + message
    y = strftime('%Y')
    lenght = len(y)
    y = y[len(y) - 2] + y[len(y) - 1]
    y = (int(y[0]) << 4) + int(y[1])
    message = "06_" + str(y) + "\n" + message
    ser.write(bytes(message, 'utf-8'))

def send_osctrim():
    osc = safe_int_conversion(osctrim_entry)
    if osc > 0:
        osc |= 256
    else:
        osc = abs(osc)
    osc >>= 1
    message = "08_" + str(osc) + "\n"
    print(message)
    ser.write(bytes(message, 'utf-8'))

def send_alm0():
    message = ""
    sec = safe_int_conversion(alm0second_entry)
    min = safe_int_conversion(alm0minutes_entry)
    h = safe_int_conversion(alm0hours_entry)
    wk = alm0wkday_entry.get().upper()
    dat = safe_int_conversion(alm0date_entry)
    mo = safe_int_conversion(alm0month_entry)
    if sec >= 0 and sec <= 60:
        if len(str(sec)) == 2:
            sec = str(sec)
            sec = (int(sec[0]) << 4) + int(sec[1])
        message = "0A_" + str(sec) + "\n" + message
    if min >= 0 and min <= 60:
        if len(str(min)) == 2:
            min = str(min)
            min = (int(min[0]) << 4) + int(min[1])
        message = "0B_" + str(min) + "\n" + message
    if h >= 0 and h <= 23:
        if len(str(h)) == 2:
            h = str(h)
            h = (int(h[0]) << 4) + int(h[1])
        message = "0C_" + str(h) + "\n" + message
    if wk in weekdays.values():
        wk = inv_weekdays[wk]
        wk = wk | (ALM0WKDAY & 248)
        message = "0D_" + str(wk) + "\n" + message
    if dat >= 0 and dat <= 31:
        if len(str(dat)) == 2:
            dat = str(dat)
            dat = (int(dat[0]) << 4) + int(dat[1])
        message = "0E_" + str(dat) + "\n" + message
    if mo >= 0 and mo <= 12:
        if len(str(mo)) == 2:
            mo = str(mo)
            mo = (int(mo[0]) << 4) + int(mo[1])
        message = "0F_" + str(mo) + "\n" + message
    ser.write(bytes(message, 'utf-8'))

def send_alm1():
    message = ""
    sec = safe_int_conversion(alm1second_entry)
    min = safe_int_conversion(alm1minutes_entry)
    h = safe_int_conversion(alm1hours_entry)
    wk = alm1wkday_entry.get().upper()
    dat = safe_int_conversion(alm1date_entry)
    mo = safe_int_conversion(alm1month_entry)
    if sec >= 0 and sec <= 60:
        if len(str(sec)) == 2:
            sec = str(sec)
            sec = (int(sec[0]) << 4) + int(sec[1])
        message = "11_" + str(sec) + "\n" + message
    if min >= 0 and min <= 60:
        if len(str(min)) == 2:
            min = str(min)
            min = (int(min[0]) << 4) + int(min[1])
        message = "12_" + str(min) + "\n" + message
    if h >= 0 and h <= 23:
        if len(str(h)) == 2:
            h = str(h)
            h = (int(h[0]) << 4) + int(h[1])
        message = "13_" + str(h) + "\n" + message
    if wk in weekdays.values():
        wk = inv_weekdays[wk]
        wk = wk | (ALM1WKDAY & 248)
        message = "14_" + str(wk) + "\n" + message
    if dat >= 0 and dat <= 31:
        if len(str(dat)) == 2:
            dat = str(dat)
            dat = (int(dat[0]) << 4) + int(dat[1])
        message = "15_" + str(dat) + "\n" + message
    if mo >= 0 and mo <= 12:
        if len(str(mo)) == 2:
            mo = str(mo)
            mo = (int(mo[0]) << 4) + int(mo[1])
        message = "16_" + str(mo) + "\n" + message
    ser.write(bytes(message, 'utf-8'))


def getArduinoInfo():

    global RTCSEC, RTCMIN, RTCHOUR, RTCWKDAY, RTCDATE, RTCMTH, RTCYEAR, CONTROL, OSCTRIM
    global ALM0SEC, ALM0MIN, ALM0HOUR, ALM0WKDAY, ALM0DATE, ALM0MTH
    global ALM1SEC, ALM1MIN, ALM1HOUR, ALM1WKDAY, ALM1DATE, ALM1MTH
    global PWRDNMIN, PWRDNHOUR, PWRDNDATE, PWRDNMTH, PWRUPMIN, PWRUPHOUR, PWRUPDATE, PWRUPMTH
    global gotData


    variable_map = {
        "00": "RTCSEC",
        "01": "RTCMIN",
        "02": "RTCHOUR",
        "03": "RTCWKDAY",
        "04": "RTCDATE",
        "05": "RTCMTH",
        "06": "RTCYEAR",
        "07": "CONTROL",
        "08": "OSCTRIM",
        "0A": "ALM0SEC",
        "0B": "ALM0MIN",
        "0C": "ALM0HOUR",
        "0D": "ALM0WKDAY",
        "0E": "ALM0DATE",
        "0F": "ALM0MTH",
        "11": "ALM1SEC",
        "12": "ALM1MIN",
        "13": "ALM1HOUR",
        "14": "ALM1WKDAY",
        "15": "ALM1DATE",
        "16": "ALM1MTH",
        "18": "PWRDNMIN",
        "19": "PWRDNHOUR",
        "1A": "PWRDNDATE",
        "1B": "PWRDNMTH",
        "1C": "PWRUPMIN",
        "1D": "PWRUPHOUR",
        "1E": "PWRUPDATE",
        "1F": "PWRUPMTH"
    }

    buffer = ser.readline().decode('utf-8').strip()
    error = False
    while len(buffer) >= 2:
        buffer_id = buffer[0] + buffer[1]
        if buffer_id in variable_map:
            try:
                globals()[variable_map[buffer_id]] = int(buffer[2:])
            except ValueError:
                error = True
                return
        buffer = ser.readline().decode('utf-8').strip()
    if error == False:
        gotData = True
    win.after(interval, getArduinoInfo)
    

def assigning_values():

    global st, second, minute, hour, ampm, oscrun, pwrfail, vbaten, wkday, date, month, year, squarewave, out, externalosc, coarsetrim, control, osctrim, osctrim_sign, almpol
    global alm0second, alm0minute, alm0hour, alm0mask, alm0flag, alm0wkday, alm0date, alm0month, alm0en
    global alm1second, alm1minute, alm1hour, alm1mask, alm1flag, alm1wkday, alm1date, alm1month, alm1en
    global pwrdnminute, pwrdnhour, pwrdnampm, pwrdndate, pwrdnwkday, pwrdnmonth
    global pwrupminute, pwruphour, pwrupampm, pwrupdate, pwrupwkday, pwrupmonth
    global gotData

    if gotData == True:

        #  seconds
        st = is_bit_set(RTCSEC, 7)
        startbit_var.set(st)
        second = RTCSEC & 127
        second = str((((second & 112) >> 4) * 10) + (second & 15))
        if len(second) == 1:
            second = '0' + second

        #  minutes

        minute = RTCMIN & 127
        minute = str((((minute & 112) >> 4) * 10) + (minute & 15))
        if len(minute) == 1:
            minute = '0' + minute

        #  hours

        if RTCHOUR >= 64:
            if is_bit_set(RTCHOUR, 5):
                ampm = 2
            else:
                ampm = 1
            hour = RTCHOUR & 31
        else:
            ampm = 0
            hour = RTCHOUR & 63
        hour = str((((hour & 48) >> 4) * 10) + (hour & 15))
        if len(hour) == 1:
            hour = '0' + hour

        #  weekday
        oscrun = is_bit_set(RTCWKDAY, 5)
        pwrfail = is_bit_set(RTCWKDAY, 4)
        if pwrfail == True:
            powerclear_button.state(['!disabled'])
        else:
            powerclear_button.state(['disabled'])
        vbaten = is_bit_set(RTCWKDAY, 3)
        vbaten_var.set(vbaten)
        wkday = str(weekdays.get(RTCWKDAY & 7))

        #  date
        
        date = str((((RTCDATE & 48) >> 4) * 10) + (RTCDATE & 15))
        if len(date) == 1:
            date = '0' + date

        #  month

        month = RTCMTH & 31
        month = str((((month & 16) >> 4) * 10) + (month & 15))
        if len(month) == 1:
            month = '0' + month

        #  year

        year = str((((RTCYEAR & 240) >> 4) * 10) + (RTCYEAR & 15))

        #  control

        out = is_bit_set(CONTROL, 7)
        alm1en = is_bit_set(CONTROL, 5)
        alm1en_var.set(alm1en)
        alm0en = is_bit_set(CONTROL, 4)
        alm0en_var.set(alm0en)
        externalosc = is_bit_set(CONTROL, 3)
        externalosc_var.set(externalosc)
        coarsetrim = is_bit_set(CONTROL, 2)
        coarsetrim_var.set(coarsetrim)
        if is_bit_set(CONTROL, 6): #square wave enabled
            if is_bit_set(CONTROL, 1) == 1:
                if is_bit_set(CONTROL, 0):
                    #32.768 kHz
                    squarewave = 32
                else:
                    #8.192 kHz
                    squarewave = 8
            else:
                if is_bit_set(CONTROL, 0):
                    #4.096 kHz
                    squarewave = 4
                else:
                    #1 Hz
                    squarewave = 1
        else:
            squarewave = 0

        osctrim = OSCTRIM << 1
        if osctrim >= 256:
            #adds
            osctrim_sign = True
            osctrim = osctrim & 255
        else:
            #subtracts
            osctrim_sign = False

        #==================================== ALARM 0 ====================================#

        #  seconds

        alm0second = str((((ALM0SEC & 112) >> 4) * 10) + (ALM0SEC & 15))
        if len(alm0second) == 1:
            alm0second = '0' + alm0second

        #  minutes

        alm0minute = str((((ALM0MIN & 112) >> 4) * 10) + (ALM0MIN & 15))
        if len(alm0minute) == 1:
            alm0minute = '0' + alm0minute

        #  hours

        if ampm == 0:
            alm0hour = ALM0HOUR & 63
        else:
            alm0hour = ALM0HOUR & 31
        alm0hour = str((((alm0hour & 48) >> 4) * 10) + (alm0hour & 15))
        if len(alm0hour) == 1:
            alm0hour = '0' + alm0hour

        #  weekday

        almpol = is_bit_set(ALM0WKDAY, 7)
        almpol_var.set(almpol)
        alm0mask = (ALM0WKDAY & 127) >> 4
        alm0flag = is_bit_set(ALM0WKDAY, 3)
        if alm0flag == True:
            alm0flag_button.state(['!disabled'])
        else:
            alm0flag_button.state(['disabled'])
        alm0wkday = str(weekdays.get(ALM0WKDAY & 7))

        #  date

        alm0date = str((((ALM0DATE & 48) >> 4) * 10) + (ALM0DATE & 15))
        if len(alm0date) == 1:
            alm0date = '0' + alm0date

        #  month

        alm0month = ALM0MTH & 31
        alm0month = str((((alm0month & 16) >> 4) * 10) + (alm0month & 15))
        if len(alm0month) == 1:
            alm0month = '0' + alm0month


        #==================================== ALARM 1 ====================================#

        #  seconds

        alm1second = str((((ALM1SEC & 112) >> 4) * 10) + (ALM1SEC & 15))
        if len(alm1second) == 1:
            alm1second = '0' + alm1second

        #  minutes

        alm1minute = str((((ALM1MIN & 112) >> 4) * 10) + (ALM1MIN & 15))
        if len(alm1minute) == 1:
            alm1minute = '0' + alm1minute

        #  hours

        if ampm == 0:
            alm1hour = ALM1HOUR & 63
        else:
            alm1hour = ALM1HOUR & 31
        alm1hour = str((((alm1hour & 48) >> 4) * 10) + (alm1hour & 15))
        if len(alm1hour) == 1:
            alm1hour = '0' + alm1hour

        #  weekday

        alm1mask = (ALM1WKDAY & 127) >> 4
        alm1flag = is_bit_set(ALM1WKDAY, 3)
        if alm1flag == True:
            alm1flag_button.state(['!disabled'])
        else:
            alm1flag_button.state(['disabled'])
        alm1wkday = str(weekdays.get(ALM1WKDAY & 7))

        #  date

        alm1date = str((((ALM1DATE & 48) >> 4) * 10) + (ALM1DATE & 15))
        if len(alm1date) == 1:
            alm1date = '0' + alm1date

        #  month

        alm1month = ALM1MTH & 31
        alm1month = str((((alm1month & 16) >> 4) * 10) + (alm1month & 15))
        if len(alm1month) == 1:
            alm1month = '0' + alm1month

        #==================================== POWER DOWN ====================================#

        #  minutes

        pwrdnminute = str((((PWRDNMIN & 112) >> 4) * 10) + (PWRDNMIN & 15))
        if len(pwrdnminute) == 1:
            pwrdnminute = '0' + pwrdnminute

        #  hours

        if PWRDNHOUR >= 64:
            pwrdnampm = 0
            pwrdnhour = PWRDNHOUR & 63
        else:
            if is_bit_set(PWRDNHOUR, 5):
                pwrdnampm = 2
            else:
                pwrdnampm = 1
            pwrdnhour = PWRDNHOUR & 31
        pwrdnhour = str((((pwrdnhour & 48) >> 4) * 10) + (pwrdnhour & 15))
        if len(pwrdnhour) == 1:
            pwrdnhour = '0' + pwrdnhour

        #  date

        pwrdndate = str((((PWRDNDATE & 48) >> 4) * 10) + (PWRDNDATE & 15))
        if len(pwrdndate) == 1:
            pwrdndate = '0' + pwrdndate

        #  month

        pwrdnwkday = str(weekdays.get((PWRDNMTH >> 5) & 7))
        pwrdnmonth = PWRDNMTH & 31
        pwrdnmonth = str((((pwrdnmonth & 16) >> 4) * 10) + (pwrdnmonth & 15))
        if len(pwrdnmonth) == 1:
            pwrdnmonth = '0' + pwrdnmonth


        #==================================== POWER UP ====================================#

        #  minutes

        pwrupminute = str((((PWRUPMIN & 112) >> 4) * 10) + (PWRUPMIN & 15))
        if len(pwrupminute) == 1:
            pwrupminute = '0' + pwrupminute

        #  hours

        if PWRUPHOUR >= 64:
            pwruphour = 0
            pwruphour = PWRUPHOUR & 63
        else:
            if is_bit_set(PWRUPHOUR, 5):
                pwrupampm = 2
            else:
                pwrupampm = 1
            pwruphour = PWRUPHOUR & 31
        pwruphour = str((((pwruphour & 48) >> 4) * 10) + (pwruphour & 15))
        if len(pwruphour) == 1:
            pwruphour = '0' + pwruphour

        #  date

        pwrupdate = str((((PWRUPDATE & 48) >> 4) * 10) + (PWRUPDATE & 15))
        if len(pwrupdate) == 1:
            pwrupdate = '0' + pwrupdate

        #  month

        pwrupwkday = str(weekdays.get((PWRUPMTH >> 5) & 7))
        pwrupmonth = PWRUPMTH & 31
        pwrupmonth = str((((pwrupmonth & 16) >> 4) * 10) + (pwrupmonth & 15))
        if len(pwrupmonth) == 1:
            pwrupmonth = '0' + pwrupmonth

    gotData = False
    
    win.after(interval, assigning_values)


def updating_gui():

    global st, second, minute, hour, ampm, oscrun, pwrfail, vbaten, wkday, date, month, year, squarewave, out, externalosc, coarsetrim, control, osctrim, osctrim_sign, almpol
    global alm0second, alm0minute, alm0hour, alm0mask, alm0flag, alm0wkday, alm0date, alm0month, alm0en
    global alm1second, alm1minute, alm1hour, alm1mask, alm1flag, alm1wkday, alm1date, alm1month, alm1en
    global pwrdnminute, pwrdnhour, pwrdnampm, pwrdndate, pwrdnwkday, pwrdnmonth
    global pwrupminute, pwruphour, pwrupampm, pwrupdate, pwrupwkday, pwrupmonth
    global gotData

    RTC_label.config(text=f"Current time is: {strftime('%H:%M:%S %A %d/%m/%Y')}\nTime stored in RTC is: {hour}:{minute}:{second} {wkday} {date}/{month}/{year}")

    
    if squarewave == 0:
        if alm0en == True and alm1en == False:
            txt = "MFP is connected to Alarm 0"
        if alm0en == False and alm1en == True:
            txt = "MFP is connected to Alarm 1"
        if alm0en == True and alm1en == True:
            txt = "MFP is connected to Alarm 0 and 1"
        if alm0en == False and alm1en == False:
            if out == True:
                txt = "MFP is set 1."
            else:
                txt = "MFP is set 0."
        else:
            if almpol == True:
                txt = txt + " and its asserted output state is set 1."
            else:
                txt = txt + " and its asserted output state is set 0."
    else:
        txt = "MFP is outputting clock " + clock[squarewave] + " signal."



    add_subtract = {True: "adds ",False: "subtracts "}
    if osctrim == 0:
        txt = txt + "\nDigital trimming is turned off."
    else:
        if coarsetrim == False:
            txt = txt + "\nDigital trimming " + add_subtract[osctrim_sign] + str(osctrim) + " cycles per minute."
        else:
            txt = txt + "\nDigital trimming " + add_subtract[osctrim_sign] + str(osctrim) + " cycles 128 times per second (coarse trimming is on)."


    if vbaten == True:
        txt = txt + "\nBattery backup supply enabled."
    else:
        txt = txt + "\nBattery backup supply disabled."
    
    control_label.config(text=txt)

    txt = "Alarm 0 "
    if alm0flag == True:
        txt = txt + "occured and it "
    else:
        txt = txt + "didn't occur and it "
    
    if alm0en == True:
        txt = txt + "is enabled.\n"
    else:
        txt = txt + "is disabled.\n"
    
    
    if alm0mask != 7:
        txt = txt + "Alarm 0 reacts to "
    if alm0mask == 0:
        txt = txt + "seconds and it is set to " + alm0second + " s." 
    if alm0mask == 1:
        txt = txt + "minutes and it is set to " + alm0minute + " min."
    if alm0mask == 2:
        txt = txt + "hours and it is set to " + alm0hour + " h."
    if alm0mask == 3:
        txt = txt + "day of the week and it is set to " + alm0wkday + "."
    if alm0mask == 4:
        txt = txt + "date and it is set to " + alm0date + " day of the month."
    if alm0mask == 7:
        txt = txt + (f"Alarm 0 is set to {alm0hour}:{alm0minute}:{alm0second} {alm0wkday} {alm0date}/{alm0month}.")

    alm0_label.config(text=txt)

    txt = "Alarm 1 "
    if alm1flag == True:
        txt = txt + "occured and it "
    else:
        txt = txt + "didn't occur and it "
    
    if alm1en == True:
        txt = txt + "is enabled.\n"
    else:
        txt = txt + "is disabled.\n"
    
    
    if alm1mask != 7:
        txt = txt + "Alarm 1 reacts to "
    if alm1mask == 0:
        txt = txt + "seconds and it is set to " + alm1second + " s." 
    if alm1mask == 1:
        txt = txt + "minutes and it is set to " + alm1minute + " min."
    if alm1mask == 2:
        txt = txt + "hours and it is set to " + alm1hour + " h."
    if alm1mask == 3:
        txt = txt + "day of the week and it is set to " + alm1wkday + "."
    if alm1mask == 4:
        txt = txt + "date and it is set to " + alm1date + " day of the month."
    if alm1mask == 7:
        txt = txt + (f"Alarm 1 is set to {alm1hour}:{alm1minute}:{alm1second} {alm1wkday} {alm1date}/{alm1month}.")

    alm1_label.config(text=txt)

    if pwrfail == True:
        txt = "Power fail occured."
    else:
        txt = "Power fail did not occur."
    txt = txt + f"\nPower was lost at {pwrdnhour}:{pwrdnminute} {pwrdnwkday} {pwrdndate}/{pwrdnmonth}."
    txt = txt + f"\nPower came back at {pwruphour}:{pwrupminute} {pwrupwkday} {pwrupdate}/{pwrupmonth}."

    power_label.config(text=txt)


    win.after(interval, updating_gui)


ser = serial.Serial(serial_port, baud_rate, timeout=0.005)
ser.flushInput()

win = tk.Tk()
win.title("MCP7940N")
win.minsize(600,400)

#        #=================================================================================#        #
#        #==================================== WIDGETS ====================================#        #
#        #=================================================================================#        #

#==================================== RTC ====================================#

RTC_frame = ttk.LabelFrame(win, padding=5, text = "RTC")
RTC_label = ttk.Label(RTC_frame, text = 'RTC and real time', font=("Arial", 12))

#  Setting time
RTCsetting_frame = ttk.Frame(RTC_frame)

RTCsetting_label = ttk.Label(RTC_frame, text = "Input time in format HH:MM:SS WKD DD/MM/YY")
RTCsecond_entry = ttk.Entry(RTCsetting_frame, width = 3)
RTCminutes_entry = ttk.Entry(RTCsetting_frame, width = 3)
RTChours_entry = ttk.Entry(RTCsetting_frame, width = 3)
RTCwkday_entry = ttk.Entry(RTCsetting_frame, width = 5)
RTCdate_entry = ttk.Entry(RTCsetting_frame, width = 3)
RTCmonth_entry = ttk.Entry(RTCsetting_frame, width = 3)
RTCyear_entry = ttk.Entry(RTCsetting_frame, width = 3)

colon1 = ttk.Label(RTCsetting_frame, text = ":")
colon2 = ttk.Label(RTCsetting_frame, text = ":")
slash1 = ttk.Label(RTCsetting_frame, text = "/")
slash2 = ttk.Label(RTCsetting_frame, text = "/")
space1 = ttk.Label(RTCsetting_frame, text = "  ")
space2 = ttk.Label(RTCsetting_frame, text = "  ")

RTCsetting_button = ttk.Button(RTC_frame, text = "Set time", command = send_RTC)
RTCautosetting_button = ttk.Button(RTC_frame, text = "Automatically set time", command = send_autoRTC)

#==================================== CONTROL ====================================#

control_frame = ttk.LabelFrame(win, text = "Control")
control_label = ttk.Label(control_frame, text = 'Control', wraplength=240, anchor="center", justify="center")

#  Set frequency
clock_speed_var = tk.StringVar(value = "Set frequency")
clock_speed_menubutton = ttk.Menubutton(control_frame, text = "Set frequency")
clock_speed_menu = tk.Menu(clock_speed_menubutton, tearoff=0)
clock_speed_menubutton['menu'] = clock_speed_menu
for value in clock.values():
    clock_speed_menu.add_command(label=value, command=lambda v=value: change_clock_speed(v))

#  Set digital trimming
osctrim_label = ttk.Label(control_frame, text = "Send digital trimming value <-254, 254>")
osctrim_frame = ttk.Frame(control_frame)
osctrim_entry = ttk.Entry(osctrim_frame)
osctrim_button = ttk.Button(osctrim_frame, text = "Set digital trimming", command = send_osctrim)

#  Star oscillator
startbit_var = tk.BooleanVar(value= False)
startbit_checkbox = ttk.Checkbutton(control_frame, text = "start bit", command = change_startbit, variable = startbit_var , onvalue = True, offvalue = False)

#  Coarse trimming
coarsetrim_var = tk.BooleanVar(value= False)
coarsetrim_checkbox = ttk.Checkbutton(control_frame, text = "coarse trim", command = change_coarse_trim, variable = coarsetrim_var , onvalue = True, offvalue = False)

#  External oscillator
externalosc_var = tk.BooleanVar(value= False)
externalosc_checkbox = ttk.Checkbutton(control_frame, text = "external oscillator", command = change_externalosc, variable = externalosc_var , onvalue = True, offvalue = False)

#  Battery backup supply
vbaten_var = tk.BooleanVar(value = False)
vbaten_checkbox = ttk.Checkbutton(control_frame, text = "Battery backup supply", command = change_vbaten, variable = vbaten_var , onvalue = True, offvalue = False)

#  Alarm polarity
almpol_var = tk.BooleanVar(value= False)
almpol_checkbox = ttk.Checkbutton(control_frame, text = "alarm polarity", command = change_almpol, variable = almpol_var , onvalue = True, offvalue = False)



#==================================== ALARM 0 ====================================#

alm0_frame = ttk.LabelFrame(win, text = "Alarm 0")
alm0_label = ttk.Label(alm0_frame, text = 'Alarm 0', anchor="center", justify="center")            #7F7F7F

#  Setting mask
alm0mask_var = tk.StringVar(value = "Set mask")
alm0mask_menubutton = ttk.Menubutton(alm0_frame, text = "Set mask")
alm0mask_menu = tk.Menu(alm0mask_menubutton, tearoff=0)
alm0mask_menubutton['menu'] = alm0mask_menu
for value in mask.values():
    alm0mask_menu.add_command(label=value, command=lambda v=value: change_alm0mask(v))

#  Alarm enable
alm0en_var = tk.BooleanVar(value= False)
alm0en_checkbox = ttk.Checkbutton(alm0_frame, text = "alarm 0 enabled", command = change_alm0en, variable = alm0en_var , onvalue = True, offvalue = False)

#  Clearing flag
alm0flag_button = ttk.Button(alm0_frame, text = "Clear interrupt flag", command = clear_alm0flag)

#  Setting alarm
alm0setting_frame = ttk.Frame(alm0_frame)

alm0setting_label = ttk.Label(alm0_frame, text = "Input alarm in format HH:MM:SS WKD DD/MM")
alm0second_entry = ttk.Entry(alm0setting_frame, width = 3)
alm0minutes_entry = ttk.Entry(alm0setting_frame, width = 3)
alm0hours_entry = ttk.Entry(alm0setting_frame, width = 3)
alm0wkday_entry = ttk.Entry(alm0setting_frame, width = 5)
alm0date_entry = ttk.Entry(alm0setting_frame, width = 3)
alm0month_entry = ttk.Entry(alm0setting_frame, width = 3)

colon01 = ttk.Label(alm0setting_frame, text = ":")
colon02 = ttk.Label(alm0setting_frame, text = ":")
slash01 = ttk.Label(alm0setting_frame, text = "/")
space01 = ttk.Label(alm0setting_frame, text = "  ")
space02 = ttk.Label(alm0setting_frame, text = "  ")

alm0setting_button = ttk.Button(alm0_frame, text = "Set alarm", command = send_alm0)

#==================================== ALARM 1 ====================================#

alm1_frame = ttk.LabelFrame(win, text = "Alarm 1")
alm1_label = ttk.Label(alm1_frame, text = 'Alarm 1', anchor="center", justify="center")

#  Setting mask
alm1mask_var = tk.StringVar(value = "Set mask")
alm1mask_menubutton = ttk.Menubutton(alm1_frame, text = "Set mask")
alm1mask_menu = tk.Menu(alm1mask_menubutton, tearoff=0)
alm1mask_menubutton['menu'] = alm1mask_menu
for value in mask.values():
    alm1mask_menu.add_command(label=value, command=lambda v=value: change_alm1mask(v))

#  Alarm enable
alm1en_var = tk.BooleanVar(value= False)
alm1en_checkbox = ttk.Checkbutton(alm1_frame, text = "alarm 1 enabled", command = change_alm1en, variable = alm1en_var , onvalue = True, offvalue = False)

#  Clearing flag
alm1flag_button = ttk.Button(alm1_frame, text = "Clear interrupt flag", command = clear_alm1flag)

#  Setting alarm
alm1setting_frame = ttk.Frame(alm1_frame)

alm1setting_label = ttk.Label(alm1_frame, text = "Input alarm in format HH:MM:SS WKD DD/MM")
alm1second_entry = ttk.Entry(alm1setting_frame, width = 3)
alm1minutes_entry = ttk.Entry(alm1setting_frame, width = 3)
alm1hours_entry = ttk.Entry(alm1setting_frame, width = 3)
alm1wkday_entry = ttk.Entry(alm1setting_frame, width = 5)
alm1date_entry = ttk.Entry(alm1setting_frame, width = 3)
alm1month_entry = ttk.Entry(alm1setting_frame, width = 3)

colon11 = ttk.Label(alm1setting_frame, text = ":")
colon12 = ttk.Label(alm1setting_frame, text = ":")
slash11 = ttk.Label(alm1setting_frame, text = "/")
space11 = ttk.Label(alm1setting_frame, text = "  ")
space12 = ttk.Label(alm1setting_frame, text = "  ")

alm1setting_button = ttk.Button(alm1_frame, text = "Set alarm", command = send_alm1)

#==================================== POWER ====================================#

power_frame = ttk.LabelFrame(win, text = "Power")
power_label = ttk.Label(power_frame, text = 'Power', anchor="center", justify="center")

powerclear_button = ttk.Button(power_frame, text = "Clear Power", command = clear_power)


#        #===========================================================================================#        #
#        #==================================== WIDGETS PLACEMENT ====================================#        #
#        #===========================================================================================#        #


win.columnconfigure(0, weight = 1, uniform = 'a')
win.columnconfigure(1, weight = 1, uniform = 'a')
win.rowconfigure(0, weight = 1, uniform = 'a')
win.rowconfigure(1, weight = 1, uniform = 'a')
win.rowconfigure(2, weight = 1, uniform = 'a')
win.rowconfigure(3, weight = 1, uniform = 'a')
win.rowconfigure(4, weight = 1, uniform = 'a')
win.rowconfigure(5, weight = 1, uniform = 'a')

RTC_frame.grid(column = 0, row = 0, rowspan = 3, sticky='nsew', padx = 10, pady = 10)
RTC_label.pack()
RTCsetting_label.pack()
RTCsetting_frame.pack()
RTChours_entry.grid(row = 0, column = 0)
colon1.grid(row = 0, column = 1)
RTCminutes_entry.grid(row = 0, column = 2)
colon2.grid(row = 0, column = 3)
RTCsecond_entry.grid(row = 0, column = 4)
space1.grid(row = 0, column = 5)
RTCwkday_entry.grid(row = 0, column = 6)
space2.grid(row = 0, column = 7)
RTCdate_entry.grid(row = 0, column = 8)
slash1.grid(row = 0, column = 9)
RTCmonth_entry.grid(row = 0, column = 10)
slash2.grid(row = 0, column = 11)
RTCyear_entry.grid(row = 0, column = 12)
RTCsetting_button.pack()
RTCautosetting_button.pack()

control_frame.grid(column = 0, row = 3, rowspan = 3, sticky='nsew', padx = 10, pady = 10)
control_label.pack()
clock_speed_menubutton.pack()
osctrim_label.pack()
osctrim_frame.pack()
osctrim_entry.pack(side=tk.LEFT, padx = 5)
osctrim_button.pack(side=tk.RIGHT, padx = 5)
startbit_checkbox.pack()
coarsetrim_checkbox.pack()
externalosc_checkbox.pack()
vbaten_checkbox.pack()
almpol_checkbox.pack()

alm0_frame.grid(column = 1, row = 0, rowspan = 2, sticky='nsew', padx = 10, pady = 10)
alm0_label.pack()
alm0en_checkbox.pack()
alm0mask_menubutton.pack()
alm0flag_button.pack()
alm0setting_label.pack()
alm0setting_frame.pack()
alm0hours_entry.grid(row = 0, column = 0)
colon01.grid(row = 0, column = 1)
alm0minutes_entry.grid(row = 0, column = 2)
colon02.grid(row = 0, column = 3)
alm0second_entry.grid(row = 0, column = 4)
space01.grid(row = 0, column = 5)
alm0wkday_entry.grid(row = 0, column = 6)
space02.grid(row = 0, column = 7)
alm0date_entry.grid(row = 0, column = 8)
slash01.grid(row = 0, column = 9)
alm0month_entry.grid(row = 0, column = 10)
alm0setting_button.pack()


alm1_frame.grid(column = 1, row = 2, rowspan = 2, sticky='nsew', padx = 10, pady = 10)
alm1_label.pack()
alm1en_checkbox.pack()
alm1mask_menubutton.pack()
alm1flag_button.pack()
alm1setting_label.pack()
alm1setting_frame.pack()
alm1hours_entry.grid(row = 0, column = 0)
colon11.grid(row = 0, column = 1)
alm1minutes_entry.grid(row = 0, column = 2)
colon12.grid(row = 0, column = 3)
alm1second_entry.grid(row = 0, column = 4)
space11.grid(row = 0, column = 5)
alm1wkday_entry.grid(row = 0, column = 6)
space12.grid(row = 0, column = 7)
alm1date_entry.grid(row = 0, column = 8)
slash11.grid(row = 0, column = 9)
alm1month_entry.grid(row = 0, column = 10)
alm1setting_button.pack()

power_frame.grid(column = 1, row = 4, rowspan = 2, sticky='nsew', padx = 10, pady = 10)
power_label.pack()
powerclear_button.pack()


getArduinoInfo()

assigning_values()

updating_gui()


win.mainloop()
