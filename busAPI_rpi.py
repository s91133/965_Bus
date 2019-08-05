from hashlib import sha1
import hmac
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import base64
from requests import request
from pprint import pprint
import  json
import demjson
import os
import time
from datetime import datetime
import socket

global writeHtmlList
global writeTxtList
boot_controller = None
vehiclejson = None
stajson = None
bus_sta_list = None
stalist = None
bus_sta_count = None

app_id = 'c2867a08b8f741b9bef1900b2c12c55a' #tuple('c2867a08b8f741b9bef1900b2c12c55a')
app_key = 'ebQiA77NHGeX_pi-HnWxlmuTU1g' #tuple('ebQiA77NHGeX_pi-HnWxlmuTU1g')
write_path = "" #tuple("/home/pi/www/")

class Auth():


    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        xdate = format_date_time(mktime(datetime.now().timetuple()))
        hashed = hmac.new(self.app_key.encode('utf8'), ('x-date: ' + xdate).encode('utf8'), sha1)
        signature = base64.b64encode(hashed.digest()).decode()

        authorization = 'hmac username="' + self.app_id + '", ' + \
                        'algorithm="hmac-sha1", ' + \
                        'headers="x-date", ' + \
                        'signature="' + signature + '"'
        return {
            'Authorization': authorization,
            'x-date': format_date_time(mktime(datetime.now().timetuple())),
            'Accept - Encoding': 'gzip'
        }


def internet(host="8.8.8.8", port=53, timeout=3):
    #   Host: 8.8.8.8 (google-public-dns-a.google.com)
    #   OpenPort: 53/tcp
    #   Service: domain (DNS/TCP)
      try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
      except Exception as ex:
        print (ex.message)
        return False

import demjson
def read_text_file(file_path,json_flag=False):
    file_ = open(file_path,'r')
    if json_flag == True:
        tmp_ = demjson.decode(file_.read())
    else:
        tmp_ = file_.read()
    file_.close()
    return tmp_

def write_text_file(file_path,write_data):
    file_ = open(file_path,'a')
    file_.write(write_data)
    file_.close()

def write_html_file(file_path,write_data,write_type='w'):
    file_ = open(file_path,write_type)
    file_.write(write_data)
    file_.close()

def programset():
    global boot_controller
    global vehiclejson
    global stajson
    global bus_sta_list
    global stalist
    global bus_sta_count

    try :
        if int(read_text_file(write_path + "./start.txt")) == 1 :
            boot_controller = 1
        else :
            boot_controller = 0
        vehiclejson = read_text_file(write_path + "./VehicleInfo.txt",json_flag = True)
        stajson = read_text_file(write_path + "./ManageStaInfo.txt",json_flag = True)

        stalist = []
        for item in stajson:
            if item["ManageSta"] not in stalist :
                stalist.append(item["ManageSta"])

        bus_sta_list = {}
        bus_sta_count = {}

        for i in stalist:
            bus_sta_list[str(i)] = []
            bus_sta_count[str(i)] = 0

    except Exception as e :
        writeList = []
        writeList.append("Program initialization failed !")
        writeList.append("時間 : {0} ".format(time.ctime()))
        writeStr = '\n\n'.join(writeList)
        write_text_file(write_path + "./VehicleInfo.txt",writeStr)
        boot_controller = 0

def informationwrite(datalist):
    if 'PlateNumb' in datalist[item] :
        writeHtmlList.append('車號: ' + datalist[item]['PlateNumb'] + '<br>')
        writeTxtList.append('車號: ' + datalist[item]['PlateNumb'] + "\n")
    if 'ManageSta' in datalist[item] :
        writeHtmlList.append('車輛所屬站: ' + datalist[item]['ManageSta'] + '站<br>')
        writeTxtList.append('車輛所屬站: ' + datalist[item]['ManageSta'] + "站\n")
    if 'VehicleType' in datalist[item] :
        writeHtmlList.append('車班類型: ' + datalist[item]['VehicleType'] + "車<br>")
        writeTxtList.append('車班類型: ' + datalist[item]['VehicleType'] + "車\n")        
    if 'StopName' in datalist[item] and 'PlateNumb' in datalist[item] :
        writeHtmlList.append('停靠站: ' + datalist[item]['StopName']['Zh_tw'] + '<br>')
        writeTxtList.append('停靠站: ' + datalist[item]['StopName']['Zh_tw'] + "\n")
    if 'A2EventType' in datalist[item] and 'PlateNumb' in datalist[item] :
        writeHtmlList.append('進站離站: ' + datalist[item]['A2EventType'] + '<br>')
        writeTxtList.append('進站離站: ' + datalist[item]['A2EventType'] + "\n")
    if 'BusStatus' in datalist[item] :
        writeHtmlList.append('行車狀況: ' + datalist[item]['BusStatus'] + '<br>')
        writeTxtList.append('行車狀況: ' + datalist[item]['BusStatus'] + "\n")
    if 'DutyStatus' in datalist[item] :
        writeHtmlList.append('勤務狀態: ' + datalist[item]['DutyStatus'] + '<br>')
        writeTxtList.append('勤務狀態: ' + datalist[item]['DutyStatus'] + "\n")
    if 'Speed' in datalist[item] :
        writeHtmlList.append('車速: ' + str(datalist[item]['Speed'])  + 'kph' + '<br>')
        writeTxtList.append('車速: ' + str(datalist[item]['Speed'])  + 'kph' + "\n")
    if 'BusPosition' in datalist[item] :
        writeHtmlList.append('車輛位置: <a href="http://maps.google.com/?q=' + str(datalist[item]['BusPosition']['PositionLat']) + ',' + str(datalist[item]['BusPosition']['PositionLon']) +'">點我</a>' + "<p>")
        writeTxtList.append('車輛位置: http://maps.google.com/?q=' + str(datalist[item]['BusPosition']['PositionLat']) + ',' + str(datalist[item]['BusPosition']['PositionLon']) +'\n\n')


if __name__ == '__main__' :
    while internet() == False :
        time.sleep(2)
    programset()
    system_sleep_flag = 1
    show_system_sleep_info_flag = 0
    system_error_counter = 0
    vehicle_quantity_data_exist_flag = 0
    while boot_controller == 1 :
        try :
            if datetime.now().strftime("%H") == "23" and show_system_sleep_info_flag == 0 :
                system_sleep_flag = 0
                write_html_file(write_path + "./965_businfo.html","系統休眠中...下次啟動時間為05:00 a.m.")
                show_system_sleep_info_flag = 1
                system_error_counter = 0
                vehicle_quantity_data_exist_flag = 0
            if datetime.now().strftime("%H%M") == "0500" :
                programset()
                system_sleep_flag = 1
                show_system_sleep_info_flag = 0
                
        except Exception as e :
            system_sleep_flag = 0
            writeList = []
            writeList.append("Error Code 0, at time reset")
            writeList.append("時間 : {0} ".format(time.ctime()))
            writeStr = '\n\n'.join(writeList)
            write_text_file(write_path + "./error_message.txt",writeStr)

            # fp = open( write_path + "./error_message.txt", "a")
            # fp.write("Error Code 0, at time reset" + "\n\n")
            # fp.write("時間 : %s \n\n" % time.ctime())
            # fp.close()

        if system_sleep_flag == 1:
            system_error_flag_r1 = 0
            system_error_flag_r2 = 0
            a = Auth(app_id, app_key)
            try :
                response01 = request('get', 'https://ptx.transportdata.tw/MOTC/v2/Bus/RealTimeByFrequency/City/NewTaipei/965?$top=50&$format=JSON', headers= a.get_auth_header())
                decodejson01 =  demjson.decode(response01.content)
            except Exception as e :
                system_error_flag_r1 = 1
                system_error_counter += 1
                writeList = []
                writeList.append("PTX RealTimeByFrequency Error!")
                writeList.append("時間 : {0} ".format(time.ctime()))
                writeStr = '\n\n'.join(writeList)
                write_text_file(write_path + "./error_message.txt",writeStr)
            
            try :
                response02 = request('get', 'https://ptx.transportdata.tw/MOTC/v2/Bus/RealTimeNearStop/City/NewTaipei/965?$top=50&$format=JSON', headers= a.get_auth_header())
                decodejson02 =  demjson.decode(response02.content)
            except Exception as e :
                system_error_flag_r2 = 1
                system_error_counter += 1
                writeList = []
                writeList.append("PTX RealTimeNearStop Error!")
                writeList.append("時間 : {0} ".format(time.ctime()))
                writeStr = '\n\n'.join(writeList)
                write_text_file(write_path + "./error_message.txt",writeStr)

            if system_error_flag_r1 == 1 and system_error_flag_r2 == 1 :
                system_error_flag = 1
            else :
                system_error_flag = 0

            datalist = {}
            carlist = []
            obtain_PTX_data_flag = 0
            outbound_count = 0

            if system_error_flag_r1 == 0 :
                try :
                    for item in decodejson01 :
                        datalist[item['PlateNumb']] = {}
                        datalist[item['PlateNumb']]['PlateNumb'] = item['PlateNumb']  
                        carlist.append(item['PlateNumb'])
                        carlist.sort()
                        for i in vehiclejson :
                            if i["LicensePlate"] == item['PlateNumb'] :
                                datalist[item['PlateNumb']]['ManageSta'] =i['ManageSta']
                                datalist[item['PlateNumb']]['VehicleType'] =i['VehicleType']    
                                if item.get('DutyStatus' , 2) != 2 :
                                    for items in stalist :
                                        if items == i['ManageSta'] and (item['PlateNumb'] not in bus_sta_list[str(items)]) :
                                            bus_sta_count[str(items)] += 1
                                            bus_sta_list[str(items)].append(item['PlateNumb'])
                                            bus_sta_list[str(items)].sort()

                        if item['Direction'] == 0 :
                            datalist[item['PlateNumb']]['Direction'] = '金瓜石'
                            outbound_count += 1
                        else:
                            datalist[item['PlateNumb']]['Direction'] = '板橋'
                        if item['DutyStatus'] == 0 :
                            datalist[item['PlateNumb']]['DutyStatus'] = '正常'
                        elif item['DutyStatus'] == 1 :
                            datalist[item['PlateNumb']]['DutyStatus'] = '開始'
                        else:
                            datalist[item['PlateNumb']]['DutyStatus'] = '結束'
                        if item['BusStatus'] == 0 :
                            datalist[item['PlateNumb']]['BusStatus'] = '正常'
                        elif item['BusStatus'] == 1 :
                            datalist[item['PlateNumb']]['BusStatus'] = '車禍'
                        elif item['BusStatus'] == 2 :
                            datalist[item['PlateNumb']]['BusStatus'] = '故障'
                        elif item['BusStatus'] == 3 :
                            datalist[item['PlateNumb']]['BusStatus'] = '塞車'
                        elif item['BusStatus'] == 4 :
                            datalist[item['PlateNumb']]['BusStatus'] = '緊急求援'
                        elif item['BusStatus'] == 5 :
                            datalist[item['PlateNumb']]['BusStatus'] = '加油'
                        elif item['BusStatus'] == 90 :
                            datalist[item['PlateNumb']]['BusStatus'] = '不明'
                        elif item['BusStatus'] == 91 :
                            datalist[item['PlateNumb']]['BusStatus'] = '去回不明'
                        elif item['BusStatus'] == 98 :
                            datalist[item['PlateNumb']]['BusStatus'] = '偏移路線'
                        elif item['BusStatus'] == 99 :
                            datalist[item['PlateNumb']]['BusStatus'] = '非營運狀態'
                        elif item['BusStatus'] == 100 :
                            datalist[item['PlateNumb']]['BusStatus'] = '客滿'
                        elif item['BusStatus'] == 101 :
                            datalist[item['PlateNumb']]['BusStatus'] = '包車出租'
                        else :
                            datalist[item['PlateNumb']]['BusStatus'] = '未知'
                        datalist[item['PlateNumb']]['Speed'] = item['Speed']
                        datalist[item['PlateNumb']]['BusPosition'] = item['BusPosition']
                        obtain_PTX_data_flag = 1
                        vehicle_quantity_data_exist_flag = 1

                except Exception as e :
                    system_error_flag = 1
                    obtain_PTX_data_flag = 0
                    vehicle_quantity_data_exist_flag = 0
                    writeList = []
                    writeList.append("Error Code 1, at item in decodejson01 : " + str(e))
                    writeList.append("decodejson01 : " + str(decodejson01))
                    writeList.append("時間 : {0} ".format(time.ctime()))
                    writeStr = '\n\n'.join(writeList)
                    write_text_file(write_path + "./error_message.txt",writeStr)
    
            if system_error_flag_r2 == 0 :
                try:
                    for item in decodejson02 :
                        if item['PlateNumb'] not in datalist :
                            datalist[item['PlateNumb']] = {}
                            datalist[item['PlateNumb']]['PlateNumb'] = item['PlateNumb']
                            carlist.append(item['PlateNumb'])
                            carlist.sort()
                            for i in vehiclejson :
                                if i["LicensePlate"] == item['PlateNumb'] :
                                    datalist[item['PlateNumb']]['ManageSta'] =i['ManageSta']
                                    datalist[item['PlateNumb']]['VehicleType'] =i['VehicleType']
                                    if item.get('DutyStatus' , 2) != 2 :
                                        for items in stalist :
                                            if items == i['ManageSta'] and (item['PlateNumb'] not in bus_sta_list[str(items)]) :
                                                bus_sta_count[str(items)] += 1
                                                bus_sta_list[str(items)].append(item['PlateNumb'])
                                                bus_sta_list[str(items)].sort()

                            if item['Direction'] == 0 :
                                datalist[item['PlateNumb']]['Direction'] = '金瓜石'
                                outbound_count += 1
                            else :
                                datalist[item['PlateNumb']]['Direction'] = '板橋'

                        if item.get('DutyStatus' , 3) != 3 :
                            if datalist.get(item['PlateNumb'] , {}).get('DutyStatus' , -1) == -1 :
                                if item['DutyStatus'] == 0 :
                                    datalist[item['PlateNumb']]['DutyStatus'] = '正常'
                                elif item['DutyStatus'] == 1 :
                                    datalist[item['PlateNumb']]['DutyStatus'] = '開始'
                                else:
                                    datalist[item['PlateNumb']]['DutyStatus'] = '結束'

                        if item.get('BusStatus' , 999) != 999 :
                            if datalist.get(item['PlateNumb'] , {}).get('BusStatus' , -1) == -1 :
                                if item['BusStatus'] == 0 :
                                    datalist[item['PlateNumb']]['BusStatus'] = '正常'
                                elif item['BusStatus'] == 1 :
                                    datalist[item['PlateNumb']]['BusStatus'] = '車禍'
                                elif item['BusStatus'] == 2 :
                                    datalist[item['PlateNumb']]['BusStatus'] = '故障'
                                elif item['BusStatus'] == 3 :
                                    datalist[item['PlateNumb']]['BusStatus'] = '塞車'
                                elif item['BusStatus'] == 4 :
                                    datalist[item['PlateNumb']]['BusStatus'] = '緊急求援'
                                elif item['BusStatus'] == 5 :
                                    datalist[item['PlateNumb']]['BusStatus'] = '加油'
                                elif item['BusStatus'] == 90 :
                                    datalist[item['PlateNumb']]['BusStatus'] = '不明'
                                elif item['BusStatus'] == 91 :
                                    datalist[item['PlateNumb']]['BusStatus'] = '去回不明'
                                elif item['BusStatus'] == 98 :
                                    datalist[item['PlateNumb']]['BusStatus'] = '偏移路線'
                                elif item['BusStatus'] == 99 :
                                    datalist[item['PlateNumb']]['BusStatus'] = '非營運狀態'
                                elif item['BusStatus'] == 100 :
                                    datalist[item['PlateNumb']]['BusStatus'] = '客滿'
                                elif item['BusStatus'] == 101 :
                                    datalist[item['PlateNumb']]['BusStatus'] = '包車出租'
                                else :
                                    datalist[item['PlateNumb']]['BusStatus'] = '未知'
                        
                        datalist[item['PlateNumb']]['StopName'] = item['StopName']
                        if item['A2EventType'] == 0 :
                            datalist[item['PlateNumb']]['A2EventType'] = '離站'
                        else :
                            datalist[item['PlateNumb']]['A2EventType'] = '進站'
                        obtain_PTX_data_flag = 1
                        vehicle_quantity_data_exist_flag = 1

                except Exception as e :
                    system_error_flag = 1
                    obtain_PTX_data_flag = 0
                    vehicle_quantity_data_exist_flag = 0
                    writeList = []
                    writeList.append("Error Code 2, at item in decodejson02 : " + str(e))
                    writeList.append("decodejson02 : " + str(decodejson02))
                    writeList.append("時間 : {0} ".format(time.ctime()))
                    writeStr = '\n\n'.join(writeList)
                    write_text_file(write_path + "./error_message.txt",writeStr)

            """ if system_error_flag == 0 and vehicle_quantity_data_exist_flag == 1 :
                path = write_path + "./businfo_965/"  + datetime.now().strftime("%Y%m%d")
                if not os.path.isdir(path) :
                    os.mkdir(path)
                try :
                    fp = open( path +  "/" + datetime.now().strftime("%Y%m%d") + "_" + "hour=" + datetime.now().strftime("%H") + ".txt", "a")
                    ft = open( write_path + "./965_businfo.html", "w")
                    ft_html = open( write_path + "./965_json_data.html", "w")

                except Exception as e :
                    system_error_flag = 1
                    obtain_PTX_data_flag = 0
                    vehicle_quantity_data_exist_flag = 0
                    writeList = []
                    writeList.append("Error Code 3, at open file : " + str(e))
                    writeList.append("時間 : {0} ".format(time.ctime()))
                    writeStr = '\n\n'.join(writeList)
                    write_text_file(write_path + "./error_message.txt",writeStr) """
                    
            if system_error_flag == 0 and vehicle_quantity_data_exist_flag == 1 :
                try :
                    writeHtmlList = []
                    writeTxtList = []
                    writeHtmlList.append('<head><meta http-equiv="refresh" content="5" /><head>')                                  
                    writeHtmlList.append("======== 965 本日出車 ========<p>")
                    writeTxtList.append("======== 965 本日出車 ========\n\n")
                    for i in range(len(stalist)) :
                        if bus_sta_count[str(stalist[i])] != 0 :
                            value = 0
                            writeHtmlList.append(str(stalist[i]) + "站 (" + str(bus_sta_count[str(stalist[i])]) + "輛) :<br>")
                            writeTxtList.append(str(stalist[i]) + "站 (" + str(bus_sta_count[str(stalist[i])]) + "輛) :\n")
                            for item in bus_sta_list[str(stalist[i])] :
                                if value != 0 :
                                    writeHtmlList.append(",")
                                    writeTxtList.append(",")
                                writeHtmlList.append(str(item))
                                writeTxtList.append(str(item))
                                value += 1
                            writeHtmlList.append("<p>")
                            writeTxtList.append("\n\n")


                    if obtain_PTX_data_flag == 1 :
                        writeHtmlList.append("======= 即時車輛動態 ========<br>")
                        writeTxtList.append("======= 即時車輛動態 ========\n")
                        writeHtmlList.append("======= 去程 往金瓜石 ========<p>")
                        writeTxtList.append("======= 去程 往金瓜石 ========\n\n")

                        for items in carlist :
                            for item in datalist :
                                if 'Direction' in datalist[item] and item == items:
                                    if datalist[item]['Direction'] == '金瓜石' and outbound_count != 0:
                                        informationwrite(datalist)
                                        outbound_count -= 1
                                        break

                        writeHtmlList.append("======= 返程 往板橋 ========<p>")
                        writeTxtList.append("======= 返程 往板橋 ========\n\n")
                        for items in carlist :
                            for item in datalist :
                                if 'Direction' in datalist[item] and item == items:
                                    if datalist[item]['Direction'] == '板橋' and outbound_count == 0 :
                                        informationwrite(datalist)
                                        break

                except Exception as e :
                    system_error_flag = 1
                    obtain_PTX_data_flag_flag = 0
                    vehicle_quantity_data_exist_flag = 0
                    writeList = []
                    writeList.append("Error Code 4, at item in datalist : " + str(e))
                    writeList.append("時間 : {0} ".format(time.ctime()))
                    writeStr = '\n\n'.join(writeList)
                    write_text_file(write_path + "./error_message.txt",writeStr)

            if system_error_flag == 0 and vehicle_quantity_data_exist_flag == 1:
                try:
                    system_error_counter = 0
                    writeHtmlList.append("Updated: {0} <br>".format(time.ctime()))
                    writeHtmlList.append("資料介接自交通部PTX平臺")
                    writeTxtList.append("Updated: 時間 : {0} \n\n".format(time.ctime()))
                    path = write_path + "./businfo_965/"  + datetime.now().strftime("%Y%m%d")
                    if not os.path.isdir(path) :
                        os.mkdir(path)
                    writeHtmlStr = ''.join(writeHtmlList)
                    writeTxtStr = ''.join(writeTxtList)
                    write_html_file(write_path + "./965_businfo.html",writeHtmlStr)
                    write_text_file(path +  "/" + datetime.now().strftime("%Y%m%d") + "_hour=" + datetime.now().strftime("%H") + ".txt",writeTxtStr)

                except Exception as e :
                    system_error_flag = 1
                    writeList = []
                    writeList.append("Error Code 5, at write : " + str(e))
                    writeList.append("時間 : {0} ".format(time.ctime()))
                    writeStr = '\n\n'.join(writeList)
                    write_text_file(write_path + "./error_message.txt",writeStr)

        if system_error_counter < 10 :
            try :
                time.sleep( 60 - int(datetime.now().strftime("%S")))
            except :
                time.sleep( 60 )
        else :
            try :
                write_html_file(write_path + "./965_businfo.html","System out of service because of PTX platform error",write_type = 'a')
            except :
                print("Write Error01")
            time.sleep( 600 )