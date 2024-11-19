# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 13:24:04 2022

@author: Matthew Gooda
"""

# TODO: remove hard coded elements from payload and BoMToCSV function.
#       read input file containing list of sites to query
#       

import requests
import xml.dom.minidom
import csv 
# import os
import sys, time
import datetime


# Set proxy environment variables to try to prevent 407 error when "default"
# system proxy http://web-prdproxy-usr.dmz:80 is used.
http_proxy = "http://web-espproxy-usr.dmz:80"
https_proxy = "http://web-espproxy-usr.dmz:80"

# os.environ["http_proxy"] = "http://web-espproxy-usr.dmz:80"
# os.environ["https_proxy"] = "http://web-espproxy-usr.dmz:80"

proxies = { 
              "http"  : http_proxy, 
              "https" : https_proxy
            }


#==============================================================================
# Create a csv file to store the SunWater flow or storage data
# Args: SunWaterSiteSeries -> single XML element of om:result
#       seriesName -> string to identify multiple series from a site
#       siteName -> string of gauging station identifier

def BoMToCSV(SunWaterSiteSeries, seriesName, siteName, dataType):
    # TODO: set output filename to gauging station name. Perhaps include data type, units, etc in name too. DONE
    #       check that output file doesn't already exist
    #       convert cumecs to ML/d DONE
    
    if dataType == "Water Course Discharge":
        dataHeading = "flow (ML/d)"
    elif dataType == "Storage Volume":
        dataHeading = "volume (ML)"
    elif dataType == "Storage Level":
        dataHeading = "level (m)"
        
    with open(siteName + '_' + seriesName + '_' + dataType.rsplit(' ', 1)[1] + '.csv', 'w') as file:
        # set a list of lines to add:
        addheaders = [" ", " ", " "]
        # write to file and add a separator
        file.writelines(s + '\n' for s in addheaders)
        file.close()
    
    csvfile = open(siteName + '_' + seriesName + '_' + dataType.rsplit(' ', 1)[1] + '.csv', 'a')
    fieldnames = ['date', dataHeading, 'quality code']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
  
    allData = SunWaterSiteSeries.getElementsByTagName("wml2:point")
    # print(streamflow.length)
    
    # Get default Quality Code if one exists
    if SunWaterSiteSeries.getElementsByTagName("wml2:defaultPointMetadata")[0].getElementsByTagName("wml2:qualifier"):
        defaultQC = SunWaterSiteSeries.getElementsByTagName("wml2:defaultPointMetadata")[0].getElementsByTagName("wml2:qualifier")[0].getAttribute("xlink:title")
    else:
        defaultQC = "0"
    
    if dataType == "Water Course Discharge":
        for thisData in allData:
            # try:
                thisDate = thisData.getElementsByTagName("wml2:time")[0].firstChild.nodeValue
                if thisData.getElementsByTagName("wml2:value")[0].getAttribute("xsi:nil") == "true":
                    # print("xsi:nil found " + thisDate)
                    thisFlow = "0"
                else:
                    # print("xsi:nil not found " + thisDate)
                    thisFlow = round(float(thisData.getElementsByTagName("wml2:value")[0].firstChild.nodeValue) * 86.4, 1)
                
                # assign quality code if one exists, otherwise check for default QC to all records and assign that.
                if thisData.getElementsByTagName("wml2:qualifier"):
                    thisQual = thisData.getElementsByTagName("wml2:qualifier")[0].getAttribute("xlink:title")
                else:
                    thisQual = defaultQC
                
                
                writer.writerow({'date': datetime.datetime.strptime(thisDate, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d/%m/%Y"), dataHeading: thisFlow, 'quality code': thisQual})
            # except (AttributeError):
                # print("There is an unexpected value or missing data at this date: " + thisDate)
                # print(AttributeError)
                # break
    elif dataType == "Storage Volume":
        for thisData in allData:
            # try:
                thisDate = thisData.getElementsByTagName("wml2:time")[0].firstChild.nodeValue
                niceDate = datetime.datetime.strptime(thisDate, "%Y-%m-%dT%H:%M:%S.%f%z")
                if niceDate.strftime("%H") == "09":
                    if thisData.getElementsByTagName("wml2:value")[0].getAttribute("xsi:nil") == "true":
                        # print("xsi:nil found " + thisDate)
                        thisFlow = "0"
                    else:
                        # print("xsi:nil not found " + thisDate)
                        thisFlow = round(float(thisData.getElementsByTagName("wml2:value")[0].firstChild.nodeValue), 1)
                    
                    # assign quality code if one exists, otherwise check for default QC to all records and assign that.
                    if thisData.getElementsByTagName("wml2:qualifier"):
                        thisQual = thisData.getElementsByTagName("wml2:qualifier")[0].getAttribute("xlink:title")
                    else:
                        thisQual = defaultQC
                                        
                    writer.writerow({'date': niceDate.strftime("%d/%m/%Y"), dataHeading: thisFlow, 'quality code': thisQual})
                
            # except (AttributeError):
                # print("There is an unexpected value or missing data at this date: " + thisDate)
                # print(AttributeError)
                # break
    elif dataType == "Storage Level":
        for thisData in allData:
            # try:
                thisDate = thisData.getElementsByTagName("wml2:time")[0].firstChild.nodeValue
                niceDate = datetime.datetime.strptime(thisDate, "%Y-%m-%dT%H:%M:%S.%f%z")
                if niceDate.strftime("%H") == "09":
                    if thisData.getElementsByTagName("wml2:value")[0].getAttribute("xsi:nil") == "true":
                        # print("xsi:nil found " + thisDate)
                        thisFlow = "0"
                    else:
                        # print("xsi:nil not found " + thisDate)
                        thisFlow = round(float(thisData.getElementsByTagName("wml2:value")[0].firstChild.nodeValue), 3)
                    
                    # assign quality code if one exists, otherwise check for default QC to all records and assign that.
                    if thisData.getElementsByTagName("wml2:qualifier"):
                        thisQual = thisData.getElementsByTagName("wml2:qualifier")[0].getAttribute("xlink:title")
                    else:
                        thisQual = defaultQC
                                        
                    writer.writerow({'date': niceDate.strftime("%d/%m/%Y"), dataHeading: thisFlow, 'quality code': thisQual})
                
            # except (AttributeError):
                # print("There is an unexpected value or missing data at this date: " + thisDate)
                # print(AttributeError)
                # break
    csvfile.close()
# end def BomToCSV
#==============================================================================


#==============================================================================
# Query BoM Water Data web service to retrieve water course discharge and
# storage volume data for SunWater gauging stations.

def getBoMWaterData(stationID):
    # SOAP request URL
    # This is the web address of the BoM waterdata service.
    url = "http://www.bom.gov.au/waterdata/services?service=SOS&version=2.0&request=GetCapabilities"
    
    # headers to attach to request
    headers = {
        'Content-Type': 'text/xml; charset=utf-8'
    }
    
    for obsProperty in ["Storage Volume", "Storage Level", "Water Course Discharge"]:
        
        if obsProperty == "Storage Volume":
            proc = "Pat6_C_B_1_HourlyMean"
        elif obsProperty == "Storage Level":
            proc = "Pat7_C_B_1_HourlyMean"
        elif obsProperty == "Water Course Discharge":
            proc = "Pat4_C_B_1_DailyMean09"
            
        # print(obsProperty)
        # print(proc)
    
        # Check for availability of data. 
        checkDataPayload = """<?xml version="1.0" encoding="UTF-8"?>
                                    <soap12:Envelope
                                    xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"
                                    xmlns:sos="http://www.opengis.net/sos/2.0"
                                    xmlns:wsa="http://www.w3.org/2005/08/addressing"
                                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                    xmlns:ows="http://www.opengis.net/ows/1.1"
                                    xmlns:fes="http://www.opengis.net/fes/2.0"
                                    xmlns:gml="http://www.opengis.net/gml/3.2"
                                    xmlns:swes="http://www.opengis.net/swes/2.0"
                                    xsi:schemaLocation="http://www.w3.org/2003/05/soap-envelope http://www.w3.org/2003/05/soap-envelope/soap-envelope.xsd
                                    http://www.opengis.net/sos/2.0 http://schemas.opengis.net/sos/2.0/sos.xsd">
                                    <soap12:Header>
                                    <wsa:To>http://www.ogc.org/SOS</wsa:To>
                                    <wsa:Action>http://www.opengis.net/def/serviceOperation/sos/foiRetrieval/2.0/GetFeatureOfInterest</wsa:Action>
                                    <wsa:ReplyTo>
                                    <wsa:Address>http://www.w3.org/2005/08/addressing/anonymous</wsa:Address>
                                    </wsa:ReplyTo>
                                    <wsa:MessageID>0</wsa:MessageID>
                                    </soap12:Header>
                                    <soap12:Body>
                                    <sos:GetFeatureOfInterest service="SOS" version="2.0.0">
                                    <sos:procedure>http://bom.gov.au/waterdata/services/tstypes/""" + proc + """</sos:procedure>
                                    <sos:observedProperty>http://bom.gov.au/waterdata/services/parameters/""" + obsProperty + """</sos:observedProperty>
                                    <sos:featureOfInterest>http://bom.gov.au/waterdata/services/stations/""" + stationID + """</sos:featureOfInterest>
                                    </sos:GetFeatureOfInterest>
                                    </soap12:Body>
                                    </soap12:Envelope>"""
        
        # print(checkDataPayload)
        
        
        checkDataResponse = requests.request("POST", url, headers=headers, data=checkDataPayload, proxies=proxies)
        print("checkDataResponse: " + str(checkDataResponse.status_code))
        
        countTries = 1
        
        while checkDataResponse.status_code != 200:
            countTries += 1
            time.sleep(3)
            checkDataResponse = requests.request("POST", url, headers=headers, data=checkDataPayload, proxies=proxies)
            if countTries >= 20:
                print("Unable to get successful response from BoM web service after 20 retries.")
                sys.exit()
        
        print("Number of attempts needed to check data availability: " + str(countTries))
        # print("checkDataResponse: " + str(checkDataResponse.status_code))
        
        tempXML = xml.dom.minidom.parseString(checkDataResponse.text)
        # tempPrettyXML = tempXML.toprettyxml()
        
        # print("tempPrettyXML" + tempPrettyXML)
        
        # If data exists, request it.
        if tempXML.getElementsByTagName("sos:featureMember"):
            # print("Response contains sos:featureMember data for " + obsProperty)
            
            
            # This request is for daily mean streamflow in cumecs from 9am to 9am or storage volume and level.
            # The featureOfInterest element defines which station to query.
            # TODO: replace the hard coded station identifier 130110A in the feature of interest element of the payload DONE
            requestData = """<soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope" xmlns:sos="http://www.opengis.net/sos/2.0" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:fes="http://www.opengis.net/fes/2.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:swes="http://www.opengis.net/swes/2.0" xsi:schemaLocation="http://www.w3.org/2003/05/soap-envelope http://www.w3.org/2003/05/soap-envelope/soap-envelope.xsd http://www.opengis.net/sos/2.0 http://schemas.opengis.net/sos/2.0/sos.xsd">
                            <soap12:Header>
                            <wsa:To>http://www.ogc.org/SOS</wsa:To>
                            <wsa:Action>http://www.opengis.net/def/serviceOperation/sos/core/2.0/GetObservation</wsa:Action>
                            <wsa:ReplyTo>
                            <wsa:Address>http://www.w3.org/2005/08/addressing/anonymous</wsa:Address>
                            </wsa:ReplyTo>
                            <wsa:MessageID>0</wsa:MessageID>
                            </soap12:Header>
                            <soap12:Body>
                            <sos:GetObservation service="SOS" version="2.0.0">
                            <sos:procedure>http://bom.gov.au/waterdata/services/tstypes/""" + proc + """</sos:procedure>
                            <sos:observedProperty>http://bom.gov.au/waterdata/services/parameters/""" + obsProperty + """</sos:observedProperty>
                            <sos:featureOfInterest>http://bom.gov.au/waterdata/services/stations/""" + stationID + """</sos:featureOfInterest>
                            <sos:temporalFilter>
                            <fes:During>
                            <fes:ValueReference>om:phenomenonTime</fes:ValueReference>
                            <gml:TimePeriod gml:id="tp1">
                            <gml:beginPosition>1889-01-01T00:00:00+10</gml:beginPosition>
                            <gml:endPosition>""" + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+10") + """</gml:endPosition>
                            </gml:TimePeriod>
                            </fes:During>
                            </sos:temporalFilter>
                            </sos:GetObservation>
                            </soap12:Body>
                            </soap12:Envelope>"""
            
            # print(requestData)
            
            # POST request
            # This sends the payload and headers specified above to the url of the BoM waterdata web service
            # and stores the result in "response"
            # response = "<Response [500]>"
            response = requests.request("POST", url, headers=headers, data=requestData, proxies=proxies)
            countTries = 1
            
            # print("response: " + str(response.status_code))
            
            while response.status_code != 200:
                countTries += 1
                time.sleep(3)
                response = requests.request("POST", url, headers=headers, data=requestData, proxies=proxies)
                if countTries >= 20:
                    print("Unable to get data from BoM web service after 20 retries.")
                    sys.exit()
            # response = requests.request("POST", url, headers=headers, data=requestData)
            
            # Debug print statements
            print("Number of attempts needed to get data: " + str(countTries))
            # print("response: " + str(response.status_code))
            # print(response)
            
            # BoMResponseXML contains the full XML response from the query
            BoMResponseXML = xml.dom.minidom.parseString(response.text)
            
            # Debug code to display the XML file in human readable form
            # pretty_xml_as_string = BoMResponseXML.toprettyxml()
            # print(pretty_xml_as_string)
            
            # Extract all OM_Observation elements from the full XML response
            SunWaterSiteData = BoMResponseXML.getElementsByTagName("om:OM_Observation")
            
            # Debug code to check number of observation series
            #numObs = SunWaterSiteData.length
            
            for allSeries in SunWaterSiteData:
                siteName = allSeries.getElementsByTagName("om:featureOfInterest")[0].getAttribute("xlink:href").rsplit('/', 1)[1]
                seriesID = allSeries.getAttribute("gml:id")
                series = allSeries.getElementsByTagName("om:result")[0]
                BoMToCSV(series, seriesID, siteName, obsProperty)

#end def getBoMWaterData
#==============================================================================

# In case running from IDE or command-line
if __name__ == '__main__':
    # pass
    getBoMWaterData("416409A")
    # getBoMWaterData("130109A")
    getBoMWaterData("130110A")

    
    
    
    