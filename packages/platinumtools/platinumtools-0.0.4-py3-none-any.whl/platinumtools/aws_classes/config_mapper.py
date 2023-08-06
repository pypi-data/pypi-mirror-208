
import pandas as pd

from dda_constants import Employee, IncomingData, DateParser, sqlDTypes, EDetermination
from dda_constants import RECIPIENT_NUMBER_ROW, SOURCEID_ROW, DATE_LOCAL_ROW, DATEUTC_ROW, MONTH_ROW, MONTHNAME_ROW, WEEKDAY_ROW, WEEKDAYNAME_ROW, DAYS_ROW, HOUR_ROW, MINUTES_ROW, DATE_ROW, TIMESLOT_ROW, OPERATION_ROW, APPLICATION_ROW, APPLICATIONTYPE_ROW, EVENTYPE_ROW, RECORD_NUMBER_ROW


# This should be enhancer instead. The idea that every enhancement just has different log settings available for it.

class ConfigMapper:

    def __init__(self, configDict: dict, bucketDict: dict, incomingData: IncomingData = IncomingData() ):
        
        
        self.configDict = configDict
        self.bucketDict = bucketDict
        self.incomingData = incomingData

        self.mappedDict = {} # To be populated with the mapped dict
        self.constants = {}
        self.mappedDF = pd.DataFrame()
        self.bucketMapper = {}
        self.createMappingDict()
        self.employee_table = pd.DataFrame() #Employee Dataframe to extract information from. 
        
        
        
        self.addToConstants(incomingData.getPropsAsDict(), table_pre=incomingData.table_name)

    def addToConstants(self, dictData: dict, table_pre: str) -> None:
        """
        Used to avoid duplication of columns by having the `tablenname_columnkey`
        """


        for key in dictData.keys():
            # print("Adding to constants: ", key, dictData[key]) #Answers if it is still an array here, or nut.
            self.constants[table_pre + "_" + key] = dictData[key]

    def useEmployeeTableMapDF(self):
        """
        Joins the employee table with 
        """

        self.mappedDF = self.mappedDF.merge(self.employee_table, left_on="UserId", right_on="employee_id_365", how="left")
        
        
                
    def dfEnhancement(self):
        
        print("DF Enhancement activated using: ", self.mappedDF.columns )
        DATEFIELDS_TOPARSE = [MONTH_ROW, MONTHNAME_ROW, WEEKDAY_ROW, WEEKDAYNAME_ROW, DAYS_ROW , HOUR_ROW, MINUTES_ROW ,DATE_ROW, DATE_LOCAL_ROW, TIMESLOT_ROW]

        
        def datetimePopulation(dfRow)->str:
            date = dfRow["creation_time"]
            dt = DateParser(date, set_timezone=dfRow["employee_timezone"], slot_splits=dfRow["employee_time_slot_split"])
            return dt.getValuesAsList(DATEFIELDS_TOPARSE)

        def classifyEventType(dfRow)->str:
            """
            Takes an individual DF Row and produces the proper response
            """
            hours_start = "employee_work_hours_start"
            hours_end = "employee_work_hours_end"
            
            weekday = int(dfRow[WEEKDAY_ROW])
            if(dfRow[WEEKDAY_ROW] not in dfRow["employee_work_days"]):
                return EDetermination.WEEKENDS.value

            # 
            elif(dfRow[DATE_ROW] in self.employeeData.escape_dates):
                return EDetermination.DAYOFF.value

            # If the time is earlier or later than the regular workday, then this is marked as afterhours
            elif not (dfRow[hours_start][weekday] == 0 and dfRow[hours_end][weekday] == 0):
                if(dfRow[HOUR_ROW] < dfRow[hours_start][weekday] or dfRow[HOUR_ROW] > dfRow[hours_end][weekday]):
                    return EDetermination.AFTERHOURS.value
            

            return EDetermination.WORKHOURS.value # For now just return the date to prove that successfullmapping can be done.

        for operationKey in self.configDict.keys():
            
            if operationKey == "map":
                for functionName in self.configDict[operationKey].keys():
                    toReplaceRow = self.configDict[operationKey][functionName]
                    self.mappedDF[functionName] = self.mappedDF[toReplaceRow]

            if operationKey == "bucket":
                for functionName in self.configDict[operationKey].keys():
                    
                    toReplaceRow = self.configDict[operationKey][functionName]
                    print("Looping for function bucket key: ", functionName)
                    if functionName == OPERATION_ROW:
                        # di = {1: "A", 2: "B", "MipLabel": "Admin"}
                        di = self.bucketDict[OPERATION_ROW]["buckets"]
                        self.mappedDF[functionName] = self.mappedDF[toReplaceRow].replace(di)

                    if functionName == APPLICATIONTYPE_ROW:
                        di = self.bucketDict[APPLICATIONTYPE_ROW]["buckets"]
                        print("Application Mapping for: ", APPLICATIONTYPE_ROW , "Using",  APPLICATION_ROW, di)
                        self.mappedDF[functionName] = self.mappedDF[toReplaceRow].replace(di)
                    

            if operationKey == "functions":
                for functionName in self.configDict[operationKey].keys():
                    # print("Operation Running:", functionName)
                    if functionName == DATE_LOCAL_ROW:
                        zipResults = zip(*self.mappedDF.apply(datetimePopulation, axis=1))
                        self.mappedDF[MONTH_ROW], self.mappedDF[MONTHNAME_ROW], self.mappedDF[WEEKDAY_ROW], self.mappedDF[WEEKDAYNAME_ROW], self.mappedDF[DAYS_ROW], self.mappedDF[HOUR_ROW], self.mappedDF[MINUTES_ROW],  self.mappedDF[DATE_ROW], self.mappedDF[DATE_LOCAL_ROW], self.mappedDF[TIMESLOT_ROW] = zipResults
                    elif functionName == EVENTYPE_ROW:
                        self.mappedDF[EVENTYPE_ROW] = self.mappedDF.apply(classifyEventType, axis=1)
                    
    
    def getNested(self, df, stringToParse):
        return self.getNestedAssistant(df, stringToParse.split("/"))

    def getNestedAssistant(self, parentObj, propertyToGet):

        if len(propertyToGet) <= 1:
            try:
                return getattr(parentObj, propertyToGet[0])
            except:
                print("Unsuccessfull at attempting to get Last", propertyToGet[0])
                return self.mappedDict["null"]
        else:
            try:
                parentObj = getattr(parentObj, propertyToGet[0])
            except:
                print("Unsuccessfull at attempting to get Parent", propertyToGet[0])
                return self.mappedDict["null"]
            return self.getNestedAssistant(parentObj, propertyToGet[1:])

    def createMappingDict(self):
        """
        Initializes everything as a dictionary to later use for mapping
        From:
        {a: [x, y, z]} => {x: a, y: a, z: a}
        """
        # Loop for each bucketSetting, and each nested key to create the dictionary
        for bucketType in self.bucketDict.keys():
            targetBucket = self.bucketDict[bucketType]["buckets"]
            self.bucketMapper[bucketType] = {}
            for mapValue in targetBucket.keys():
                for mapKey in targetBucket[mapValue]:
                    self.bucketMapper[bucketType][mapKey] = mapValue
