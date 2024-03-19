# [How to Retrieve Early Partial Delivery of Embargoed Reports via DataScope Select REST API](https://developers.lseg.com/en/article-catalog/article/how-to-retrieve-early-partial-delivery-of-embargoed-reports-via-0)

The Python example demonstrates how to perform the immediate schedule Intraday Pricing extraction with the PartialEmbargoedReportsEnabled options enabled. The example can be downloaded from GitHub. You can run the example with the following parameters.

```
EarlyPartialReportPython.py -u <DSS username> -p <DSS Password>
```

The list of instruments and content fields can be modified in the code.

```
instrument_list = [
    ('Ric','0001.HK'),
    ('Ric','IBM.N'),
    ('Ric','JPY='),
    ('Ric','1579.T'),
    ('Ric','PTT.BK')
    ]

...

intraday_fields =[
    'RIC',
    'Last Price',
    'Last Update Time',
    'Last Volume',
    'Bid Price',
    'Ask Price',
    'Bid Size',
    'Ask Size'
    ]
```
The output is:
```
####################################################################

    Disclaimer:
    The example applications presented here has been written by LSEG for the only purpose of illustrating articles published on the LSEG Developer Community. These example applications has not been tested for a usage in production environments. LSEG cannot be held responsible for any issues that may happen if these example applications o
r the related source code is used in production or any other client environment.

####################################################################

DSS username is  9008895

1. Request a token
==================
Token is _77_swwUP_xxx2OK04Qj79Z4yNKfI

2. Get embargo description
==========================
RIC             Current Embargo Delay
0001.HK         5 minute(s)
IBM.N           0 minute(s)
JPY=            0 minute(s)
1579.T          20 minute(s)
PTT.BK          15 minute(s)

3. Check the partial embargoed reports settings
=================================================
Current Settings:
PartialEmbargoedReportsEnabled: False
IntermediateReportsEnabled: False
DeltaReportsEnabled: False
Date Format: MM/dd/yyyy
Time Format: tt hh:mm:ss

Update Settings:
PartialEmbargoedReportsEnabled: True
IntermediateReportsEnabled: True
DeltaReportsEnabled: True


4. Schedule an immediate extraction
=====================================
4.1 Create an instrument list
The instrument list ID of EmbargoedTestInstrumentList is 0x089e325b5e591445

4.2 Append instruments to an instrument list
Append 5 instruments

4.3 Create an intraday pricing report template
The report template ID of EmbargoedTestIntradayPricingTemplate is 0x089e5e7fdc091485

4.4 Schedule an immediate extraction
The schedule ID of this immediate extraction is 0x089e2deb5b891440

5. Get a report extraction
============================
Report Extraction ID is 2000000608864226, Status: Pending/Queued

6. Get Notes and Data
######################
6.1 Get Notes


Extraction Services Version 17.3.1.46134 (701464ae16af), Built Aug  1 2023 16:17:07
User has overridden estimates broker entitlements.
Processing started at 09/08/2023 AM 11:17:31.
User ID: 9008895
Extraction ID: 2000000608864226
Correlation ID: CiD/9007633/Z3YuAA.08983130b5a90800/EQM/ED.0x089e2deb5b991440.0
Schedule: EmbargoedTestImmediateSchedule (ID = 0x089e2deb5b891440)
Input List (5 items): EmbargoedTestInstrumentList (ID = 0x089e325b5e591445) Created: 09/08/2023 AM 11:17:25 Last Modif
ied: 09/08/2023 AM 11:17:26
Report Template (8 fields): EmbargoedTestIntradayPricingTemplate (ID = 0x089e5e7fdc091485) Created: 09/08/2023 AM 11:1
7:28 Last Modified: 09/08/2023 AM 11:17:28
Schedule dispatched via message queue (0x089e2deb5b991440)
Schedule Time: 09/08/2023 AM 11:17:29
Temporary Integration Test Checkpoint 22
Successful operation - data received from RDP
Real-time data was snapped at the following times:
   09/08/2023 AM 11:17:29
   09/08/2023 AM 11:17:32 for data scheduled to snap at 09/08/2023 AM 11:17:29.
Processing completed successfully at 09/08/2023 AM 11:17:32, taking 0.486 Secs.
Extraction finished at 09/08/2023 AM 04:17:32 UTC, with servers: xc06xfhcQ13, QSDHA1 (0.0 secs), QSHC20 (0.1 secs)
Columns for (RIC,IBM.N,NYS) suppressed due to trade date other than today
Embargo delay of 20 minutes required by [ TYO (TOKYO STOCK EXCHANGE), TYM (TOKYO SE FLEX FULL OPEN MKT MODEL) ] for qu
otes from TYO
Embargo delay of 15 minutes required by [ SET (STOCK EXCHANGE OF THAILAND), ST2 (STOCK EXCHANGE OF THAILAND L1 L2) ] f
or quotes from SET
The last report will be embargoed until 09/08/2023 AM 11:37:31 (20 minutes) due to quote: RIC,1579.T,TYO - Last Update
 Time: 09/08/2023 AM 11:17:31.
Usage Summary for User 9008895, Client 65507, Template Type Intraday Pricing
Base Usage
        Instrument                          Instrument                   Terms          Price
  Count Type                                Subtype                      Source         Source
------- ----------------------------------- ---------------------------- -------------- ------------------------------
----------
      4 Equities                                                         N/A            N/A
      1 Money Market                                                     N/A            N/A
-------
      5 Total instruments charged.
      0 Instruments with no reported data.
=======
      5 Instruments in the input list.
No Evaluated Pricing Service complex usage to report -- 5 Instruments in the input list had no reported data.
The file 9008895.EmbargoedTestImmediateSchedule.20230908.111731.2000000608864226.xc06xfhcQ13.0min.csv will be available immediately.The file 9008895.EmbargoedTestImmediateSchedule.20230908.111731.2000000608864226.xc06xfhcQ13.15min.csv will be embargoed until 09/08/2023 AM 11:32:25. The file 9008895.EmbargoedTestImmediateSchedule.20230908.111731.2000000608864226.xc06xfhcQ13.20min.csv will be embargoed until 09/08/2023 AM 11:37:31.
Writing RIC maintenance report.


6.2 Get Data
2023-09-08 11:17:42: 9008895.EmbargoedTestImmediateSchedule.20230908.111731.2000000608864226.xc06xfhcQ13.0min.csv

RIC,Last Price,Last Update Time,Last Volume,Bid Price,Ask Price,Bid Size,Ask Size
0001.HK,,09/08/2023 AM 11:10:55,,,,,
IBM.N,,09/08/2023 AM 11:16:16,,,,0,0
JPY=,147.25,09/08/2023 AM 11:17:31,,147.25,147.3,,

Wait for Embargo Delay: 893 seconds
2023-09-08 11:32:42: 9008895.EmbargoedTestImmediateSchedule.20230908.111731.2000000608864226.xc06xfhcQ13.15min.csv


RIC,Last Price,Last Update Time,Last Volume,Bid Price,Ask Price,Bid Size,Ask Size
PTT.BK,35,09/08/2023 AM 11:17:25,"1,500",34.75,35,"11,265,300","7,764,600"

Wait for Embargo Delay: 1199 seconds
2023-09-08 11:37:56: 9008895.EmbargoedTestImmediateSchedule.20230908.111731.2000000608864226.xc06xfhcQ13.20min.csv

RIC,Last Price,Last Update Time,Last Volume,Bid Price,Ask Price,Bid Size,Ask Size
1579.T,"21,290",09/08/2023 AM 11:17:31,60,"21,285","21,295",210,490


7. Cleanup
############
Delete the schedule: 0x089e2deb5b891440
Delete the intraday pricing report template: 0x089e5e7fdc091485
Delete the instrument list: 0x089e325b5e591445
Reset the user preferences

Press any key to continue . . .
```
