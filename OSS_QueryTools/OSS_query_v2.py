#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys,getopt
import os
import time
import datetime
import decimal
import cx_Oracle
from NSNG_OSS_config import NSNG_OSS_config

class QueryOptions(object):
    def __init__(self):
        self.selectelement = ''             # 网元名称      （'SHMME03BNK'/'SHSAEGW03BNK'/'ALL')
        self.startdate = ''                 # 查询的开始日期 ('2016/07/01')
        self.starttime = ''                 # 查询的开始时间（'09'(小时)）
        self.starttimemm = ''               # 查询的开始时间（'00'(分钟)）
        self.starttimeall = ''              # 查询的开始时间（'0910'(小时+分钟)）
        self.stopdate = ''                  # 查询的结束日期 ('2016/07/01')
        self.stoptime = ''                  # 查询的结束时间（'10'(小时)）
        self.stoptimemm = ''                # 查询的结束时间（'30'(分钟)）
        self.stoptimeall = ''               # 查询的开始时间（'1030'(小时+分钟)）
        self.selectperiod = '15'            # 查询的时间间隔（'15'/'60'(15分钟/每小时))
        self.selectunittype = 'NE'          # 查询的统计粒度（'NE'(MME)/'TAC','NE'(SAEGW)/'Session')
        self.selectcounters = ''            # 查询的Counters（'EPS_EME_ATTACH_FAIL',填入网管数据库里的对应Counter的列名）
        self.reportfilename = ''            # 查询后输出的文件名 ('xxxx.json')
        self.localsave = '1'                # 查询数据是否需要输出到本地文件('0'/'1')
    
    def getQueryoptions(self,info):
        result = 0
        curdate=time.strftime('%Y/%m/%d',time.localtime(time.time()))
        curtime=time.strftime('%H%M',time.localtime(time.time()))

        opts, args = getopt.getopt(info[1:], "e:c:D:T:d:t:p:u:l:") 
        lenofargs=len(opts)
        #print lenofargs
        
        for op, value in opts: 
            if op == "-e": 
                self.selectelement = value 
            elif op == "-D": 
                self.startdate = value 
            elif op == "-T": 
                self.starttime = value[0:2]
                self.starttimemm = value[2:] 
                self.starttimeall = value
            elif op == "-d": 
                self.stopdate = value 
            elif op == "-t": 
                self.stoptime = value[0:2]
                self.stoptimemm = value[2:]
                self.stoptimeall = value
            elif op == "-p": 
                self.selectperiod = value
            elif op == "-u": 
                self.selectunittype = value
            elif op == "-c":
                self.selectcounters = value
            elif op == "-l":
                self.localsave = value
            elif op == "-R":
                self.reportfilename = value

        if (self.selectelement == None or self.selectelement == ''):
	        self.selectelement = 'ALL'
        if (self.stopdate == None or self.stopdate == ''):
	        self.stopdate=curdate
        if (self.startdate == None or self.startdate == ''):
	        self.startdate=self.stopdate
        if (self.stoptime == None or self.stoptime == ''):
            self.stoptime = curtime[0:2]
            self.stoptimemm = curtime[2:] 
            self.stoptimeall = curtime
        if (self.starttime == None or self.starttime == ''):
            t = time.strptime(self.stopdate+'/'+self.stoptimeall,'%Y/%m/%d/%H%M')
            dt = datetime.datetime(t[0],t[1],t[2],t[3],t[4],t[5])
            startdatetimeall = (dt+datetime.timedelta(minutes=-30)).strftime('%Y/%m/%d/%H%M')
            self.startdate = startdatetimeall[0:10]
            self.starttime = startdatetimeall[11:13]
            self.starttimemm = startdatetimeall[11:13] 
            self.starttimeall = startdatetimeall[11:15]
        if (self.selectperiod == None or self.selectperiod == ''):
	        self.selectperiod='60'
        if (self.selectunittype == None or self.selectunittype == ''):
	        self.selectunittype='NE'
        if (self.selectcounters == None or self.selectcounters == ''):
	        self.selectcounters=''
        if (self.localsave == None or self.localsave == ''):
	        self.localsave='1'
        if self.selectcounters == '':
            printusage('Please input the counters !',info)
            result = 1
            return result
        
        if (self.reportfilename == None or self.reportfilename == ''):
            fnstartdate = self.startdate.replace("/","")
            fnstopdate = self.stopdate.replace("/","")
            if (not os.path.exists("./Reports/")):
                os.makedirs(r"./Reports/")
            self.reportfilename = "NESta_" + self.selectelement + '_' + fnstartdate + self.starttimeall + "_" + fnstopdate + self.stoptimeall + "_" + self.selectperiod + "_" + self.selectunittype + ".json"
        
        print "Report File Name: " + self.reportfilename
        
        if (lenofargs<7):
            QueryOptionsString = 'Now query options: \n' 
            QueryOptionsString = QueryOptionsString + 'Start Date : ' + self.startdate +'\n'
            QueryOptionsString = QueryOptionsString + 'Stop Date : ' + self.stopdate +'\n'
            QueryOptionsString = QueryOptionsString + 'Start Time : ' + self.starttime + ':' + self.starttimemm + '\n'
            QueryOptionsString = QueryOptionsString + 'Stop Time : ' + self.stoptime + ':' + self.stoptimemm + '\n'
            QueryOptionsString = QueryOptionsString + 'Element : ' + self.selectelement +'\n'
            QueryOptionsString = QueryOptionsString + 'Period : ' + self.selectperiod +'\n' 
            QueryOptionsString = QueryOptionsString + 'Unit Type : ' + self.selectunittype +'\n'
            QueryOptionsString = QueryOptionsString + 'LocalSave : ' + self.localsave +'\n'
            QueryOptionsString = QueryOptionsString + 'ReportFileName : ' + self.reportfilename +'\n'
            QueryOptionsString = QueryOptionsString + 'if these options are not what you want, please give parameters as usage :'
            printusage(QueryOptionsString,info)
        
        return result

def printusage(UsageString,info):
    print UsageString
    print "Usage:	" + info[0] + " -D2015/04/03 -T0400 -d2015/04/03 -t0500 -eSHMME03BNK -cSUCC_COMBINED_ATTACH -p60 -uNE -l1 -RReport_20160701.json"
    print "-D (Start Date   :2015/04/02)"
    print "-T (Start Time   :0500)"
    print "-d (Stop Date    :2015/04/02)"
    print "-t (Stop Time    :0600)"
    print "-e (Element      :SHMME03BNK/ALL)"
    print "-c (Counter      :SUCC_COMBINED_ATTACH)"
    print "-p (Period       :15/60)"
    print "-u (Unittype     :Type NE/TAC/session)"
    print "-l (Localsave    :0/1 (Not/Yes)"
    print "-R (ReportName   :'Report_xxxx.json')"

def getDatabaseName(nsng_oss_ne, elementname):
    databasename = ''
    if (elementname == 'ALL'):
        return nsng_oss_ne['NE'][0]['database']
    for i in nsng_oss_ne['NE']:
        if i['name'] == elementname:
            databasename = i['database']
    return databasename

def getDatabase_config(nsng_oss_database,database_name):
    datebase_config = {}
    for i in nsng_oss_database['database']:
        if i['name'] == database_name:
            database_config = i
    return database_config

def getTables_config(nsng_oss_tables_views,column_name_list):
    request_column_list = column_name_list.split(',')
    return_column_list = []
    return_table_name = ''
    for table in nsng_oss_tables_views['NE_OSS_table_view']:
        for column in table['tables']['columns']['column']:
            if column in request_column_list:
                return_column_list.append(column)
        if (len(return_column_list) > 0):
            return_table_name = table['tables']['name']
            break
    return return_column_list,return_table_name

def getSQLstring(table_name,column_list,queryoptions):
    SelectString = ''
    FromString = ''
    WhereString = ''

    # Generate Select String
    SelectString = '''
select
objects.CO_NAME,
to_char(period_start_time,'yyyy/mm/dd') Sdate,
to_char(period_start_time,'hh24:mi') Stime,
'''
    if (queryoptions.selectunittype=='NE'):
        SelectString = SelectString + "'ALL' as ElementType,\n"
    else:
        SelectString = SelectString + queryoptions.selectunittype + " as ElementType,\n"

    SelectString = SelectString + queryoptions.selectcounters + '\n'

    # Generate From String
    FromString = 'from ' + table_name + ' g , UTP_COMMON_OBJECTS objects '

    # Generate Where String
    WhereString = """
where 
g.FINS_ID=objects.CO_GID 
"""
    if (queryoptions.selectelement != 'ALL'):
        WhereString = WhereString + " and objects.co_name = '" + queryoptions.selectelement + "'" 
    WhereString = WhereString + " and to_char(g.period_start_time,\'yyyy/mm/dd/hh24mi\')>=\'"+queryoptions.startdate+"/"+queryoptions.starttimeall+"\' and to_char(g.period_start_time,\'yyyy/mm/dd/hh24mi\')<=\'"+queryoptions.stopdate+"/"+queryoptions.stoptimeall + "\' "

    return SelectString + FromString + WhereString

def write_column(reportfile,x):
    firstcolumn = 1
    for y in x:
        if (firstcolumn == 1):
            reportfile.write('\t\t"' + str(y) + '"')
            firstcolumn = 0
        else:
            reportfile.write(',\n\t\t"' + str(y) + '"')

def makeQueryoptions(info):
    # Get query config
    queryoptions = QueryOptions()
    result = 1
    if (queryoptions.getQueryoptions(info) == 0):
        result = 0
    return queryoptions , result

def GenerateReport(rowinfo , queryoptions):
    if (queryoptions.localsave == '1'):
        queryresult , result = GenerateReportFile(rowinfo , queryoptions)
    else:
        queryresult , result = GenerateReportData(rowinfo , queryoptions)
    return queryresult , result

def GenerateReportData(rowinfo , queryoptions):
    queryresult = {}
    columndesc = []
    columndesc.append("NE_NAME")
    columndesc.append("Date")
    columndesc.append("Time")
    columndesc.append("StatType")
    for column_name in queryoptions.selectcounters.split(':'):
        columndesc.append(column_name)
    
    queryresult['columndesc'] = columndesc

    columns = []
    for x in rowinfo:
        column = []
        for y in x:
            column.append(str(y))
        columns.append(column)
    queryresult['cloumns'] = columns

    return queryresult , ''

def GenerateReportFile(rowinfo , queryoptions):
    result = ''
    try:
        if (not os.path.exists("./Reports/")):
            os.makedirs(r"./Reports/")
        reportfile = open('./Reports/' + queryoptions.reportfilename,'w')
    except Exception , e:
        result = 'Reportfile : ./Reports/' + queryoptions.reportfilename + ' can not create. '
        return None , result
    # json 'columndesc' is query result 's column name
    reportfile.write('{\n')
    reportfile.write('\t"columndesc": [\n')
    reportfile.write('\t\t"NE_NAME",\n')
    reportfile.write('\t\t"Date",\n')
    reportfile.write('\t\t"Time",\n')
    reportfile.write('\t\t"StatType"')
    for column_name in queryoptions.selectcounters.split(':'):
        reportfile.write(',\n')
        reportfile.write('\t\t"' + column_name + '"\n')
    reportfile.write('\t],\n')
    
    # json 'columns' is query result 's column value
    firstrow = 1
    reportfile.write('\t"columns": [\n')
    for x in rowinfo:
        if (firstrow == 1):
            reportfile.write('\t[\n')
            firstrow = 0
            write_column(reportfile,x)
        else:
            reportfile.write(',\n\t[\n')
            write_column(reportfile,x)
        
        reportfile.write('\n\t]')
    reportfile.write('\n\t]')
        
    reportfile.write('\n}')
    reportfile.close()
    return reportfile , result

def GenerateQueryData(queryoptions):

    result = ''
    # Get oss config 
    nsng_oss_configs = NSNG_OSS_config()
    nsng_oss_tables_views = nsng_oss_configs.NSNG_OSS_tables_views
    nsng_oss_database = nsng_oss_configs.NSNG_OSS_database
    nsng_oss_ne = nsng_oss_configs.NSNG_OSS_NE
    
    # Get Database config
    database_name = getDatabaseName(nsng_oss_ne,queryoptions.selectelement)
    if (database_name == ''):
        result = 'Can not get the database name according to the element name(' + queryoptions.selectelement + ')'
        
    print 'database_name: ' + database_name

    database = getDatabase_config(nsng_oss_database,database_name)
    if (database == {}):
        result = 'Can not get the database config according to the database name(' + database_name + ')'
        
    # Get Tables Views config
    column_list,table_name = getTables_config(nsng_oss_tables_views,queryoptions.selectcounters)
    
    # Get Database Connection
    # db = cx_Oracle.connect('omc', 'omc', '127.0.0.1:51063/oss')
    try:
        db = cx_Oracle.connect(database['user'] , database['password'] , database['ip'] + ':' + database['port'] + '/' + database['db'])
    except Exception, e:
        result = '\nDatabse Conntect Exception :' + str(e.message)
        return None , result

    # Get SQL
    try:
        SQLstring = getSQLstring(table_name,column_list,queryoptions)
        SQLstring = SQLstring
        print '\nSQLstring:' + SQLstring
        cursor=db.cursor()
        cursor.execute(SQLstring)
        row1=cursor.fetchall()
    except Exception, e:
        result = '\nDatabse Query Exception :' + str(e.message)
        return None , result

    if (result != ''):    
        return None , result
    else:
        queryresult , result = GenerateReport(row1,queryoptions)
        if (queryresult == None):
            return None ,  "Generate Report have error!"
        else:
            return queryresult ,  ""
    
    
if __name__ == "__main__":
    queryoptioninfo , result = makeQueryoptions(sys.argv)
    if (result != 0):
        printusage('Error in argv:',sys.argv)
        sys.exit(1)
    queryresult , result = GenerateQueryData(queryoptioninfo)
    if (result != ''):
        print result + ' , please check parameter or contact the code developer.'  

