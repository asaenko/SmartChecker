# -*- coding: utf-8 -*-
"""Check if memory leaks in FlexiNG AS/SAB nodes
VALIDITY: NG3.1, NG3.2
"""
import re
from libs.checker import CheckStatus,ResultInfo
from libs.flexing import get_ng_version

## Mandatory variables
##--------------------------------------------
module_id = 'NG20150518.01'
name      = "memory_leak"
version   = '1.0'
desc      = __doc__
tags      = ['flexing','china']
priority  = 'critical'

mem_threshold = {'AS':110,'SAB':500}  #MB
criteria      = "memory usage: AS < %(AS)sMB or SAB < %(SAB)sMB" % mem_threshold
##--------------------------------------------

## Optional variables

pat_memfail = re.compile("ssh ([\w\d-]+) showstat\|.*?mem_alloc_failed_for_linear_filters = (\d+)",re.DOTALL)
pat_memallo = re.compile("info ([\w\d-]+) featuremem.*FASTPATH_MALLOC dynamic allocated bytes \[chunks\]: (\d+)/(\d+)")

##

def check_memory_fail_counter(loglines):
    _logblk=''.join(loglines)
    status = CheckStatus.UNKNOWN
    info = []
    error = ''

    _results = pat_memfail.findall(_logblk)
    for node,cnt in set(_results):
        if int(cnt) > 0:
            status = CheckStatus.FAILED
            info.append("%s has %s times memory failed." % (node,cnt))

    return status,info,error

def check_memory_allocation(loglines):
    status = CheckStatus.UNKNOWN
    info = []
    error = ''
    _mem = {'AS':[],'SAB':[]}

    for line in loglines:
        r2 = pat_memallo.search(line)
        if r2:
            mem = int(r2.groups()[1])/1024.0/1024.0
            node = r2.groups()[0]
            node_type = re.sub('[\d+-]','',node)
            _mem[node_type].append((node,mem))
            #print "mem allocated!",node,mem,result.status
            if mem > mem_threshold[node_type]:
                status = CheckStatus.FAILED
                info.append('%s memory is closing to full: %.5s MB' %(node, mem))

    if status !=CheckStatus.FAILED:
        for ntype,memlist in _mem.items():
            if len(memlist) == 0: continue
            maxmem=sorted(memlist,key=lambda x:x[1],reverse=True)[0]
            info.append('%s has a max memory %.6s MB' % maxmem)

    return status,info,error

## Mandatory function: run
def run(logfile, *args, **kwargs):
    "this function execute the check steps and return "
    loglines = file(logfile).readlines()
    result = ResultInfo(name)
    info = []
    error = ''

    ngversion=get_ng_version(logfile)
    if ngversion[0][:3] == '3.2':
        status,info,error = check_memory_fail_counter(loglines)
        if status == CheckStatus.FAILED and len(info)>0:
            result.status = status


    ## check function 2
    status,_info,error = check_memory_allocation(loglines)

    if status==CheckStatus.UNKNOWN:
        result.status = CheckStatus.PASSED

    result.load(info=info,error=error)
    return result
