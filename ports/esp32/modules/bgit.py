# ugit
# micropython OTA update from github
# Created by TURFPTAx for the openmuscle project
# Check out https://openmuscle.org for more info
#
# Pulls files and folders from open github repository

import os
import urequests
import json
import hashlib
import binascii
import machine
import time
import network

global internal_tree

###############################################################
import esp32
nvs = esp32.NVS("raptor")
#start file logger
###############################################################
########

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
#### -------------User Variables----------------####
#### 
# Default Network to connect using wificonnect()
# ssid = "OpenMuscle"
# password = "3141592653"

# CHANGE TO YOUR REPOSITORY INFO
# Repository must be public if no personal access token is supplied
# user = 'Raptor-Tech'
# repository = 'Test'

# Change this variable to 'master' or any other name matching your default branch
# default_branch = 'v0.3'

# Don't remove ugit.py from the ignore_files unless you know what you are doing :D
# Put the files you don't want deleted or updated here use '/filename.ext'
# ignore_files = ['/lib/ugit.py', '/cf/machine.yml']
# ignore = ignore_files
### -----------END OF USER VARIABLES ----------####

# Static URLS
# GitHub uses 'main' instead of master for python repository trees
# giturl = 'https://github.com/{user}/{repository}'
# call_trees_url = f'https://api.github.com/repos/{user}/{repository}/git/trees/{default_branch}?recursive=1'
# raw = f'https://raw.githubusercontent.com/{user}/{repository}/master/'

def pull(f_path,raw_url, no_pull, token = ''):
  if f_path in no_pull:
     print("Not pulling %s" % f_path)
     return False
  else:
    #print(f'pulling {f_path} from github')
    #files = os.listdir()
    headers = {'User-Agent': 'APRaptortech'} 
    # ^^^ Github Requires user-agent header otherwise 403
    if len(token) > 0:
        headers['authorization'] = "bearer %s" % token 
    r = urequests.get(raw_url, headers=headers)
    try:
      with open(f_path, 'w')  as f:
        f.write(r.content.decode('utf-8'))

    except Exception as e:
      print(e)
      print("########################WOULD HAVE RESET HERE###########################################")
      #machine.reset()

    return True  
  
def pull_all(tree_url,raw,ignore,no_pull, token = ''):
  os.chdir('/')
  tree = pull_git_tree(tree_url, token=token )
  #internal_tree = build_internal_tree()
  #internal_tree = remove_ignore(internal_tree, ignore = ignore)
  #print(' ignore removed ----------------------')
  #print(internal_tree)
  log = []
  # download and save all files
  for i in tree['tree']:
    if i['type'] == 'tree':
      try:
        os.mkdir(i['path'])
      except:
        #print(f'failed to {i["path"]} dir may already exist')
        pass
    elif i['path'] not in ignore:
      '''
      try:
        
        os.remove(i['path'])
        log.append(f'{i["path"]} file removed from int mem')
        internal_tree = remove_item(i['path'],internal_tree)
      except Exception as e:
        print(str(e))
        log.append(f'{i["path"]} del failed from int mem')
        print('failed to delete %s' % i['path'])
      '''
      try:
        print(raw + i['path'])
        if pull(i['path'],raw + i['path'],no_pull, token=token):
          log.append(i['path'] + ' updated')
      except:
        log.append(i['path'] + ' failed to pull')
        #machine.reset()
        print("########################WOULD HAVE RESET HERE###########################################")
  '''
  # delete files not in Github tree
  if len(internal_tree) > 0:
      print(internal_tree, ' leftover!')
      for i in internal_tree:
          os.remove(i)
          log.append(i + ' removed from int mem')
  '''
  with open('ugit_log.py','w') as logfile:
    logfile.write(str(log))

  #return check instead return with global
  
def build_internal_tree():
  global internal_tree
  internal_tree = []
  os.chdir('/')
  for i in os.listdir():
    add_to_tree(i)
  return(internal_tree)

def add_to_tree(dir_item):
  global internal_tree
  if is_directory(dir_item) and len(os.listdir(dir_item)) >= 1:
    #print("is file")
    os.chdir(dir_item)
    for i in os.listdir():
      add_to_tree(i)
    os.chdir('..')
  else:
    #print(dir_item)
    if os.getcwd() != '/':
      subfile_path = os.getcwd() + "/" + dir_item
    else:
      subfile_path = os.getcwd() + dir_item
    try:
      #print(f'sub_path: {subfile_path}')
      hash = get_hash(subfile_path)
      internal_tree.append([subfile_path, hash])
    except Exception as e: #type: ignore # for removing the type error indicator :)
      print(f'{dir_item} could not be added to tree')
      print(str(e))


def get_hash(file):
  #print(file)
  o_file = open(file)
  r_file = o_file.read()
  sha1obj = hashlib.sha1(r_file)
  hash = sha1obj.digest()
  return(binascii.hexlify(hash))

def get_data_hash(data):
    sha1obj = hashlib.sha1(data)
    hash = sha1obj.digest()
    return(binascii.hexlify(hash))
  
def is_directory(file):
  directory = False
  try:
    return (os.stat(file)[8] == 0)
  except:
    return directory
    
def pull_git_tree(tree_url, token = ''):
  headers = {'User-Agent': 'APRaptortech'} 
  # ^^^ Github Requires user-agent header otherwise 403
  if len(token) > 0:
      headers['authorization'] = "bearer %s" % token 
  r = urequests.get(tree_url,headers=headers)
  data = json.loads(r.content.decode('utf-8'))
  if 'tree' not in data:
      print('\nDefault branch "main" not found. Set "default_branch" variable to your default branch.\n')
      raise Exception(f'Default branch {default_branch} not found.') 
  tree = json.loads(r.content.decode('utf-8'))
  return(tree)
  
def parse_git_tree():
  tree = pull_git_tree()
  dirs = []
  files = []
  for i in tree['tree']:
    if i['type'] == 'tree':
      dirs.append(i['path'])
    if i['type'] == 'blob':
      files.append([i['path'],i['sha'],i['mode']])
  print('dirs:',dirs)
  print('files:',files)
   
   
def check_ignore(tree,ignore):
  os.chdir('/')
  tree = pull_git_tree()
  check = []
  # download and save all files
  for i in tree['tree']:
    if i['path'] not in ignore:
        print(i['path'] + ' not in ignore')
    if i['path'] in ignore:
        print(i['path']+ ' is in ignore')
        
def remove_ignore(internal_tree,ignore):
    clean_tree = []
    int_tree = []
    for i in internal_tree:
        int_tree.append(i[0])
    for i in int_tree:
        if i not in ignore:
            clean_tree.append(i)
    return(clean_tree)
        
def remove_item(item,tree):
    culled = []
    for i in tree:
        if item not in i:
            culled.append(i)
    return(culled)

token = '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'

def update_file(target_file = '', user = "Raptor-Tech",repository = "RaptorOS_RC", token = token):
    print(target_file +' to newest version')
    url = f'https://raw.githubusercontent.com/{user}/{repository}/main/'
    print(url)
    #raw_url = 'https://raw.githubusercontent.com/turfptax/ugit/master/'
    pull(target_file,url+target_file,[],token = token)
    print("File update completed")
'''
from connectivity.ugit import update_file
update_file(target_file = "cf/appcf.json")
update_file(target_file = "lib/connectivity/sender.py")

'''
def backup():
    int_tree = build_internal_tree()
    backup_text = "ugit Backup Version 1.0\n\n"
    for i in int_tree:
        data = open(i[0],'r')
        backup_text += f'FN:SHA1{i[0]},{i[1]}\n'
        backup_text += '---'+data.read()+'---\n'
        data.close()
    backup = open('ugit.backup','w')
    backup.write(backup_text)
    backup.close()


def get_releases(user, repo, token):
    url = f'https://api.github.com/repos/{user}/{repo}/releases'
    headers = {"User-Agent": "APRaptortech", "Accept": "application/vnd.github.v3+json", 'authorization':"bearer %s" % token}
    res = urequests.get(url, headers=headers)
    if res.status_code != 200:
        print("Request failed: %s" % res.status_code)
        return None
    else:
        releases = []
        for x in res.json():
            releases.append(x['tag_name'])
        return releases



def update_code(target_version, user = "Raptor-Tech",repository = "RaptorOS_RC", token = token):
  index_target = None
  current_version = nvs_get("FW")

  n = 0
  while n < 5:  
    try:
      if target_version == 'latest':
        target_version = get_releases(user, repository, token)[0]
        index_target = 0
      else:
        available_versions = get_releases(user, repository, token)
        index_target = available_versions.index(target_version)
      break
    except Exception as e:
        print("Update failed: %s" % e)
        n += 1

  if index_target is not None:
    print("Current version: %s" % current_version)
    print("Target version found: %s" % target_version)
    if current_version == target_version:
        print("Current version (%s) is up to date." % current_version)
    elif index_target is not None:
        print("Setting NVS: " + target_version)
        nvs_set("FWT",target_version)
        print("NVS SET: " + nvs_get("FWT"))
        #ignore = ['/lib/ugit.py', '/cf/machine.yml'] #doesn't delete these files
        ignore = []
        #no_pull = ['pymakr.conf','cf/appcf.json','lib/connectivity/ble_advertising.py','lib/connectivity/ble_service.py','lib/interfaces/RX8130.py','lib/interfaces/slip.py','lib/percept/s_CAS.py','lib/percept/s_CTRL.py','lib/connectivity/ublox.py','lib/connectivity/mqtt_s2.py']                 #doesn't download these files
        no_pull = []                 #doesn't download these files
        call_trees_url = f'https://api.github.com/repos/{user}/{repository}/git/trees/{target_version}?recursive=1'
        raw = f'https://raw.githubusercontent.com/{user}/{repository}/{target_version}/'
        global default_branch
        default_branch = target_version
        print("New version available: %s, updating code..." % target_version)
        pull_all(call_trees_url, raw, ignore, no_pull, token = token)
        nvs_set("FW",target_version)
        print('resetting machine in 5: machine.reset()')
        time.sleep(5)
        machine.reset()
  else:
     print("Update failed")


import os
def rmdir(dir):
    for i in os.listdir(dir):
        os.remove('{}/{}'.format(dir,i))
    os.rmdir(dir)
'''
with open("/sd/test.py", "wb") as f:
  f.write("test")


with open("/sd/test.py", "rb") as f:
  print(f.read())
'''
