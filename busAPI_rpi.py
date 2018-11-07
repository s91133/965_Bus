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


if __name__ == '__main__':
    while internet() == False :
        time.sleep(2)
    var = 1
    bus_count_list = []
    while var == 1 :
        a = Auth(app_id, app_key)
        response01 = request('get', 'https://ptx.transportdata.tw/MOTC/v2/Bus/RealTimeByFrequency/City/NewTaipei/965?$top=50&$select=PlateNumb&$format=JSON', headers= a.get_auth_header())
        decodejson01 =  demjson.decode(response01.content)
        
        response02 = request('get', 'https://ptx.transportdata.tw/MOTC/v2/Bus/RealTimeNearStop/City/NewTaipei/965?$top=50&$format=JSON', headers= a.get_auth_header())
        decodejson02 =  demjson.decode(response02.content)

        datalist = {}
        error_val = 0

        try :
            if datetime.now().strftime("%H%M") == "0300" :
                bus_count_list = []
        except Exception as e:
                error_val = 1
                fp = open( "./businfo_rec/error_message.txt", "a")
                fp.write("Error at time reset" + "\n\n")
                fp.close()

        if error_val == 0:
            try :
                for item in decodejson01 :
                    datalist[item['PlateNumb']] = {}
                    datalist[item['PlateNumb']]['PlateNumb'] = item['PlateNumb']
                    if item['PlateNumb'] not in bus_count_list :
                        bus_count_list.append(item['PlateNumb'])

                        tmp = bus_count_list[len(bus_count_list)-1]
                        j = len(bus_count_list) - 2
                        while j >= 0 and tmp < bus_count_list[j] :
                            bus_count_list[j + 1] = bus_count_list[j]
                            j = j - 1
                        bus_count_list[ j + 1 ] = tmp
                        
                    if item['Direction'] == 0 :
                        datalist[item['PlateNumb']]['Direction'] = '金瓜石'
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

            except Exception as e:
                error_val = 1
                fp = open( "./businfo_rec/error_message.txt", "a")
                fp.write("Error at item in decodejson01 : " + str(e) + "\n\n")
                fp.write("decodejson01 : " + str(decodejson01) + "\n\n")
                fp.write("時間 : %s \n\n" % time.ctime())
                fp.close()

    
        if error_val == 0:
            try:
                for item in decodejson02 :
                    if item['PlateNumb'] not in datalist :
                        datalist[item['PlateNumb']] = {}
                    datalist[item['PlateNumb']]['StopName'] = item['StopName']
                    if item['A2EventType'] == 0 :
                        datalist[item['PlateNumb']]['A2EventType'] = '離站'
                    else:
                        datalist[item['PlateNumb']]['A2EventType'] = '進站'

            except Exception as e:
                error_val = 1
                fp = open( "./businfo_rec/error_message.txt", "a")
                fp.write("Error at item in decodejson02 : " + str(e) + "\n\n")
                fp.write("decodejson02 : " + str(decodejson02) + "\n\n")
                fp.write("時間 : %s \n\n" % time.ctime())
                fp.close()

        if error_val == 0:
            path = "./businfo_rec/"  + datetime.now().strftime("%Y%m%d")
            if not os.path.isdir(path) :
                os.mkdir(path)
            try :
                fp = open( path +  "/" + datetime.now().strftime("%Y%m%d") + "_" + "hour=" + datetime.now().strftime("%H") + ".txt", "a")

            except Exception as e :
                error_val = 1
                fp = open( "./businfo_rec/error_message.txt", "a")
                fp.write("Error at open file : " + str(e) + "\n\n")
                fp.write("時間 : %s \n\n" % time.ctime())
                fp.close()
                
        if error_val == 0 :
            try:
                for item in datalist :
                    if 'PlateNumb' in datalist[item] :
                        print( '車號: ' + datalist[item]['PlateNumb'] )
                        fp.write('車號: ' + datalist[item]['PlateNumb'] + "\n")
                    
                    if 'Direction' in datalist[item] :
                        print( '開往: ' + datalist[item]['Direction'] )
                        fp.write('開往: ' + datalist[item]['Direction'] + "\n")

                    if 'BusStatus' in datalist[item] :
                        print( '行車狀況: ' + datalist[item]['BusStatus'] )
                        fp.write('行車狀況: ' + datalist[item]['BusStatus'] + "\n")

                    if 'StopName' in datalist[item] and 'PlateNumb' in datalist[item] :
                        print( '停靠站: ' , datalist[item]['StopName']['Zh_tw'] )
                        fp.write('停靠站: ' + datalist[item]['StopName']['Zh_tw'] + "\n")

                    if 'A2EventType' in datalist[item] and 'PlateNumb' in datalist[item] :
                        print( '進站離站: ' + datalist[item]['A2EventType'] )
                        fp.write('進站離站: ' + datalist[item]['A2EventType'] + "\n")
                    
                    if 'DutyStatus' in datalist[item] :
                        print( '勤務狀態: ' + datalist[item]['DutyStatus'] )
                        fp.write('勤務狀態: ' + datalist[item]['DutyStatus'] + "\n")

                    if 'Speed' in datalist[item] :
                        print( '車速: ' , datalist[item]['Speed']  , 'kph' , "\n")
                        fp.write('車速: ' + str(datalist[item]['Speed'])  + 'kph' + "\n\n")

            except Exception as e:
                error_val = 1
                fp = open( "./businfo_rec/error_message.txt", "a")
                fp.write("Error at item in datalist : " + str(e) + "\n\n")
                fp.write("時間 : %s \n\n" % time.ctime())
                fp.close()

        if error_val == 0 :
            try:
                print( '本日出現車號: ' )
                print(*bus_count_list, sep = ", " ) 
                print("")

                value = 0
                fp.write( "本日出現車號: " + "\n")
                for i in bus_count_list :
                    if value != 0 :
                        fp.write( ", " )
                    if value % 4 ==0 and value != 0 :
                        fp.write("\n")
                    fp.write(str(i))
                    value += 1
                fp.write( "\n\n" )

                print ("資料最後更新時間 : %s \n" % time.ctime())
                fp.write("資料最後更新時間 : %s \n\n" % time.ctime())
                fp.close()

            except Exception as e:
                error_val = 1
                fp = open( "./businfo_rec/error_message.txt", "a")
                fp.write("Error at write : " + str(e) + "\n\n")
                fp.write("時間 : %s \n\n" % time.ctime())
                fp.close()
        
        time.sleep( 60 )
        
os.system("pause")