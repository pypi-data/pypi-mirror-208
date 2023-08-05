import pandas as pd 
import os
import json
from pandas import to_datetime
from flask import request, make_response, Flask 
import urllib.parse
import datetime
from pandarallel import pandarallel
import numpy as np
from functools import partial
import traceback
import loggerutility as logger
import re
import sys
import matplotlib
from prophet import Prophet
from DatabaseConnectionUtility import Oracle, SAPHANA, InMemory, Dremio, MySql, ExcelFile, Postgress, MSSQLServer, Tally, ProteusVision, SnowFlake, FileURL, RestAPI
import requests
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences 
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM,Dense, Dropout, SpatialDropout1D
from tensorflow.keras.layers import Embedding, serialize
from tensorflow import keras
import googletrans
from googletrans import Translator   
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import Dense, Input, GlobalMaxPooling1D
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Embedding, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.initializers import Constant
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import joblib
from rasamodelandtrain import Rasa
from openAIInsight import OpenAI_PineConeVector

class IncentiveCalculation:

    pandarallel.initialize()
    
    df = None
    detSql = None
    sqlQuery = None
    lookupTableMap = {}
    queryStringMap = {}
    currentDetData = None
    CPU_COUNT = os.cpu_count()
    errorId = ""
    dbDetails = None
    calculationData=""
    val="" 
    group_style =""
    outputType="JSON"
    group=""
    colum=""
    pool = None
    isPool  = 'false'
    minPool = 2
    maxPool = 100
    timeout = 180
    editorId=""
    userId=""
    visualId=""
    tableHeading =""
    argumentList = None
    advancedFormatting=None 
    isColumnChange= 'true'   
    isSqlChange= 'true'      
    transpose="false"
    dataSourceType="S"
    fileName=""
    transId=""
    auth_key=""
    serverUrl=""
    userName=""
    password= "" 
    jsonDataResponse=""
    dataSourceColumlist = []
    modelScope="G"    
    
    def getConnection(self):
       
        if self.dbDetails != None:
                # Added by SwapnilB for dynamically creating instance of DB class on [ 10-AUG-22 ] [ START ] 
                klass = globals()[self.dbDetails['DB_VENDORE']]
                dbObject = klass()
                self.pool = dbObject.getConnection(self.dbDetails)
                # Added by SwapnilB for dynamically creating instance of DB class on [ 10-AUG-22 ]  [ END ] 
                
        return self.pool

    def getQueryData(self, jsonData=None, isWebsocet=None):
        try:
            con = None
            logger.log(f'\n This code is From queryandprocessdata Package', "0")
            logger.log(f'\n Print time on start : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
            
            if isWebsocet == "true":
                print("jsonData in getQueryData:", jsonData, type(jsonData))
                domData = jsonData
            else:
                domData = request.get_data('jsonData', None)
                domData = domData[9:]
            self.calculationData = json.loads(domData)
            logger.log(f'\n Inside getQueryData jsonData : {self.calculationData}', "0")

            if 'isSqlChange' in self.calculationData.keys():
                if self.calculationData.get('isSqlChange') != None:
                    self.isSqlChange = self.calculationData['isSqlChange']

            if 'isColumnChanges' in self.calculationData.keys():
                if self.calculationData.get('isColumnChanges') != None:
                    self.isColumnChange = self.calculationData['isColumnChanges']   

            if 'editorId' in self.calculationData.keys():
                if self.calculationData.get('editorId') != None:
                    self.editorId = self.calculationData['editorId']   

            if 'userId' in self.calculationData.keys():
                if self.calculationData.get('userId') != None:
                    self.userId = self.calculationData['userId']   
            
            if 'visualId' in self.calculationData.keys():
                if self.calculationData.get('visualId') != None:
                    self.editorId = self.calculationData['visualId']   

            if 'tableHeading' in self.calculationData.keys():
                if self.calculationData.get('tableHeading') != None:
                    self.tableHeading = self.calculationData['tableHeading']        
        
            if 'argumentList' in self.calculationData.keys():
                if self.calculationData.get('argumentList') != None:
                    argumentList_withOperator = self.calculationData['argumentList']   
                    if len(argumentList_withOperator) > 0: 
                        argumentList_withOperator = json.loads(argumentList_withOperator)
                    logger.log(f"argumentList_withOperator::: {argumentList_withOperator}","0" )
                    if bool(argumentList_withOperator):
                        logger.log(f"inside argumentList not empty condition  ::: ","0" )
                        self.argumentList = self.removeOperator(argumentList_withOperator)
                    else:
                        logger.log(f"self.argumentList is empty:: {self.argumentList}","0")
                    logger.log(f"self.argumentList ::: {self.argumentList}","0" )
        
            if 'advancedFormatting' in self.calculationData.keys():
                if self.calculationData.get('advancedFormatting') != None:
                    self.advancedFormatting = self.calculationData['advancedFormatting']

            if 'dbDetails' in self.calculationData.keys() and self.calculationData.get('dbDetails') != None:
                if 'DATA_SOURCE_TYPE' in self.calculationData['dbDetails'] and self.calculationData.get('dbDetails')['DATA_SOURCE_TYPE'] != None:
                    self.dataSourceType = self.calculationData['dbDetails']['DATA_SOURCE_TYPE']
                    logger.log(f'\n self.dataSourceType : {self.dataSourceType}', "0")

            sql = self.calculationData['source_sql']
            
            self.dbDetails = self.calculationData['dbDetails']
            if self.dataSourceType == "S":
                self.pool = self.getConnection()

            if self.dbDetails != None:
                if self.dbDetails['DB_VENDORE'] == 'Oracle':
                    if self.isPool == 'true':
                        con = self.pool.acquire()
                    else:
                        con = self.pool
                else:
                    con = self.pool

            if 'update ' in sql or 'delete ' in sql:
                return self.getErrorXml("Invalid SQL" , "Update and Delete operations are not allowed in Visual.")
            else:
                if self.isSqlChange == 'true':
                    logger.log(f'\n Print time for before executing source_sql : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                    
                    if self.dataSourceType == "F":          
                        klass = globals()[self.dbDetails['DB_VENDORE']]
                        fileObject = klass()
                        self.df = fileObject.getData(self.calculationData)
                        logger.log(f"fileURL self.df shape:: {self.df.shape}","0")
                        
                    elif self.dataSourceType == "R":
                        klass = globals()[self.dbDetails['DB_VENDORE']]
                        APIObject = klass()
                        self.df = APIObject.getData(self.calculationData)
                        logger.log(f"\nRestAPI self.df:: {self.df}\n {type(self.df)}\n","0")
                        if type(self.df)== str :
                            if "Errors" in self.df:
                                return str(self.df)
                        elif type(self.df)== dict :
                            if "Errors" in self.df["Root"]:
                                return str(self.df)
                        else:
                            logger.log(f"'Errors' key not found :: {self.df}","0")
                        logger.log(f"RestAPI self.df shape:: {self.df.shape}","0")
                    
                    elif self.dataSourceType == "S":
                        self.df = pd.read_sql(sql, con)
                        logger.log(f"self.df type-S read_sql :::::{self.df}{type(self.df)}","0")
                        
                    else:
                        logger.log(f"Invalid dataSourceType:::::{self.dataSourceType}","0")

                    logger.log(f'\n Print time for after executing source_sql : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                    self.store(self.df, self.userId, self.editorId, self.visualId, 'sourceSql')
                else:
                    self.df = self.read(self.userId, self.editorId, self.visualId, 'sourceSql')

            self.df.columns = self.df.columns.str.strip().str.lower()
            
            if con:
                if self.dbDetails != None:
                    if self.dbDetails['DB_VENDORE'] == 'Oracle':
                        if self.isPool == 'true' :
                            self.pool.release(con)

            udf_divide = partial(self.udf_divide)
            udf_round = partial(self.udf_round)
            contribution = partial(self.contribution)               # Added by AniketG on [16-Aug-2022] for calculating percentage
            forecast = partial(self.forecast)
            trainemodel = partial(self.trainemodel)
            predict = partial(self.predict)
            translate = partial(self.translate)

            #logger.log(f'\n Print sourcesql result ::: \n {self.df}', "0")

            if not self.df.empty:
                
                if self.isColumnChange == 'true':
      
                    for key in self.calculationData:

                        if key == 'column':
                            detailArr = self.calculationData[key]
                            
                            for detail in detailArr:
                                self.currentDetData = detail

                                if "line_no" in detail:
                                    self.errorId = 'errDetailRow_' + str(detail['line_no'])
                                
                                if detail['calc_type'] == 'S':
                                    logger.log(f'\n Inside getQueryData calc_expression for type SQL : {detail["calc_expression"]}', "0")
                                    self.detSql = detail['calc_expression']
                                    logger.log(f'\n Print time for type SQL before performing applyFunction : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                                    
                                    if detail['calc_expression'] != None:
                                        self.df[detail['col_name'].lower().strip()] = self.df.apply(lambda row : self.getSqlResult(row, self.pool, detail), axis=1)
                                    else:
                                        self.df[detail['col_name'].lower().strip()] = self.df.parallel_apply(lambda x : None, axis=1)

                                    logger.log(f'\n Print time for type SQL after performing applyFunction : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")

                                elif detail['calc_type'] == 'F':
                                    logger.log(f'\n Inside getQueryData calc_expression for type Forecast : {detail["calc_expression"]}', "0")
                                    expr = detail['col_name'].lower().strip() + '=' + detail['calc_expression'].lower().strip()
                                    logger.log(f'\n Print time for type Forecast before performing applyFunction : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                                    
                                    if detail['calc_expression'] != None:
                                            self.df = forecast()
                                        
                                    else:
                                        self.df = self.df.eval(detail['col_name'].lower().strip() + '=' + None)

                                    logger.log(f'\n Print time for type Forecast after performing applyFunction : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")

                                elif detail['calc_type'] == 'E':
                                    logger.log(f'\n Inside getQueryData calc_expression for type EXPRESSION : {detail["calc_expression"]}', "0")
                                    expr = detail['col_name'].lower().strip() + '=' + detail['calc_expression'].lower().strip()
                                    logger.log(f'\n Print time for type EXPRESSION before performing applyFunction : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                                    
                                    if detail['calc_expression'] != None:
                                        self.df = self.df.eval(expr)
                                    else:
                                        self.df = self.df.eval(detail['col_name'].lower().strip() + '=' + None)

                                    logger.log(f'\n Print time for type EXPRESSION after performing applyFunction : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")

                                elif detail['calc_type'] == 'L':
                                    logger.log(f'\n Inside getQueryData calc_expression for type LOOKUP : {detail["calc_expression"]}', "0")
                                    self.detSql = detail['calc_expression']
                                    
                                    logger.log(f'\n Print time for type LOOKUP before performing applyFunction : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                                    
                                    if detail['calc_expression'] != None:
                                        self.df[detail['col_name'].lower().strip()] = self.df.apply(lambda row : self.getLookUpValue(row, self.pool), axis=1)
                                    else:
                                        self.df[detail['col_name'].lower().strip()] = self.df.apply(lambda row : self.getLookUpValue(row, self.pool), axis=1)

                                    logger.log(f'\n Print time for type LOOKUP after performing applyFunction : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")

                                elif detail['calc_type'] == 'C':
                                    logger.log(f'\n Inside getQueryData calc_expression for type CONDITIONAL EXPRESSION : {detail["calc_expression"]}', "0")
                                    logger.log(f'\n Print time for type CONDITIONAL EXPRESSION before performing applyFunction : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                                    
                                    if detail['calc_expression'] != None:
                                        exprArr = detail['calc_expression'].lower().split(':')
                                        condition = exprArr[0]
                                        trueExpr = None
                                        falseExpr = None
                                        if exprArr[1] != None:
                                            trueExpr = exprArr[1]
                                        if exprArr[2] != None:
                                            falseExpr = exprArr[2]
                                        self.df[detail['col_name'].lower().strip()] = self.udf_if(self.df, condition, trueExpr, falseExpr)
                                    else:
                                        self.df = self.df.eval(detail['col_name'].lower().strip() + ' = ' + None)

                                    logger.log(f'\n Print time for type CONDITIONAL EXPRESSION after performing applyFunction : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                                    
                                elif detail['calc_type'] == 'U':
                                    logger.log(f'\n Inside getQueryData calc_expression for type Cumulative Sum : {detail["calc_expression"]}', "0")
                                    logger.log(f'\n Print time for type Cumulative Sum before performing applyFunction : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                                    
                                    if detail['calc_expression'] != None:
                                        columnArrList = detail['calc_expression'].lower().split(',')
                                        cumsumColumn = columnArrList[0]
                                        if len(columnArrList) == 1:
                                            self.df[detail['col_name'].lower().strip()] = self.df[cumsumColumn].cumsum()
                                        else:
                                            del columnArrList[0]
                                            self.df[detail['col_name'].lower().strip()] = self.df.groupby(columnArrList)[cumsumColumn].cumsum()
                                    else:
                                        self.df[detail['col_name'].lower().strip()] = self.df.parallel_apply(lambda x : None, axis=1)

                                elif detail['calc_type'] == 'N':
                                    logger.log(f'\n Inside getQueryData UserDefine for type EXPRESSION : {detail["calc_expression"]}', "0")
                                    expr = detail['col_name'].lower().strip() + '=' + detail['calc_expression'].lower().strip()
                                    logger.log(f'\n Print time for type EXPRESSION before performing applyFunction : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                                    
                                    if detail['calc_expression'] != None:
                                        self.df = self.df.eval(expr)
                                    else:
                                        self.df = self.df.eval(detail['col_name'].lower().strip() + '=' + None)

                                    logger.log(f'\n Print time for type EXPRESSION after performing applyFunction : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")

                    self.store(self.df, self.userId, self.editorId, self.visualId, 'final')               
                else:
                    self.df = self.read(self.userId, self.editorId, self.visualId, 'final')        
            else:
                returnErr = self.getErrorXml("No records found against the source sql", "")
                logger.log(f'\n Print exception returnSring inside getQueryData : {returnErr}', "0")
                return str(returnErr)
            
            #logger.log(f'\n End of query datatypes:::\n {self.df.dtypes}', "0")
            self.df.columns = self.df.columns.str.strip().str.lower()
            
            if self.calculationData.get('sorting_col_name'):
                sortingColName = self.calculationData['sorting_col_name']
                if sortingColName != "":
                    sortingColName = sortingColName.lower().strip()
                    self.df.sort_values(by=[sortingColName], inplace=True, ascending=True)
            
            dbDataTypes = self.df.dtypes.to_json()
            #self.df = self.df.to_json(orient='records')
            #logger.log(f'\n End of query data:::\n {self.df}', "0")
            
            if 'visualJson' in self.calculationData.keys():
                if self.calculationData.get('visualJson') != None:
                    visualJson = self.calculationData['visualJson']

            if 'OutputType' in self.calculationData.keys():
                if self.calculationData.get('OutputType') != None:
                    self.outputType = self.calculationData['OutputType']      
            
            if 'columnHeading' in self.calculationData.keys():
                if self.calculationData.get('columnHeading') != None:
                    columnHeading = self.calculationData['columnHeading']        
            
            if 'oldColumnHeading' in self.calculationData.keys():
                if self.calculationData.get('oldColumnHeading') != None:
                    oldColumnHeading = self.calculationData['oldColumnHeading']        

            if self.outputType == 'HTML':
                #logger.log(f'\n Print dataframe at end::: \n {self.df}', "0")
                visualJson1 = json.loads(visualJson)
                columnHeading = columnHeading.split(",")
                self.df.rename(columns=dict(zip(self.df.columns, columnHeading)), inplace=True)
                oldColumnHeading = oldColumnHeading.split(",")
            
                if 'groups' in visualJson1.keys():
                    if len(visualJson1.get('groups')) != 0:    
                        self.group = visualJson1['groups']

                if 'rows' in visualJson1.keys():
                    if len(visualJson1.get('rows')) != 0: 
                        row = visualJson1["rows"]
                
                if 'columns' in visualJson1.keys():
                    if len(visualJson1.get('columns')) != 0:
                        self.colum = visualJson1["columns"]
                
                if 'values' in visualJson1.keys():
                    if len(visualJson1.get('values')) != 0:
                        self.val = visualJson1["values"]
                        
                if len(self.group) != 0:
                    lst=[]
                    for label, df_obj in (self.df).groupby(self.group):
                        sum = df_obj[self.val].sum()
                        df_obj.loc[' '] = sum   
                        lst.append(df_obj)

                    final_df = pd.concat(lst)
                    final_df.loc[final_df[row[0]].isnull(), self.group[0]] = "Total "  
                    final_df.loc[''] = self.df[self.val].sum()
                    final_df.fillna('', inplace=True)
                    final_df.iloc[-1, final_df.columns.get_loc(self.group[0])] = 'Grand Total '
                    self.group_style = True
                    html_str = self.getTableHTML(final_df)
                    logger.log(f'\n Print time on end : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                    return html_str
                    
                elif len(self.colum) == 0:
                    html_str = self.getTableHTML(self.df)
                    logger.log(f'\n Print time on end : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                    return html_str
                    
                else:
                    final_pivot = pd.pivot_table(self.df, index=row, columns=self.colum, values=self.val)
                    html_str = self.getTableHTML(final_pivot)
                    logger.log(f'\n Print time on end : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                    return html_str
                    
            elif self.outputType == "JSON":
                self.df = self.df.to_json(orient='records', date_format='iso')
                #logger.log(f'\n Print dataframe at end::: \n {self.df}', "0")
                data_set = {"dbDataTypesDetails": dbDataTypes, "allData":  self.df }
                logger.log(f'\n Print time on end : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                #return self.df
                #return data_set 
                return json.dumps(data_set)
            
            elif self.outputType == "XML":               
                xml_Str = self.to_xml(self.df)
                xmlStr = '<?xml version="1.0" encoding="UTF-8"?>\n<root>\n' + xml_Str + '\n</root>'
                logger.log(f'\n Print time on end : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                return xmlStr

            else:
                pass
                
        except Exception as e:
            logger.log(f'\n In getQueryData exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            if "Invalid column name" in descr :
                trace = "Column is not present in selected criteria, so please select specific column in criteria and then use in your calculation."
                returnErr = self.getErrorXml(descr, trace)
                logger.log(f'\n Print SQLResult exception  getQueryData : {returnErr}', "0")
                return str(returnErr)
            else:    
                returnErr = self.getErrorXml(descr, trace)
                logger.log(f'\n Print exception returnSring inside getQueryData : {returnErr}', "0")
                return str(returnErr)
        finally:
            try:
                if self.pool:
                    if self.dbDetails != None:
                        if self.dbDetails['DB_VENDORE'] == 'Oracle':
                            if self.isPool == 'true' :
                                self.pool.close()
                            else:
                                con.close()
                        else:
                            con.close()
            except Exception as e: 
                logger.log(f'\n In getQueryData exception stacktrace : ', "1")
                trace = traceback.format_exc()
                descr = str(e)
                returnErr = self.getErrorXml(descr, trace)
                logger.log(f'\n Print exception returnSring inside getQueryData : {returnErr}', "0")
                return str(returnErr)

    def getLookUpValue(self, row, pool):
        try:
            expr = self.detSql.split(',')
            lookUpTable = str(expr[0].strip())
            lookUpCol = expr[1].strip().lower()
            validateLookup = "false"
            isLookUpDateColValBlank = "false"
            lookupExpLen = len(expr)
            
            if lookupExpLen == 3:
                lookUpDateCol = expr[2].strip().lower()
                lookUpDateColVal = row[lookUpDateCol]
                validateLookup = "true"
                if str(lookUpDateColVal) == None or str(lookUpDateColVal) == '' or str(lookUpDateColVal) == 'NaT':
                    lookUpDateColVal = str('')
                    isLookUpDateColValBlank = "true"

            if lookUpTable != None and lookUpTable.startswith('\''):
                length = len(lookUpTable)
                lookUpTable = lookUpTable[1:length-1]
            else:
                lookUpTable = lookUpTable.lower()
                if  lookUpTable in row:
                    rowVal = row[lookUpTable]
                    lookUpTable = str(rowVal)
                else:
                    lookUpTable = ""
            
            rowVal = row[lookUpCol]

            isLookUpColValBlank = "false"
            if str(rowVal) == None or str(rowVal) == '' or str(rowVal) == 'NaT':
                rowVal = str('')
                isLookUpColValBlank = "true"

            if self.lookupTableMap == None or not ""+str(lookUpTable) in self.lookupTableMap:
                self.setLookUpData( lookUpTable, validateLookup, self.pool )

            if validateLookup == 'true':
                lookUpTable = lookUpTable + '_validate'

            dfLookUpDet = None
            resDataType = str('')
            isdfLookUpDet = "false"
            if self.lookupTableMap != None and ""+str(lookUpTable) in self.lookupTableMap:
                lookUpHeadDetMap = self.lookupTableMap[""+str(lookUpTable)]

                dfLookUpDet = lookUpHeadDetMap["lookUpDet"]

                resDataType = lookUpHeadDetMap["resDataType"]

                query = lookUpHeadDetMap["queryString"]
                if isLookUpDateColValBlank == "false" and isLookUpColValBlank == "false":
                    dfLookUpDet = dfLookUpDet.query( query )
                    isdfLookUpDet = "true"
                else:
                    isdfLookUpDet = "false"
            else:
                isdfLookUpDet = "false"

            if  isdfLookUpDet == "false" or dfLookUpDet.empty:
                if resDataType == 'N':
                    dfLookUpDet = 0
                    dfLookUpDet = pd.to_numeric(dfLookUpDet)
                elif resDataType == 'D':
                    dfLookUpDet = str('')
                    dfLookUpDet = pd.to_datetime(dfLookUpDet)
                elif resDataType == 'S':
                    dfLookUpDet = str('')
                else:
                    dfLookUpDet = str('')

            else:
                dfLookUpDet = dfLookUpDet.iloc[0:1,0:1]
                dfLookUpDet = dfLookUpDet.iat[0,0]

                if resDataType == 'N':
                    dfLookUpDet = pd.to_numeric(dfLookUpDet)
                elif resDataType == 'D':
                    dfLookUpDet = pd.to_datetime(dfLookUpDet)

            return dfLookUpDet
        except Exception as e:
            raise e

    def getSqlResult(self, row, pool, detail):
        try:
            if self.dbDetails != None:
                if self.dbDetails['DATABASETYPE'] == '1':
                    if self.isPool == 'true':
                        con = self.pool.acquire()
                    else:
                        con = self.pool
                elif self.dbDetails['DATABASETYPE'] == '2' or self.dbDetails['DATABASETYPE'] == '3' :
                    con = self.pool

            colDbType = detail['col_datatype']
            self.sqlQuery = self.detSql
            splitColValue = None
            dfSqlResult = None
            newSql = None

            if self.sqlQuery.find("?") != -1:
                newSql = self.sqlQuery.split(':')
                self.sqlQuery = newSql[0]
                sqlInput = newSql[1].lower()
                columns = sqlInput.split(',')
                self.buildSqlQuery(self.sqlQuery, columns, row)

            if 'update ' in self.sqlQuery or 'delete ' in self.sqlQuery:
                return self.getErrorXml("Invalid SQL" , "Update and Delete operations are not allowed in Visual.")
            else:
                logger.log(f"self.sqlQuery:: {self.sqlQuery}","0")
                dfSqlResult = pd.read_sql(
                    self.sqlQuery, con
                )

            if not dfSqlResult.empty:
                dfSqlResult = dfSqlResult.iloc[0:1,0:1]
                dfSqlResult = dfSqlResult.iat[0,0]
            else:
                if colDbType == 'N':
                    dfSqlResult = 0
                    dfSqlResult = pd.to_numeric(dfSqlResult)
                elif colDbType == 'D':
                    dfSqlResult = str('')
                    dfSqlResult = pd.to_datetime(dfSqlResult)
                else:
                    dfSqlResult = str('')
                    
            return dfSqlResult
        except Exception as e:
            raise e
        finally:
            try:
                if con:
                    if self.dbDetails != None:
                        if self.dbDetails['DATABASETYPE'] == '1':
                            if self.isPool == 'true' :
                                self.pool.release(con)
                        
            except Exception as e :
                logger.log(f'\n In getQueryData exception stacktrace : ', "1")
                trace = traceback.format_exc()
                descr = str(e)
                returnErr = self.getErrorXml(descr, trace)
                logger.log(f'\n Print exception returnSring inside getQueryData : {returnErr}', "0")
                return str(returnErr)

    def buildSqlQuery(self, sql, columns, row):
        ctr = 0
        rowVal = ""
        logger.log(f"\nsql:::{sql}  /ncolumns:::{columns}  /nrow:::{row} ","0")
        if sql.find('?') != -1 and len(columns) > 0:
            indexPos = sql.find('?')
            
            if columns[ctr].lower().startswith("criteria"):
                logger.log("inside criteria","0")
                criteriaColName = columns[ctr][columns[ctr].find('.')+1:]  # slice
                logger.log(f"criteriaColName:::{criteriaColName}","0")
                criteriaColName = criteriaColName.upper()
                logger.log(f"criteriaColName upper():::{criteriaColName}","0")
                logger.log(f"self.argumentList:::{self.argumentList}","0")
                
                if criteriaColName in self.argumentList.keys():
                    if self.argumentList.get(criteriaColName) != None:
                        rowVal = self.argumentList[criteriaColName]   
                else:
                    logger.log(f"inside buildSqlQuery else column not found ","0")
                    descr = "Invalid column name : " + criteriaColName
                    raise Exception(descr)
                    
                logger.log(f"rowVal:::{rowVal}","0")

            else:
                rowVal = str(row[columns[ctr].strip()])

            if str(rowVal) == None or str(rowVal) == 'None': 
                rowVal = str('')

            if len(sql) - 1 != indexPos:
                sql = sql[:indexPos] + "'" + rowVal + "'" + sql[indexPos+1:]
            else:
                sql = sql[:-1] + "'" + rowVal + "'"

            columns.pop(ctr)
            self.sqlQuery = str(sql)
            if(sql.find('?') != -1):
                self.buildSqlQuery(sql, columns, row)

    def getErrorXml(self, descr, trace, message=""):

        if  self.currentDetData:
            colName = self.currentDetData['col_name']
            calcType = self.currentDetData['calc_type']
            
            errorXml = '''<Root>
                            <Header>
                                <editFlag>null</editFlag>
                            </Header>
                            <Errors>
                                <error column_name="'''+colName+'''" type="E" column_value="'''+calcType+'''">
                                    <message><![CDATA[Error occurred in calculation of '''+colName+''' column for column type '''+calcType+''']]></message>
                                    <description><![CDATA['''+descr+''']]></description>
                                    <trace><![CDATA['''+trace+''']]></trace>
                                    <type>E</type>
                                    <errorId>'''+self.errorId+'''</errorId>
                                </error>
                            </Errors>
                        </Root>'''

            return errorXml
        else:
            errorXml = '''<Root>
                            <Header>
                                <editFlag>null</editFlag>
                            </Header>
                            <Errors>
                                <error type="E">
                                    <message><![CDATA['''+message+''']]></message>
                                    <description><![CDATA['''+descr+''']]></description>
                                    <trace><![CDATA['''+trace+''']]></trace>
                                    <type>E</type>
                                </error>
                            </Errors>
                        </Root>'''

            return errorXml

    def udf_divide(self, x, y):
        return x/y

    def udf_round(self, value, decimal):
        return round(value, decimal)

    def udf_if(self, df,condition,true_exp, false_exp):
        udf_divide = partial(self.udf_divide)
        udf_round = partial(self.udf_round)
        return np.where(df.eval(condition),df.eval(true_exp),df.eval(false_exp))

    def firstRowColVal(self, df):
        df = df.iloc[0:1,0:1]
        df = df.iat[0,0]
        return df
        
    def setLookUpData(self,lookUpTable,validateLookup, pool):
        try:
            if self.dbDetails != None:
                if self.dbDetails['DATABASETYPE'] == '1':
                    if self.isPool == 'true':
                        con = self.pool.acquire()
                    else:
                        con = self.pool
                elif self.dbDetails['DATABASETYPE'] == '2' or self.dbDetails['DATABASETYPE'] == '3' :
                    con = self.pool

            dfLookUpHead = None
            dfLookUpDet = None
            queryString = ''

            lookUpSql = "SELECT LOOKUP_TYPE, KEY_DATA_TYPE, RESULT_DATA_TYPE FROM GENLOOKUP WHERE LOOKUP_TABLE = '" + lookUpTable + "'"
            dfLookUpHead = pd.read_sql ( lookUpSql, con )

            lookUpDetSql = "SELECT RESULT_VALUE, MIN_KEY_VALUE, MAX_KEY_VALUE, EFF_FROM, VALID_UPTO FROM GENLOOKUP_TABLE WHERE LOOKUP_TABLE = '" + lookUpTable + "'"    
            dfLookUpDet = pd.read_sql( lookUpDetSql, con )

            rowVal = ''
            rowVal = str(rowVal)

            lookUpDateColVal = ''
            lookUpDateColVal = str(lookUpDateColVal)

            if not dfLookUpHead.empty and not dfLookUpDet.empty:
                resDataType = dfLookUpHead['RESULT_DATA_TYPE'].iloc[0]
                lookUpType = dfLookUpHead['LOOKUP_TYPE'].iloc[0]
                keyDataType = dfLookUpHead['KEY_DATA_TYPE'].iloc[0]

                if lookUpType == 'F':
                    if keyDataType == 'N':
                        dfLookUpDet[["MIN_KEY_VALUE", "MAX_KEY_VALUE"]] = dfLookUpDet[["MIN_KEY_VALUE", "MAX_KEY_VALUE"]].apply(pd.to_numeric)
                        rowVal = pd.to_numeric(rowVal)

                    elif keyDataType == 'D':
                        dfLookUpDet[["MIN_KEY_VALUE", "MAX_KEY_VALUE"]] = dfLookUpDet[["MIN_KEY_VALUE", "MAX_KEY_VALUE"]].apply(pd.to_datetime)
                        rowVal = pd.to_datetime(rowVal)

                    queryString = '@rowVal == MIN_KEY_VALUE'
                elif lookUpType == 'S':
                    if keyDataType == 'N':
                        dfLookUpDet[["MIN_KEY_VALUE", "MAX_KEY_VALUE"]] = dfLookUpDet[["MIN_KEY_VALUE", "MAX_KEY_VALUE"]].apply(pd.to_numeric)
                        rowVal = pd.to_numeric(rowVal)

                    elif keyDataType == 'D':
                        dfLookUpDet[["MIN_KEY_VALUE", "MAX_KEY_VALUE"]] = dfLookUpDet[["MIN_KEY_VALUE", "MAX_KEY_VALUE"]].apply(pd.to_datetime)
                        rowVal = pd.to_datetime(rowVal)

                if validateLookup == 'true':
                    dfLookUpDet[["EFF_FROM", "VALID_UPTO"]] = dfLookUpDet[["EFF_FROM", "VALID_UPTO"]].apply(pd.to_datetime)
                    lookUpDateColVal = pd.to_datetime(lookUpDateColVal)
                    if lookUpType == 'S':
                        queryString = '(@rowVal >= MIN_KEY_VALUE & @rowVal <= MAX_KEY_VALUE) & (@lookUpDateColVal >= EFF_FROM & @lookUpDateColVal <= VALID_UPTO)'
                    else:
                        queryString = '(@rowVal == MIN_KEY_VALUE) & (@lookUpDateColVal >= EFF_FROM & @lookUpDateColVal <= VALID_UPTO)'
                    lookUpTable = lookUpTable + '_validate'
                else:
                    if lookUpType == 'S':
                        queryString = '@rowVal >= MIN_KEY_VALUE & @rowVal <= MAX_KEY_VALUE'
                    else:
                        queryString = '@rowVal == MIN_KEY_VALUE'

                lookUpHeadDetMap = {}
                lookUpHeadDetMap["lookUpDet"] = dfLookUpDet
                lookUpHeadDetMap["resDataType"] = resDataType
                lookUpHeadDetMap["queryString"] = queryString
                self.lookupTableMap[lookUpTable] = lookUpHeadDetMap
        except Exception as e:
            raise e
        finally:
            if con:
                try:
                    if self.dbDetails != None:
                        if self.dbDetails['DATABASETYPE'] == '1':
                            if self.isPool == 'true' :
                                self.pool.release(con)
                        
                except Exception as e :
                    logger.log(f'\n In getQueryData exception stacktrace : ', "1")
                    trace = traceback.format_exc()
                    descr = str(e)
                    returnErr = self.getErrorXml(descr, trace)
                    logger.log(f'\n Print exception returnSring inside getQueryData : {returnErr}', "0")
                    return str(returnErr)

    def is_json(self,a):                                               
        try:
            json.loads(a)
        except Exception as e:
            return False
        return True

    def to_xml(self, dt_frame):
        def row_xml(row):
            xml = ['<Detail>']
            for i, col_name in enumerate(row.index):
                xml.append('  <{0}>{1}</{0}>'.format(col_name, row.iloc[i]))
            xml.append('</Detail>')
            return '\n'.join(xml)
        res = '\n'.join(dt_frame.apply(row_xml, axis=1))
        return(res)

    def format_num(self, str):
        return "text-align:right !important"

    def getTableHTML(self,pivot):
        if self.group_style :
            pivot_style = (pivot).reset_index(drop=True).style.applymap(self.format_num, subset=self.val).format('{:.3f}', na_rep='', subset=self.val)
            
        else:
            pivot_style = (pivot).style.applymap(self.format_num, subset=self.val).format('{:.3f}', na_rep='', subset=self.val)
        
        pivot_style = (pivot_style).set_table_attributes('class= "insight_html_table"')
        html = pivot_style.render()
        # logger.log(f'\n html inside method pivotstyle  : {type(html), html}', "0")                      

        col_dtype = dict(zip((self.calculationData['columnHeading']).split(','), json.loads(self.calculationData['columndataTypes']).values()))
        
        if self.advancedFormatting:
            for i in self.advancedFormatting.keys():
                if col_dtype[i] == 'string' :
                    pivot_style = pivot_style.set_properties(**{'background-color': self.advancedFormatting[i]}, subset=[i])
                else:
                    pivot_style = pivot_style.background_gradient(cmap=self.advancedFormatting[i], subset=[i])
                    
        html = "<h3 class='tableHeading'>"+ self.updateTableHeading(self.tableHeading, self.argumentList)+"</h3>" +  pivot_style.render()
        return html
    
    def store(self, df, userId, editorId, visualId, transpose):
        dir = 'Pickle_files'
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        filename= str(userId) +'_' + str(editorId) + '_' + str(visualId) + '_' + transpose
        df.to_pickle(dir + '/' + filename + '.pkl')
        if os.path.isfile(dir +'/' + filename + '.pkl'):
            logger.log('\n' + transpose + ' Pickle file created','0')   
        else:
            logger.log('\n' + transpose + ' Pickle file created','0')
        return dir +'/' + filename + '.pkl'
    
    def read(self, userId, editorId, visualId, transpose):
        dir = 'Pickle_files'
        if os.path.exists(dir):
            filename= str(userId) +'_' + str(editorId) + '_' + str(visualId) + '_' + transpose
            if os.path.isfile(dir +'/' + filename + '.pkl'):
                df_obj = pd.read_pickle(dir +'/' + filename + '.pkl')
                return df_obj
        else:
            return self.getErrorXml( dir + "directory does not exist","Pickle file directory not found" )  
    
    def replace(self, tableHeading, argumentList):
        left, right = tableHeading[:tableHeading.find("@")], tableHeading[tableHeading.find("@"):]
        key = right[:right.find(" ")]
        
        for i in argumentList.keys():
            if (key[1:]) in i:
                tableHeading = re.sub(key, argumentList[i], tableHeading) 
                break
        if "@" in tableHeading:
            tableHeading = self.replace(tableHeading, argumentList)
        
        return tableHeading

    def updateTableHeading(self, tableHeading, argumentList):    
        if "@" in tableHeading:
            tableHeading = self.replace(tableHeading, argumentList)
        else:
            return tableHeading

        return tableHeading
        
    def contribution(self, x):
        return (x / x.sum()) * 100

    def forecast(self):
        logger.log(f'\nForcast function start time, {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',"0")
        convert = json.loads(self.calculationData['columndataTypes'])
        length_of_string_col = 0
        string_list = []
        numeric_list_Int = []
        numeric_list = []
        length_of_dataset = 0
        
        for k in self.calculationData['column']:
            colname = k['col_name']
            expression1 = k['calc_expression']

        periodsof=expression1.split(",")
        per = periodsof[-1].split(")")
        global da
        for m,i in enumerate(convert):
            if convert[i] == 'string':
                string_list.append(i)
            elif convert[i] == 'date':
                da = i
                dateindex = m
            elif convert[i] == 'number':
                numeric_list.append(i)
                numeric_list_Int.append(m)
                pos=m
        
        for num, numbervalue in enumerate(convert):
                if numbervalue == numeric_list[0]:
                    for numbervalue in range(len(self.df)):
                        self.df.at[numbervalue, colname] = self.df[self.df.columns[num]].values[numbervalue]
        
        if len(string_list) != 0:
            new = self.df.filter([i for i in string_list], axis=1)
            drop_dataframe = new.drop_duplicates()    #### for drop duplicate value
            drop_dataframe.index = [i for i in range(0,len(drop_dataframe))]   ####   for contine index   
            for i in range(0,len(drop_dataframe)):
                datestring = []
                y = []
                head = []
                valuesofdataframe = [0]
                logger.log(f'\nForcast New DataFrame creation and finding the same data, start time : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',"0")
                newo =pd.DataFrame(drop_dataframe.iloc[[i]])
                newo.index=valuesofdataframe
                k=newo.values
                newdataframe = newo.copy()                                                                                                                                            
                newdataframe['marker'] = True
                joined = pd.merge(new, newdataframe, on=[i for i in new], how='left')
                val = joined[pd.notnull(joined['marker'])][new.columns]
                lis = []
                lis = val.index.tolist()
                logger.log(f'\nForcast New DataFrame creation and finding the same data, end time : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',"0")
                logger.log(f'\nForcast function process start time : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',"0")
                for ind in lis:
                    datestring.append(self.df[self.df.columns[dateindex]].values[ind])
                    y.append(self.df[self.df.columns[numeric_list_Int[0]]].values[ind])
                    length_of_dataset = length_of_dataset + 1

                if all(item == 0 for item in y) or len(y) < 2:
                    continue

                m = Prophet()
                df_for_prophet = pd.DataFrame(dict(ds=datestring, y=y))
                m.fit(df_for_prophet)
                future = m.make_future_dataframe(periods=int(per[0]))
                forecast = m.predict(future)
                logger.log(f'\nForcast function process End time : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',"0")
                for l, val in enumerate(forecast["trend"]):
                    df2 = {da: to_datetime([forecast["ds"][l]]), colname: [val]}
                    dd = pd.DataFrame(dict(df2))
                    df3 = pd.concat([newo, dd], axis=1)
                    df4 = df3[~df3[da].isin(datestring)]
                    self.df = self.df.append(df4, ignore_index = True)
                
            self.df.drop_duplicates(subset=da, keep='first', inplace=True)
            logger.log(f'\nForcast function end time :  {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',"0")
            return self.df

        elif len(string_list) == 0:
            ds = []
            y = []
            for num, numbervalue in enumerate(convert):
                if numbervalue == numeric_list[0]:
                    for numbervalue in range(len(self.df)):
                        pos = num
                        y.append(self.df[self.df.columns[num]].values[numbervalue])

            for num, datevalue in enumerate(convert):
                if convert[datevalue] == "date":
                    d = num
                    date = datevalue
                    for datevalue in range(len(self.df)):
                        ds.append(self.df[self.df.columns[num]].values[datevalue])

            logger.log(f'\nForcast function process start time : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',"0")
            dit = []
            m = Prophet()
            df_for_prophet = pd.DataFrame(dict(ds=ds, y=y))
            m.fit(df_for_prophet)
            future = m.make_future_dataframe(periods=int(per[0]))
            forecast = m.predict(future)
            logger.log(f'\nForcast function process End time : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',"0")
            for l, val in enumerate(forecast["trend"]):
                df2 = {da: forecast["ds"][l],colname: val}
                self.df = self.df.append(df2, ignore_index=True)

            logger.log(f'\nForcast function end time : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',"0")
            self.df  = self.df.drop_duplicates(subset=[da], keep='first', inplace=False, ignore_index=False)
            return self.df

    def trainemodel(self):
        try:
            flag =""
            input_column_name = ""
            train_column_name = ""
            modelType = ""
            logger.log(f"inside trainemodel()","0")
            jsonData = request.get_data('jsonData', None)
            jsonData = json.loads(jsonData[9:])
            logger.log(f"jsonData: {jsonData}{type(jsonData)}","0")

            modelType = jsonData['modelType'].lower().replace(" ","_")    # Added by SwapnilB for replacing folder name with "space" to "_"   
            jsonToDf = jsonData['modelJsonData']
            parsed_json = (json.loads(jsonToDf))
            df = pd.DataFrame(parsed_json[1:])
            
            modelParameter =json.loads(jsonData['modelParameter'])
            
            if "input_column_name" in modelParameter and modelParameter["input_column_name"] == None:
                input_column_name = modelParameter['input_column_name']

            if "train_column_name" in modelParameter and modelParameter["train_column_name"] == None:
                train_column_name = modelParameter['train_column_name']
                
            colNamesLst=[input_column_name, train_column_name]
            if 'model_name' not in modelParameter.keys() or modelParameter["model_name"] == None:
                if modelType != "product_identification":
                    modelName = modelType +"_training_model"  
                else:
                    modelName = "item_classification"  
            else:
                modelName = modelParameter['model_name'].lower().replace(" ","_")
            
            self.modelScope = "global" if jsonData['modelScope'] == "G" else "enterprise"   
            enterprise_key = jsonData['enterprise_key'].lower()     
            
            if modelType == 'sentiment_analytics':
                logger.log(f"Inside sentimentTraining model","0")      
                review_df = df[colNamesLst]
                review_df=review_df[review_df[colNamesLst[1]] != "neutral"]  
                review_df[colNamesLst[1]].value_counts()
                sentiment_label=review_df[colNamesLst[1]].factorize()  # creates vector Array
                tweet = review_df[colNamesLst[0]].values
                tokenizer = Tokenizer(num_words=5000)
                tokenizer.fit_on_texts(tweet)
                encoded_docs = tokenizer.texts_to_sequences(tweet)     
                padded_sequence = pad_sequences(encoded_docs, maxlen=200)
                vocab_size = len(tokenizer.word_index) + 1
                embedding_vector_length = 32
                model = Sequential()
                model.add(Embedding(vocab_size, embedding_vector_length, input_length=200))
                model.add(SpatialDropout1D(0.25))
                model.add(LSTM(50, dropout=0.5, recurrent_dropout=0.5))
                model.add(Dropout(0.2))
                model.add(Dense(1, activation='sigmoid'))
                model.compile(loss='binary_crossentropy',optimizer='adam', metrics=['accuracy'])
                model.fit(padded_sequence,sentiment_label[0], epochs=3, validation_split=0.2, batch_size=32)
            
            elif modelType == 'classification':
                review_df = df[colNamesLst]
                train_column_name=review_df[colNamesLst[1]]
                input_column_name = review_df[colNamesLst[0]]
                X_train, X_test, y_train, y_test = train_test_split(input_column_name, train_column_name, test_size=10,
                                                    random_state=10)
                svm = Pipeline([
                    ('vect', CountVectorizer()),
                    ('tfidf', TfidfTransformer()),
                    ('clf', LinearSVC()),
                ])
                svm.fit(X_train, y_train)
                logger.log(f'Model Created',"0")
            
            elif modelType == "intent_classification":
                review_df = df[colNamesLst]
                logger.log(f"colNamesLst::{colNamesLst}", "0")
                review_df.dropna(inplace=True)
                labels=review_df[colNamesLst[1]].factorize()  # creates 1-D Array
                commands=review_df.copy()
                commands[colNamesLst[1]]=labels[0]
                int_label = list(labels[0])
                str_label = list(labels[1])
                set_label=(set(int_label))
                predicted_label=dict(zip(set_label, str_label))
                logger.log(f"predicted_label::{predicted_label}","0")

                MAX_SEQUENCE_LENGTH = 50
                MAX_NUM_WORDS = 5000
                tokenizer = Tokenizer(num_words=MAX_NUM_WORDS)
                tokenizer.fit_on_texts(commands[colNamesLst[0]])
                sequences = tokenizer.texts_to_sequences(commands[colNamesLst[0]])
                word_index = tokenizer.word_index
                logger.log(f"Found {len(word_index)} unique tokens. ","0")
                data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
                labels = to_categorical(np.asarray(commands[colNamesLst[1]]))
                logger.log(f"Shape of data tensor: {data.shape}","0")
                logger.log(f"Shape of label tensor: {labels.shape}","0")

                VALIDATION_SPLIT = 0.1
                indices = np.arange(data.shape[0])
                np.random.shuffle(indices)
                data = data[indices]
                labels = labels[indices]
                num_validation_samples = int(VALIDATION_SPLIT * data.shape[0])
                x_train = data[:-num_validation_samples]
                y_train = labels[:-num_validation_samples]
                x_val = data[-num_validation_samples:]
                y_val = labels[-num_validation_samples:]

                EMBEDDING_DIM = 60
                num_words = min(MAX_NUM_WORDS, len(word_index) + 1)
                embedding_layer = Embedding(num_words,EMBEDDING_DIM,input_length=MAX_SEQUENCE_LENGTH,trainable=True)

                sequence_input = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')
                embedded_sequences = embedding_layer(sequence_input)
                x = Conv1D(64, 3, activation='relu')(embedded_sequences)
                x = Conv1D(64, 3, activation='relu')(x)
                x = MaxPooling1D(2)(x)
                x=Flatten()(x)
                x = Dense(100, activation='relu')(x)
                preds = Dense(y_train.shape[1], activation='softmax')(x)
                model = Model(sequence_input, preds)
                model.compile(loss='categorical_crossentropy',optimizer='rmsprop',metrics=['accuracy'])
                model.summary()

                for i in range (1,50):
                    model.fit(x_train, y_train,batch_size=50, epochs=3, validation_data=(x_val, y_val))
                scores = model.evaluate(x_val, y_val, verbose=0)
                logger.log(f"scores: {scores}","0")
            
            elif modelType == "product_identification":
                if "training_mode" in modelParameter or modelParameter["training_mode"] == None:
                    mode=modelParameter["training_mode"] # "init"
                parsed_json=parsed_json[1:]  # parsed_json[0] has datatypes of each column
                logger.log(f"parsed_json from index 1: {parsed_json}{type(parsed_json)}","0")
                modelType=modelType.lower()
                rasa = Rasa()
                result = rasa.create_model(enterprise_key, mode, parsed_json, self.modelScope, modelName, modelType, modelParameter)
                logger.log(f"rasa result : {result}","0")
                
            elif modelType == "pinecone_vector":
                logger.log(f'inside pinecone_vector condition',"0")
                result=""
                modelParameter["dfJson"] = jsonToDf
                pineConeVector =OpenAI_PineConeVector()
                result = pineConeVector.trainData(modelParameter)
                if result != "" and "Index Creation successful" in result:
                    flag = "success"
                    logger.log(f' pinecone_vector result genProcess() :::::: \n\t{result}',"0")
                else:
                    flag = "fail"

            else:
                logger.log(f'Invalid Model Type',"0")
                raise Exception(f"Ivalid Model Type:{modelType}")

        except Exception as e:
            logger.log(f'\n In Training model exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = self.getErrorXml(descr, trace)
            logger.log(f'\n Print exception returnSring inside Training model : {returnErr}', "0")
            raise str(e)
        else:
            
            modelPath = self.getTraineModelPath(modelType, modelName, self.modelScope, enterprise_key)
            logger.log(f"modelPath::{modelPath}","0")
            if modelType == 'sentiment_analytics':
                model.save(modelPath)     # to serialize model configuration and save model                  
                with open(modelPath +'/tokenizer.dictionary', 'wb') as tokenizer_dictionary_file:
                    pickle.dump(tokenizer, tokenizer_dictionary_file)
                    flag = "success"
                    logger.log("Sentiment Model has been trained and saved successfully.","0")
                    
            elif  modelType == 'classification':
                joblib.dump(svm, modelPath +'/' + modelName +'.pkl')
                flag = "success"
                logger.log("Classification Model has been trained and saved successfully.","0")
                
            elif modelType == "intent_classification":
                model.save(modelPath)     
                with open(modelPath +'/tokenizer.dictionary', 'wb') as tokenizer_dictionary_file:
                    pickle.dump(tokenizer, tokenizer_dictionary_file)
                with open(modelPath +'/label.dictionary', 'wb') as label_dictionary_file:
                    pickle.dump(predicted_label, label_dictionary_file)
                    flag = "success"
                    logger.log("Intent Model has been trained and saved successfully.","0")
            
            elif modelType == "product_identification":
                flag="success"

            elif modelType == "pinecone_vector":
                pass

            else:
                logger.log(f'Invalid Model Type',"0")
                raise Exception(f"Ivalid Model Type:{modelType}")

            if modelType != "pinecone_vector":
                result= self.createModelScope(self.modelScope, modelType, modelName, enterprise_key)
                logger.log(f"ModelScope result::{result}","0")
            
            if flag == "success":
                return modelType.upper() + " Model has been trained and saved successfully." 
            else:
                return modelType.upper() + " Model has failed to train."

    def predict(self, textColumn, modelName,  modelType, modelScope):
        logger.log(f"inside predict_sentiment","0")
        logger.log(f"textColum:{textColumn}, modelName:{modelName} ","0")

        modelType = modelType.lower().replace(" ","_")
        self.modelScope = modelScope
        enterprise=""
        predicted_Sentiment=None
        predicted_label_lst=[]
                
        if 'enterprise' in self.calculationData.keys():
            if self.calculationData.get('enterprise') != None:
                enterprise = self.calculationData['enterprise']

        logger.log(f"modelScope 1165::{self.modelScope}", "0")
        logger.log(f"enterprise 1170::{enterprise}", "0")
        modelPath = self.getTraineModelPath(modelType, modelName, self.modelScope, enterprise)

        if modelType == "sentiment_analytics":
            with open(modelPath +'/tokenizer.dictionary', 'rb') as config_dictionary_file:
                tokenizer = pickle.load(config_dictionary_file)
                logger.log(f"tokenizer:::{tokenizer} {type(tokenizer)}","0")
            logger.log(f"self.df::::{self.df}\n{self.df.shape}","0")
            logger.log(f'\nSentiment prediction start time : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',"0")
            loaded_Model = keras.models.load_model(modelPath)   #("models/"+ modelName)
            for i,j in textColumn.iteritems():
                tw = tokenizer.texts_to_sequences([j])
                tw = pad_sequences(tw, maxlen=200)
                prediction = int(loaded_Model.predict(tw).round().item())
                predicted_label = "Positive" if prediction==0 else "Negative" 
                # logger.log(f"\n\n{j}\n\n Predicted label::::: {predicted_label}","0")
                predicted_label_lst.append(predicted_label)
            
            logger.log(f'\nSentiment prediction end time : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',"0")
            predicted_Sentiment = pd.DataFrame(predicted_label_lst, columns=['predicted_sentiment'])
        
        elif modelType == "classification":
            iterater = []
            predictmodel = joblib.load(modelPath +"/" +modelName+".pkl")
            logger.log(f"predictmodel : {predictmodel}","0")
            return predictmodel.predict(textColumn)
        
        elif modelType == "intent_classification":
            with open(modelPath +'/tokenizer.dictionary', 'rb') as config_dictionary_file:
                tokenizer = pickle.load(config_dictionary_file)
                logger.log(f"tokenizer:{tokenizer}, {type(tokenizer)}","0")
            with open(modelPath +'/label.dictionary', 'rb') as label_dictionary_file:
                predicted_label = pickle.load(label_dictionary_file)
            loaded_Model = keras.models.load_model(modelPath )  #+ modelName)
            sequences_new = tokenizer.texts_to_sequences(textColumn)
            data = pad_sequences(sequences_new, maxlen=50)
            yprob = loaded_Model.predict(data)
            yclasses=yprob.argmax(axis=-1)
            logger.log(f"yclasses{yclasses}","0")
            res=[predicted_label[i] for i in yclasses]
            logger.log(f"res:{res}","0")
            predicted_Sentiment = pd.DataFrame(res, columns=['predicted_intent'])

        else:
            raise Exception(f"Invalid model name : '{modelType}'")
        logger.log(f'\npredicted_Sentiment : {predicted_Sentiment}{type(predicted_Sentiment)}',"0")
        return predicted_Sentiment

    def translate(self,colname_value,translate_to=None):
        logger.log(f'\n Print time for before executing Translate function : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
        da = Translator()
        ls=[]
        for i in colname_value:
            if i != None:
                logger.log(f'\n Print time for before executing Translate OPERATION : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                ls.append((da.translate(i,dest=translate_to)).text)
                logger.log(f'\n Print time for after executing Translate OPERATION : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")          
            else:
                ls.append("")
                
        logger.log(f'\n Print time for after executing Translate function : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")          
        return ls

    def createModelScope(self, modelScope, modelType, modelName,enterprise_key=""):
        path = "/proteus-sense/trained_model"
        fileName = "modelScope.json"
        filePath = path + "/" + fileName
        if os.path.exists(filePath):
            logger.log(f"File already exists.","0")
        else:
            if not os.path.exists(path):
                os.makedirs(path)   
            with open (filePath,"w") as file:
                fileData={}
                fileData=str(fileData).replace("'", '"')
                logger.log(f"after{str(fileData)}","0")
                file.write(fileData)
                file.close()
                if os.path.exists(filePath):
                    logger.log(f"File created","0")

        with open (filePath,"r") as file:
            FilejsonData = file.read()
            file.close()
            logger.log(f"FilejsonData::{FilejsonData},{type(FilejsonData)}","0")

            modelScopefileJson=json.loads(FilejsonData)
            logger.log(f"parsedJsonData::{modelScopefileJson},{type(modelScopefileJson)}","0")
        
        if modelScope == "global":
            if modelType in modelScopefileJson:
                if modelScope in modelScopefileJson[modelType]:
                    if modelName not in modelScopefileJson[modelType][modelScope]:
                        modelScopefileJson[modelType][modelScope].append(modelName)
                    else:
                        logger.log(f"ModelName exists","0")
                    logger.log(f"if::{modelScopefileJson}","0")

                else:
                    modelScopefileJson[modelType][modelScope] = [modelName]
            else:
                modelScopefileJson[modelType] = {modelScope :[modelName]}
        
        elif modelScope == "enterprise":
            if modelType in modelScopefileJson:
                if modelScope in modelScopefileJson[modelType]:
                    if enterprise_key not in modelScopefileJson[modelType][modelScope]:
                        modelScopefileJson[modelType][modelScope][enterprise_key]=[modelName]
                    else:    
                        if not modelName in modelScopefileJson[modelType][modelScope][enterprise_key]:
                            modelScopefileJson[modelType][modelScope][enterprise_key].append(modelName)
                        else:
                            logger.log(f"ModelName exists","0")
                else:
                    modelScopefileJson[modelType][modelScope] = {enterprise_key:[modelName]}
            else:
                modelScopefileJson[modelType] = {modelScope: {enterprise_key:[modelName]}}
        else:
            logger.log(f"Invalid modelScope received:: {modelScope}","0")
        
        logger.log(f"data: {modelScopefileJson}","0")

        with open (filePath,"w") as file:
            logger.log(f"modelScopefileJson in write mode;::: {modelScopefileJson}","0")    
            modelScopefileJson=str(modelScopefileJson).replace("'", '"')
            logger.log(f"after line 1198 :: {str(modelScopefileJson)}","0")
            file.write(modelScopefileJson)
            file.close()
            logger.log(f"File updated","0")
        
        return "File Updated successfully "
    
    def getTraineModelPath(self, modelType, modelName, modelScope, enterprise_key=""):
        modelPath=""
        logger.log("inside getTraineModelPath","0")
        logger.log(f"modelScope 1297::{modelScope}", "0")
        modelScope =  "global" if modelScope=="G" or modelScope=="global" or modelScope=="g" else "enterprise"
        logger.log(f"modelScope 1299::{modelScope}", "0")
        if modelScope=="global":
            logger.log("inside getTraineModelPath if","0")
            modelPath = "/proteus-sense/trained_model/" + modelType.lower() + "/" + modelScope.lower() +  "/"+ modelName.lower()
        else:
            logger.log("inside getTraineModelPath else ","0")
            modelPath = "/proteus-sense/trained_model/" +  modelType.lower()  + "/" + modelScope.lower() + "/" + enterprise_key.lower() +  "/"+ modelName.lower()
        if not os.path.exists(modelPath):
            os.makedirs(modelPath)
            logger.log(f"inside getTraineModelPath modelPath::{modelPath}","0")
        return modelPath
        
    def getModelScopeList(self):
        try:
            enterprise=""
            listreturn = {}
            modelScopeList=[]
            descr=""
            filePath="/proteus-sense/trained_model/modelScope.json"
            jsonData = (request.get_data('jsonData', None)).decode("utf-8")[9:]
            logger.log(f"jsonData::{jsonData}{type(jsonData)}","0")
            jsonData = json.loads(jsonData)
            modelType = jsonData["function_name"].lower().replace(" ","_")
            modelScope = "global" if jsonData["model_scope"]=="G" else "enterprise"
            
            if 'enterprise' in jsonData.keys():
                if jsonData['enterprise'] != None and jsonData['enterprise'] != "":
                    enterprise = jsonData['enterprise'].lower()
                    logger.log(f"enterprise::{enterprise}{type(enterprise)}","0")

            if os.path.exists(filePath) and len(open(filePath).read())!=0 :
                with open(filePath, "r") as file:
                    fileData = json.loads(file.read())
                    if modelType in fileData.keys():
                        if modelScope == "global":
                            if modelScope in fileData[modelType]:
                                modelScopeList = fileData[modelType][modelScope]
                            else:
                                descr = f'''For the model scope {modelScope.title()} and model type {modelType.title().replace("_"," ")} there is no trained model found.'''
                        else:
                            if modelScope in fileData[modelType]:
                                if enterprise in fileData[modelType][modelScope]:
                                    modelScopeList = fileData[modelType][modelScope][enterprise]
                                else:
                                    descr = f'''For the model scope {modelScope.title()} and  and model type {modelType.title().replace("_"," ")} there is no trained model found.'''
                            else:
                                descr = f'''For the model scope {modelScope.title()} and model type {modelType.title().replace("_"," ")} there is no trained model found.'''
                    else:
                        descr = f'''For the model scope {modelScope.title()} and model type {modelType.title().replace("_"," ")} there is no trained model found.'''
                        
                    logger.log(f"\nmodelScopeList::{modelScopeList}{type(modelScopeList)}","0")
                    listreturn['modelname'] = modelScopeList
                    logger.log(f"\nlistreturn::{listreturn}{type(listreturn)}","0")
            else:
                descr = f'''For the model scope {modelScope.title()} and model type {modelType.title().replace("_"," ")} there is no trained model found.'''    
            if descr != "":
                returnErr = self.getErrorXml(descr, "ERROR")
                return returnErr 
            else:
                return json.dumps(listreturn)
                
        except Exception as e:
            logger.log(f"Exception in getModelScopeAPI:: {e}","0")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = self.getErrorXml(descr, trace)
            logger.log(f'\n Print exception returnSring inside getModelScopeAPI : {returnErr}', "0")
            return str(returnErr)
            

    def removeOperator(self, argumentList):
        with_OperatorLst=[]
        without_OperatorLst=[]
        without_Operator = ""
        
        with_OperatorLst = [key[:(key.rfind("_")+1)] for key in argumentList.keys()]
        logger.log(f"with_OperatorLst:: {with_OperatorLst}", "0")
        for i in range(len(with_OperatorLst)):
            if "_like_" in with_OperatorLst[i]:
                logger.log(f"inside _like_ :: {with_OperatorLst[i]}", "0")
                without_Operator = with_OperatorLst[i].replace("_like_","")
            
            elif "_between_" in with_OperatorLst[i]:
                logger.log(f"inside _between_ :: {with_OperatorLst[i]}","0")
                without_Operator = with_OperatorLst[i].replace("_between_","")
            
            elif "_in_" in with_OperatorLst[i]:
                logger.log(f"inside _in_ :: {with_OperatorLst[i]}","0")
                without_Operator = with_OperatorLst[i].replace("_in_","")
            
            elif "!=_" in with_OperatorLst[i]:
                logger.log(f"inside !=_ :: {with_OperatorLst[i]}","0")
                without_Operator = with_OperatorLst[i].replace("!=_","")
            
            elif ">_" in with_OperatorLst[i]:
                logger.log(f"inside >_ :: {with_OperatorLst[i]}","0")
                without_Operator = with_OperatorLst[i].replace(">_","")
            
            elif ">=_" in with_OperatorLst[i]:
                logger.log(f"inside >=_ :: {with_OperatorLst[i]}","0")
                without_Operator = with_OperatorLst[i].replace(">=_","")
            
            elif "<_" in with_OperatorLst[i]:
                logger.log(f"inside >=_ :: {with_OperatorLst[i]}","0")
                without_Operator = with_OperatorLst[i].replace("<_","")
            
            elif "<=_" in with_OperatorLst[i]:
                logger.log(f"inside >=_ :: {with_OperatorLst[i]}","0")
                without_Operator = with_OperatorLst[i].replace("<=_","")
            
            elif "=_" in with_OperatorLst[i]:
                logger.log(f"inside >=_ :: {with_OperatorLst[i]}","0")
                without_Operator = with_OperatorLst[i].replace("=_","")
            
            without_OperatorLst.append(without_Operator)
        
        logger.log(f"without_OperatorLst:: {without_OperatorLst}","0")
        
        final_argumentList = dict(zip(without_OperatorLst, list(argumentList.values())))
        logger.log(f"\nargumentList:: {argumentList} \n\nfinal_argumentList:: {final_argumentList}","0")
        return final_argumentList       
    


    


    
