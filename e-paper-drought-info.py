#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

# ALLSKY_SFC_SW_DWN  CERES SYN1deg All Sky Surface Shortwave Downward Irradiance (MJ/m^2/day)
# T2M               MERRA-2 Temperature at 2 Meters (C) 
# T2M_MAX           MERRA-2 Temperature at 2 Meters Maximum (C) 
# TS                MERRA-2 Earth Skin Temperature (C) 
# TS_MAX            MERRA-2 Earth Skin Temperature Maximum (C) 
# PRECTOTCORR       MERRA-2 Precipitation Corrected (mm/day) 
# RH2M              MERRA-2 Relative Humidity at 2 Meters (%) 
#
# See https://power.larc.nasa.gov/#resources for all available data.

import geocoder
from datetime import datetime, timedelta
from nasapower import *
from usdm import *
from usstates import *

#Items for e-Paper display
import logging
import epd2in13bc
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

# importing kintone
import kintone
from kintone import getCurrentTimeStamp


dataToDownload = ["ALLSKY_SFC_SW_DWN", "T2M", "T2M_MAX", "TS", "TS_MAX", "PRECTOTCORR", "RH2M"]

def getPastDate(daysAgo):
    doubleDigitMonth = doubleDigitDay = "00"
    today = datetime.now()
    dt = today - timedelta(days=daysAgo)
    if dt.month // 10 == 0:
        doubleDigitMonth = "0" + str(dt.month)
    else:
        doubleDigitMonth = str(dt.month)
    if dt.day // 10 == 0:
        doubleDigitDay = "0" + str(dt.day)
    else:
        doubleDigitDay = str(dt.day)
    return str(dt.year) + doubleDigitMonth + doubleDigitDay

def ipToLatLonCityState():
    geoInfo = geocoder.ip("me")
    lat = geoInfo.lat
    lon = geoInfo.lng
    city = geoInfo.city
    state = geoInfo.state
    return (lat, lon, city, state)

lat, lon, city, stateFullName = ipToLatLonCityState()
stateCode = stateToStateCode[stateFullName]

# YYYYMMDD format
yesterday = getPastDate(1)
daysAgo14 = getPastDate(14)
daysAgo15 = getPastDate(15)
daysAgo28 = getPastDate(28)

elevation, dataset1 = downloadNasaData(lat, lon, dataToDownload, daysAgo14, yesterday)

elevation, dataset2 = downloadNasaData(lat, lon, dataToDownload, daysAgo28, daysAgo15)

severityIndex = downloadUsdmData(city, stateCode, daysAgo14, yesterday)
severityDescription = ["Abnormally Dry", "Moderate Drought",
                       "Severe Drought", "Extreme Drought", "Exceptional Drought"]

print("\n\nCurrent Address:\n" + city + ", " + stateCode)
print("Average Irradiance (ALLSKY_SFC_SW_DWN) of past 2 weeeks/4 weeks:\n" + str(dataset1[0]) + " / " + str((dataset1[0] + dataset2[0]) / 2) + " MJ/m^2/day")
print("Average Temperature (T2M) of past 2 weeks/4 weeks:\n" + str(dataset1[1]) + " / " + str((dataset1[1] + dataset2[1]) /2) + " C")
print("Average Maximum Temperature (T2M_MAX) of past 2 weeks/4 weeks:\n" + str(dataset1[2]) + " / " + str((dataset1[2] + dataset2[2]) / 2) + " C")
print("Average Earth Skin Temperature (TS) of past 2 weeks/4 weeks:\n" + str(dataset1[3]) + " / " + str((dataset1[3] + dataset2[3]) / 2) + " C")
print("Average Earth Skin Temperature (TS_MAX) of past 2 weeks/4 weeks:\n" + str(dataset1[4]) + " / " + str((dataset1[4] + dataset2[4]) / 2) + " C")
print("Average Precipitation (PRECTOTCORR) of past 2 weeks/4 weeks:\n" + str(dataset1[5]) + " / " + str((dataset1[5] + dataset2[5]) / 2) + " mm/day")
print("Average Humidity (RH2M) of past 2 weeks/4 weeks:\n" + str(dataset1[6]) + " / " + str((dataset1[6] + dataset2[6]) /2) + " %")
print("\nSeverity of Drought: D" + str(severityIndex) + " " + severityDescription[severityIndex])

# Uploading the data into Kintone
sdomain = "kokun"
appId = "12"
token = "XlFBywIWUFEq5hGTM4TsQChshkWD0qOlYIj43R0N"

# payload = {"app": appId,
#            "record": {"allsky_sfc_sw_dwn": {"value": },
#                       "t2m": {"value": }
#                       "t2m_max" : {"value": }
#                       "ts" : {"value": }
#                       "ts_max" : {"value": }
#                       "prectotcorr" : {"value": }
#                       "rh2m" : {"value":}
#                       "severity" : {"value": }}}

# recordId = kintone.uploadRecord(subDomain=sdomain,
#                                 apiToken=token,
#                                 record=payload)
# if recordId is None:
#     print("Failed to upload the data on Kintone.")

# Display the data
# logging.basicConfig(level.logging=DEBUG)

try:
    logging.info("epd2in13bc Demo")
    epd = epd2in13bc.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    time.sleep(1)
    
    # Drawing on the image
    logging.info("Drawing")
    font1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
    font2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    HBlackimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126
    HRYimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126  ryimage: red or yellow image
    drawBlack = ImageDraw.Draw(HBlackimage)
    drawRed = ImageDraw.Draw(HRYimage)
    
    drawBlack.text((0, 0), city + ', ' + stateCode, font = font1, fill = 0)
    drawBlack.text((0, 16), "Irradiance(avg. 2 wks):", font = font1, fill = 0)
    drawBlack.text((0, 32), str(round(dataset1[0], 5)) + " MJ/m^2/day", font = font1, fill = 0)
    drawBlack.text((0, 48), "Precipitation(avg. 2 wks): ", font = font1, fill = 0)
    drawBlack.text((0, 64), str(round(dataset1[5], 5)) + " mm/day", font = font1, fill = 0)
    if severityIndex <= 2:
        drawBlack.text((0, 80), "D" + str(severityIndex) + " " + severityDescription[severityIndex] , font = font2, fill = 0)
    elif severityIndex > 2 and severityIndex <= 4:
        drawRed.text((0, 80), "D" + str(severityIndex) + " " + severityDescription[severityIndex] , font = font2, fill = 0)
    else:
        print("Error Occured")
    
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
    time.sleep(2)
    
    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
        
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in13bc.epdconfig.module_exit()
    exit()