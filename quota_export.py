#!/usr/bin/python

import papi
import getpass
import json
import sys
import getopt


def get_quotas (cluster, user, password):
  path = "/platform/1/quota/quotas?resolve_names=True"
  (status, reason, resp) = papi.call (cluster, '8080', 'GET', path, '', 'any', 'application/json', user, password)
  if status != 200:
    err_string = "ERROR: Bad Status: " + status
    sys.stderr.write (err_string)
    exit (status)
  return (json.loads(resp))

def byte_convert (bytes,raw):
  if raw == True:
    return (str(bytes))
  if (bytes < 1024):
    bytes_s =  str(bytes)
  elif (bytes >= 1024 and bytes < 1048576):
    bytes = float(bytes) / 1024
    bytes_s = str("%.2f" % bytes) + "K"
  elif (bytes >= 1048576 and bytes < 1073741824):
    bytes = float(bytes) / 1024 / 1024
    bytes_s = str("%.2f" % bytes) + "M"
  elif (bytes >= 1073741824 and bytes < 1099511627776):
    bytes = float(bytes) / 1024 / 1024 / 1024
    bytes_s = str("%.2f" % bytes) + "G"
  else:
    bytes = float(bytes) / 1024 / 1024 / 1024 / 1024
    bytes_s = str("%.2f" % bytes) + "T"
  return (bytes_s)

def usage():
  sys.stderr.write ("Usage: quota_export[.py] {-c | --cluster} cluster_name [-r] [-h]\n")
  sys.stderr.write ("{-c | --cluster} : Name or IP address of any node in the cluster\n")
  sys.stderr.write ("[{-r | --raw} : Raw numbers in bytes\n")
  sys.stderr.write ("[{-h | --help}] : Prints this message\n")  
  exit (0)

cluster=''
raw = False

optlist, args = getopt.getopt (sys.argv[1:], 'c:hr', ["cluster=", "help", "raw"])
for opt, a in optlist:
  if opt in ('-c', '--cluster'):
    cluster = a
  if opt in ('-h', '--help'):
    usage()
  if opt in ('-r', '--raw'):
    raw = True

user = raw_input ("User: ")
password = getpass.getpass ("Password: ")
quotas = get_quotas (cluster, user, password)
print "Type,Applies To,Path,Snap,Hard,Soft,Adv,Used"
for i, q in enumerate (quotas['quotas']):
  qtype = quotas['quotas'][i]['type']
  try:
    quotas['quotas'][i]['persona']['name']
  except TypeError:
    qappl = 'DEFAULT'
  else:
    qappl = quotas['quotas'][i]['persona']['name']
  qpath = quotas['quotas'][i]['path']
  if quotas['quotas'][i]['include_snapshots'] == True:
    qsnap = "Yes"
  else:
    qsnap = "No"
  if type(quotas['quotas'][i]['thresholds']['hard']) is int:
    qhard = byte_convert(quotas['quotas'][i]['thresholds']['hard'],raw)
  else:
    qhard = "-"
  if type(quotas['quotas'][i]['thresholds']['soft']) is int:
    qsoft = byte_convert(quotas['quotas'][i]['thresholds']['soft'],raw)
  else:
    qsoft = "-"
  if type(quotas['quotas'][i]['thresholds']['advisory']) is int:
    qadvise = byte_convert(quotas['quotas'][i]['thresholds']['advisory'],raw)
  else:
    qadvise = "-"
  qusage = byte_convert(quotas['quotas'][i]['usage']['logical'],raw)

  print qtype + "," + qappl + "," + qpath + "," + qsnap + "," + qhard + "," + qsoft + "," + qadvise + "," + qusage
