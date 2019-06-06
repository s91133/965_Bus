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

app_id = 'c2867a08b8f741b9bef1900b2c12c55a'
app_key = 'ebQiA77NHGeX_pi-HnWxlmuTU1g'
write_path = "/home/pi/www/"

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
      """
      Host: 8.8.8.8 (google-public-dns-a.google.com)
      OpenPort: 53/tcp
      Service: domain (DNS/TCP)
      """
      try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
      except Exception as ex:
        print (ex.message)
        return False

def programset():
    global var
    global vehiclejson
    global stajson
    global bus_list
    global stalist
    global buscount

    try :
        fp = open( write_path + "./start.txt","r")
        chk = fp.read()
        fp.close()
        if int(chk) == 1 :
            var = 1
        else :
            var = 0
        fp2 = open(write_path + "./VehicleInfo.txt","r")
        vehiclejson = demjson.decode(fp2.read())
        fp2.close()

        fp = open(write_path + "./ManageStaInfo.txt","r")
        stajson = demjson.decode(fp.read())
        fp.close()

        stalist = []
        for item in stajson:
            if item["ManageSta"] not in stalist :
                stalist.append(item["ManageSta"])

        bus_list = {}
        buscount = {}

        for i in stalist:
            bus_list[str(i)] = []
            buscount[str(i)] = 0

    except Exception as e :
        fp = open( write_path + "./error_message.txt", "a")
        fp.write("Program initialization failed !" + "\n\n")
        fp.write("時間 : %s \n\n" % time.ctime())
        fp.close()
        var = 0


if __name__ == '__main__' :
    while internet() == False :
        time.sleep(2)
    programset()
    timechk = 1
    var1 = 0
    var2 = 0
    while var == 1 :
        try :
            if datetime.now().strftime("%H") == "23" and var1 == 0 :
                timechk = 0
                print("System Sleep")
                ft1 = open( write_path + "./965_businfo.html", "w")
                ft1.write("Non-working hours")
                ft1.close()
                var1 = 1
                var2 = 0
            if datetime.now().strftime("%H%M") == "0500" :
                programset()
                timechk = 1
                var1 = 0
                
        except Exception as e :
            timechk = 0
            fp = open( write_path + "./error_message.txt", "a")
            fp.write("Error Code 0, at time reset" + "\n\n")
            fp.write("時間 : %s \n\n" % time.ctime())
            fp.close()

        if timechk == 1:
            error_val_r1 = 0
            error_val_r2 = 0
            a = Auth(app_id, app_key)
            try :
                response01 = request('get', 'https://ptx.transportdata.tw/MOTC/v2/Bus/RealTimeByFrequency/City/NewTaipei/965?$top=50&$select=PlateNumb&$format=JSON', headers= a.get_auth_header())
                decodejson01 =  demjson.decode(response01.content)
            except Exception as e :
                error_val_r1 = 1
                var2 += 1
                fp = open( write_path + "./error_message.txt", "a")
                fp.write("PTX RealTimeByFrequency Error!" + "\n\n")
                fp.write("時間 : %s \n\n" % time.ctime())
                fp.close()
            
            try :
                response02 = request('get', 'https://ptx.transportdata.tw/MOTC/v2/Bus/RealTimeNearStop/City/NewTaipei/965?$top=50&$format=JSON', headers= a.get_auth_header())
                decodejson02 =  demjson.decode(response02.content)
            except Exception as e :
                error_val_r2 = 1
                var2 += 1
                fp = open( write_path + "./error_message.txt", "a")
                fp.write("PTX RealTimeNearStop Error!" + "\n\n")
                fp.write("時間 : %s \n\n" % time.ctime())
                fp.close()

            if error_val_r1 == 1 and error_val_r2 == 1 :
                error_val = 1
            else :
                error_val = 0

            datalist = {}
            write_check = 0
            outbound_count = 0

            if error_val_r1 == 0 :
                try :
                    for item in decodejson01 :
                        datalist[item['PlateNumb']] = {}
                        datalist[item['PlateNumb']]['PlateNumb'] = item['PlateNumb']  
                        for i in vehiclejson :
                            if i["LicensePlate"] == item['PlateNumb'] :
                                datalist[item['PlateNumb']]['ManageSta'] =i['ManageSta']
                                datalist[item['PlateNumb']]['VehicleType'] =i['VehicleType']    
                                if item.get('DutyStatus' , 2) != 2 :
                                    for items in stalist :
                                        if items == i['ManageSta'] and (item['PlateNumb'] not in bus_list[str(items)]) :
                                            buscount[str(items)] += 1
                                            bus_list[str(items)].append(item['PlateNumb'])
                                            tmp = bus_list[str(items)][len(bus_list[str(items)])-1]
                                            j = len(bus_list[str(items)]) - 2
                                            while j >= 0 and tmp < bus_list[str(items)][j] :
                                                bus_list[str(items)][j + 1] = bus_list[str(items)][j]
                                                j = j - 1
                                            bus_list[str(items)][ j + 1 ] = tmp  

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
                        write_check = 1

                except Exception as e :
                    error_val = 1
                    write_check = 0
                    fp = open( write_path + "./error_message.txt", "a")
                    fp.write("Error Code 1, at item in decodejson01 : " + str(e) + "\n\n")
                    fp.write("decodejson01 : " + str(decodejson01) + "\n\n")
                    fp.write("時間 : %s \n\n" % time.ctime())
                    fp.close()
    
            if error_val_r2 == 0 :
                try:
                    for item in decodejson02 :
                        if item['PlateNumb'] not in datalist :
                            datalist[item['PlateNumb']] = {}
                            datalist[item['PlateNumb']]['PlateNumb'] = item['PlateNumb']
                            for i in vehiclejson :
                                if i["LicensePlate"] == item['PlateNumb'] :
                                    datalist[item['PlateNumb']]['ManageSta'] =i['ManageSta']
                                    datalist[item['PlateNumb']]['VehicleType'] =i['VehicleType']
                                    if item.get('DutyStatus' , 2) != 2 :
                                        for items in stalist :
                                            if items == i['ManageSta'] and (item['PlateNumb'] not in bus_list[str(items)]) :
                                                buscount[str(items)] += 1
                                                bus_list[str(items)].append(item['PlateNumb'])

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
                        write_check = 1

                except Exception as e :
                    error_val = 1
                    write_check = 0
                    fp = open( write_path + "./error_message.txt", "a")
                    fp.write("Error Code 2, at item in decodejson02 : " + str(e) + "\n\n")
                    fp.write("decodejson02 : " + str(decodejson02) + "\n\n")
                    fp.write("時間 : %s \n\n" % time.ctime())
                    fp.close()

            if error_val == 0 and write_check == 1 :
                path = write_path + "./businfo_965/"  + datetime.now().strftime("%Y%m%d")
                if not os.path.isdir(path) :
                    os.mkdir(path)
                try :
                    fp = open( path +  "/" + datetime.now().strftime("%Y%m%d") + "_" + "hour=" + datetime.now().strftime("%H") + ".txt", "a")
                    ft = open( write_path + "./965_businfo.html", "w")

                except Exception as e :
                    error_val = 1
                    write_check = 0
                    fp = open( write_path + "./error_message.txt", "a")
                    fp.write("Error Code 3, at open file : " + str(e) + "\n\n")
                    fp.write("時間 : %s \n\n" % time.ctime())
                    fp.close()
                    
            if error_val == 0 and write_check == 1 :
                try :
                    var3 = 0
                    ft.write( '<head><meta http-equiv="refresh" content="5" /><head>' )

                    fp.write( "======== 965 今日出車 ========\n\n")
                    ft.write( "======== 965 今日出車 ========<p>")
                    for i in range(len(stalist)) :
                        if buscount[str(stalist[i])] != 0 :
                            value = 0
                            fp.write( str(stalist[i]) + "站 (" + str(buscount[str(stalist[i])]) + "輛) :" + "\n")
                            ft.write( str(stalist[i]) + "站 (" + str(buscount[str(stalist[i])]) + "輛) :" + "<br>")
                            for item in bus_list[str(stalist[i])] :
                                if value != 0 :
                                    fp.write( "," )
                                    ft.write( "," )
                                fp.write(str(item))
                                ft.write(str(item))
                                value += 1
                            fp.write( "\n\n" )
                            ft.write( "<p>" )

                    fp.write( "========= 車輛資訊 ==========\n")
                    ft.write( "========= 車輛資訊 ==========<br>")
                    fp.write( "======= 去程 往金瓜石 ========\n\n")
                    ft.write( "======= 去程 往金瓜石 ========<p>")

                    for item in datalist :
                        if 'Direction' in datalist[item] :
                            if datalist[item]['Direction'] == '金瓜石' and outbound_count != 0:
                                if var3 != 0 :
                                    fp.write("\n")
                                    ft.write('<br>')
                                if 'PlateNumb' in datalist[item] :
                                    fp.write('車號: ' + datalist[item]['PlateNumb'] + "\n")
                                    ft.write('車號: ' + datalist[item]['PlateNumb'] + '<br>')
                                if 'ManageSta' in datalist[item] :
                                    fp.write('車輛所屬站: ' + datalist[item]['ManageSta'] + "站\n")
                                    ft.write('車輛所屬站: ' + datalist[item]['ManageSta'] + '站<br>')
                                if 'VehicleType' in datalist[item] :
                                    fp.write('車班類型: ' + datalist[item]['VehicleType'] + "車\n")
                                    ft.write('車班類型: ' + datalist[item]['VehicleType'] + "車<br>")
                                if 'BusStatus' in datalist[item] :
                                    fp.write('行車狀況: ' + datalist[item]['BusStatus'] + "\n")
                                    ft.write('行車狀況: ' + datalist[item]['BusStatus'] + '<br>')
                                if 'StopName' in datalist[item] and 'PlateNumb' in datalist[item] :
                                    fp.write('停靠站: ' + datalist[item]['StopName']['Zh_tw'] + "\n")
                                    ft.write('停靠站: ' + datalist[item]['StopName']['Zh_tw'] + '<br>')
                                if 'A2EventType' in datalist[item] and 'PlateNumb' in datalist[item] :
                                    fp.write('進站離站: ' + datalist[item]['A2EventType'] + "\n")
                                    ft.write('進站離站: ' + datalist[item]['A2EventType'] + '<br>')
                                if 'DutyStatus' in datalist[item] :
                                    fp.write('勤務狀態: ' + datalist[item]['DutyStatus'] + "\n")
                                    ft.write('勤務狀態: ' + datalist[item]['DutyStatus'] + '<br>')
                                if 'Speed' in datalist[item] :
                                    fp.write('車速: ' + str(datalist[item]['Speed'])  + 'kph' + "\n")
                                    ft.write('車速: ' + str(datalist[item]['Speed'])  + 'kph' + '<br>')
                                var3 = 1
                                outbound_count -= 1

                    fp.write( "\n======= 返程 往板橋 ========\n\n")
                    ft.write( "<br>======= 返程 往板橋 ========<p>")
                    var3 = 0
                    for item in datalist :
                        if 'Direction' in datalist[item] :
                            if datalist[item]['Direction'] == '板橋' and outbound_count == 0 :
                                if var3 != 0 :
                                    fp.write("\n")
                                    ft.write('<br>')
                                if 'PlateNumb' in datalist[item] :
                                    fp.write('車號: ' + datalist[item]['PlateNumb'] + "\n")
                                    ft.write('車號: ' + datalist[item]['PlateNumb'] + '<br>')
                                if 'ManageSta' in datalist[item] :
                                    fp.write('車輛所屬站: ' + datalist[item]['ManageSta'] + "站\n")
                                    ft.write('車輛所屬站: ' + datalist[item]['ManageSta'] + '站<br>')
                                if 'VehicleType' in datalist[item] :
                                    fp.write('車班類型: ' + datalist[item]['VehicleType'] + "車\n")
                                    ft.write('車班類型: ' + datalist[item]['VehicleType'] + "車<br>")
                                if 'BusStatus' in datalist[item] :
                                    fp.write('行車狀況: ' + datalist[item]['BusStatus'] + "\n")
                                    ft.write('行車狀況: ' + datalist[item]['BusStatus'] + '<br>')
                                if 'StopName' in datalist[item] and 'PlateNumb' in datalist[item] :
                                    fp.write('停靠站: ' + datalist[item]['StopName']['Zh_tw'] + "\n")
                                    ft.write('停靠站: ' + datalist[item]['StopName']['Zh_tw'] + '<br>')
                                if 'A2EventType' in datalist[item] and 'PlateNumb' in datalist[item] :
                                    fp.write('進站離站: ' + datalist[item]['A2EventType'] + "\n")
                                    ft.write('進站離站: ' + datalist[item]['A2EventType'] + '<br>')
                                if 'DutyStatus' in datalist[item] :
                                    fp.write('勤務狀態: ' + datalist[item]['DutyStatus'] + "\n")
                                    ft.write('勤務狀態: ' + datalist[item]['DutyStatus'] + '<br>')
                                if 'Speed' in datalist[item] :
                                    fp.write('車速: ' + str(datalist[item]['Speed'])  + 'kph' + "\n")
                                    ft.write('車速: ' + str(datalist[item]['Speed'])  + 'kph' + '<br>')
                                var3 = 1

                except Exception as e :
                    error_val = 1
                    write_check = 0
                    fp = open( write_path + "./error_message.txt", "a")
                    fp.write("Error Code 4, at item in datalist : " + str(e) + "\n\n")
                    fp.write("時間 : %s \n\n" % time.ctime())
                    fp.close()

            if error_val == 0 and write_check == 1 :
                try:
                    var2 = 0
                    fp.write("\n資料最後更新時間 : %s \n\n" % time.ctime())
                    ft.write("<br>" + "資料最後更新時間 : %s <br>" % time.ctime())
                    fp.close()
                    ft.close()

                except Exception as e :
                    error_val = 1
                    fp = open( write_path + "./error_message.txt", "a")
                    fp.write("Error Code 5, at write : " + str(e) + "\n\n")
                    fp.write("時間 : %s \n\n" % time.ctime())
                    fp.close()
        if var2 < 10 :
            try :
                time.sleep( 60 - int(datetime.now().strftime("%S")))
            except :
                time.sleep( 60 )
        else :
            try :
                ft5 = open( write_path + "./965_businfo.html", "a")
                ft5.write("System out of service because of PTX platform error <br>")
                ft5.close()
            except :
                print("Write Error01")
            time.sleep( 600 )