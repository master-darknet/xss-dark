import sys, getopt
import colorama
import requests
import time
from pprint import pprint
from bs4 import BeautifulSoup as bs 
from urllib.parse import urljoin
import json
from payload import PayloadsInfo
from pyfiglet import Figlet
import re


if sys.version > '3':
    import urllib.parse as urlparse
    import urllib.parse as urllib

else:
    import urlparse
    import urllib


try:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()

except:
    pass

G = '\033[92m'  # green
Y = '\033[93m'  # yellow
B = '\033[94m'  # blue
R = '\033[91m'  # red
W = '\033[0m'   # white

def no_color():
   global G,B,Y,R,W
   G=B=R=Y=W=''

def banner():
    xira_banner = Figlet(justify='left')
    xb = Figlet(font='slant', justify='left' )
    print(  R + xb.renderText('XSS-dark'))
    print( G + "~#  Dasturchi: @darknet_off1cial ")
    print( Y + "~# Kanal: @termux_private ")
banner()

def custom_cookie(url):
    res = requests.get(url)
    soup = bs(res.content, "html.parser")
    if res.cookies:
        for cookie in res.cookies:
            cookie = input("Enter cookie : ")
            print("Cookie Session = "+ cookie)
        cookies = {cookie}
        return soup.find_all("form"), cookies
    return [soup.find_all("form")]

def get_all_forms(url):
    
   
    response = requests.get(url)
    soup = bs(response.content, "html.parser")
    if response.cookies:
        for cookie in response.cookies:
            print("Cookie Session= "+ cookie.value)
        cookies = {cookie.name: cookie.value}
        return soup.find_all("form"),cookies
    return [soup.find_all("form")]

def get_all_payloads():

    return PayloadsInfo('payload.json')

def get_form_details(form):
    

    details = {}

    
    action = form.attrs.get("action").lower()
    
   
    method = form.attrs.get("method", "get").lower()

    
    inputs = []

    for input_tag in form.find_all("input"):
        payload_value=""
        payload_type = input_tag.attrs.get("type")
        payload_name = input_tag.attrs.get("name")
        payload_pattern = input_tag.attrs.get("pattern")
        if input_tag.attrs.get("pattern"):
            pattern = payload_pattern
        else:
            pattern = None
        if input_tag.attrs.get("type") == "hidden":
            if input_tag.attrs.get("value"):
                payload_value = input_tag.attrs.get("value")
        inputs.append({"type": payload_type,"name": payload_name,"value":payload_value,"pattern":pattern})
    pattern = None
    for input_tag in form.find_all("textarea"):
        payload_name = input_tag.attrs.get("name")
        inputs.append({"type": "textarea", "name": payload_name, "value":payload_value, "pattern":pattern})
   
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
   
    return details

def submit_form(form_details, url, value, cookies):
 
    target_url = urljoin(url, form_details["action"]) 
    
  
    inputs = form_details["inputs"]
    data = {}
    
    for input in inputs:
        
        if input["type"] == "text" or input["type"] == "search" or input["type"] == "email" or input["type"] == "textarea":
            input["value"] = value
            if input["type"] == "email":
                input["value"] = "some@blabla.com"
            
            if input['pattern']:
                input["value"] = "http://evil.com"
        payload_name = input.get("name")
        payload_value = input.get("value")
        if payload_name and payload_value :
            
            data[payload_name] = payload_value
    
    if form_details["method"] == "post":
        if cookies:
            return requests.post(target_url, data=data, cookies=cookies)
        else:
            return requests.post(target_url, data=data)
    else:
        if cookies:
            return requests.get(target_url, params=data, cookies=cookies)
        else:
            return requests.get(target_url, params=data)


def xira(url):
    
    forms = get_all_forms(url)
    redirect = False
   
    if (len(forms) == 2): 
        cookie = forms[1]
    else:
        cookie = None
    print( '%s [+] Aniqlandi %s shakllar yoqilgan %s%s'%(R,len(forms[0]), url ,Y ) ) 
    if (len(forms[0])==0):
        print("Shunday qilib, biz bu erda hech qanday kiritish shaklini olmaymiz. Biz hozir chiqamiz! " )
    else:
        with open ('payload.json','r', encoding="utf-8") as file:
             payload_data = json.load(file)
             file.close()
             try:
                 is_vulnerable = False
                 for form in forms[0]:
                     form_details = get_form_details(form)
                     print(form_details)
                     
                     for payload_name in payload_data.values():
                         print("har bir foydali yukdan o'tish: " )
                         for payload in payload_name: 
                             for payload_name in payload.values(): 
                                payload_name = str(payload_name)
                                

                                content_raw = submit_form(form_details,url,payload_name,cookie)
                                if content_raw.history:
                                 
                                    if str(content_raw.history[0])[11:14] == "302":
                                        redirect = True
                                content = submit_form(form_details,url,payload_name,cookie).content.decode()
                                
                                soup = bs(content, "html.parser")
                                elem = [soup.get_text()]
                             
                                matches = [match for match in elem if payload_name in match]
                                

                                xss_attr = None
                                for tag in soup.find_all(re.compile("^i")):
                                    xss_attr = [match for match in tag.attrs if "on" in match] 
                                    
                                if redirect:
                                    check_stored = requests.get(url)
                                    redirect = False
                                    soup = bs(check_stored.text, "html.parser")
                                    if payload_name in check_stored.text:
                                        print("%s [+] saqlanmalarga kirish yoqilgan %s%s" %( G, Y, url))
                                        print("%s [*] Tavfsilotlarsan: %s%s" %(Y,B,R) )
                                        pprint(form_details)
                                        
                                        print("%s  Muvafaqiyatli yuk: %s"%( G ,payload_name))
                                        is_vulnerable = True
                                    else:
                                        print("%s saqlangan, kiritilmagan. " %(R) )
                                if xss_attr:
                                    print("%s [+] Xss aniqlandi %s%s" %( G, Y, url))
                                    print("%s [*] tavfsilotlardan: %s%s" %(Y,B,R) )
                                    pprint(form_details)

                                if matches:
                                    print("%s Xss zaiflik topilmadi! " %(R) )
                                elif payload_name in content:

                                   print("%s [+] xss zaiflik aniqlandi %s%s" %( G, Y, url))
                                   print("%s [*] tafsilotlardan: %s%s" %(Y,B,R) )
                                   pprint(form_details)

                                   print("%s Muvafaqiyatli yuk : %s"%( G ,payload_name))
                                   is_vulnerable = True
                                else:
                                   print("%s xss aniqlanmadi " %(R) )
                                
                                
                 return is_vulnerable
             except KeyboardInterrupt as key:
                 print(key)
                 pass

             except ConnectionError as error:
                 print(error)
                 pass
            
             except Exception as error:
                  print (error)
                  pass
     
         
if __name__ == '__main__':
    try:
      opts, args = getopt.getopt(sys.argv[1:],"hu:",["url="])
    except getopt.GetoptError:
        print('xss-dark.py -u <url>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('xss-dark.py -u <url>')
            print('xss-dark.py -c <cookie> -u <url>')
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg
            print(xira(url))
        elif opt in ("-c", "--cookie", "-u", "--url"):
            cookie = arg
            print(xira(url))      
