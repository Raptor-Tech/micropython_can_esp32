import network 
from network import WLAN
import time
import json
import binascii
import machine
import os 
import btelnet as telnet

###############################################################
import esp32
nvs = esp32.NVS("raptor")
#start file logger
###############################################################
########
try:
    def nvs_set(key,value):
        if type(value) is int:
            nvs.set_i32(key,value)
        else:
            nvs.set_blob(key,value)
        nvs.commit()

    def nvs_get(key):
        buf = bytearray(200)
        try: 
            len = nvs.get_blob(key,buf)
            return (str(buf[0:len], 'utf-8'))
        except:
            try:
                return nvs.get_i32(key)
            except: 
                print("exception NVS_GET: " + key)
                nvs_set(key,0)
                return 0

    wlan = WLAN(network.STA_IF)
    wlan.active(True)
    host = 'RC-' + str(binascii.hexlify(machine.unique_id()),"UTF-8")
    wlan.config(dhcp_hostname = host)
    wifi_networks = sorted(wlan.scan(), key=lambda x: x[3], reverse=True)
    print(wifi_networks)
    ssids = [net[0] for net in wifi_networks]    
    networks = [{'ssid':'provisionraptor', 'password':'rosCore1!'}]

    print(networks)
    connected = 0
    for match in networks:
        for ssid in ssids:
            if match['ssid'] in ssid: 
                if not wlan.isconnected(): 
                    print("Connecting to wifi...." + str(ssid) + " " + str(match["password"]))
                    print(ssid.decode('utf-8'), match["password"])
                    wlan.connect(ssid.decode('utf-8'), match["password"])
                    for retries in range(5):
                        time.sleep(2)
                        if wlan.isconnected():
                            wlan_reconnect_timer  = time.ticks_ms()
                            ssid = ssid
                            break
                        else: 
                            print("Retrying connection")
                        retries+=1
    if b'provisionraptor' in ssids:
        for x in range(5):
            if wlan.isconnected():
                telnet.start(wlan)    
                debug = machine.UART(1, baudrate=115200, tx=42,rx=41)
                os.dupterm(debug)
                break
            else: time.sleep(1) 

except Exception as e: print("BOOT SEQUENCE FAILED: " + str(e))
print("Boot sequence completed")

