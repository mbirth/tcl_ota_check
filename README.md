[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/mbirth/tcl_ota_check/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/mbirth/tcl_ota_check/?branch=master)
[![Build Status](https://scrutinizer-ci.com/g/mbirth/tcl_ota_check/badges/build.png?b=master)](https://scrutinizer-ci.com/g/mbirth/tcl_ota_check/build-status/master)
[![Code Intelligence Status](https://scrutinizer-ci.com/g/mbirth/tcl_ota_check/badges/code-intelligence.svg?b=master)](https://scrutinizer-ci.com/code-intelligence)


TCL OTA Check
=============

This is a Python script originally created by [thurask](https://gist.github.com/thurask) ([original
GIST](https://gist.github.com/thurask/f4ace564e6575ef41c4e35d2458ca2d0)) to check for update files
for a BlackBerry KEYone phone. It tries to emulate the requests done by the "Updater" app or the
"Mobile Q Loader" firmware updater.


What is a FOTA/OTA?
-------------------

(F)OTA = (Firmware) Over-the-Air

OTAs are differential(!) updates for a specific firmware version to a newer one. To install it,
you **must** have the correct initial firmware installed. Otherwise, the updater script will fail
and abort the update.


How to find available OTA updates
---------------------------------

After downloading or cloning the repository, make all tclcheck*.py scripts executable if needed.
Let's assume you have a UK BBB100-2, so your PRD would be `PRD-63117-003` and as of September
2017, your firmware version would be `AAM481`. Just run the following script:

    ./tclcheck_allota.py AAM481

You'll get an output like this:

```
List of latest OTA firmware from AAM481 by PRD:
...
PRD-63117-003 failed. (No update available.)
PRD-63117-011: AAM481 ⇨ AAN358 d819919187b46793abeaeff60dd6deee17baac4b (QWERTZ BBB100-2 (Germany))
PRD-63117-015: AAM481 ⇨ AAN358 d819919187b46793abeaeff60dd6deee17baac4b (BBB100-2 (NL, Belgium))
PRD-63117-019: AAM481 ⇨ AAN358 d819919187b46793abeaeff60dd6deee17baac4b (BBB100-2)
PRD-63117-023: AAM481 ⇨ AAN358 d819919187b46793abeaeff60dd6deee17baac4b (AZERTY BBB100-2 (Belgium))
PRD-63117-025 failed. (No data for requested CUREF/FV combination.)
PRD-63117-027: AAM481 ⇨ AAN358 d819919187b46793abeaeff60dd6deee17baac4b (QWERTY BBB100-2 (UAE))
PRD-63117-028: AAM481 ⇨ AAN358 d819919187b46793abeaeff60dd6deee17baac4b (BBB100-2)
PRD-63117-029: AAM481 ⇨ AAN358 d819919187b46793abeaeff60dd6deee17baac4b (BBB100-2)
PRD-63117-034 failed. (No data for requested CUREF/FV combination.)
PRD-63117-036 failed. (No data for requested CUREF/FV combination.)
PRD-63117-037 failed. (No data for requested CUREF/FV combination.)
PRD-63117-041: AAM481 ⇨ AAN358 d819919187b46793abeaeff60dd6deee17baac4b (BBB100-2)
PRD-63117-042 failed. (No data for requested CUREF/FV combination.)
PRD-63117-703 failed. (No data for requested CUREF/FV combination.)
PRD-63117-704 failed. (No data for requested CUREF/FV combination.)
PRD-63117-717 failed. (No data for requested CUREF/FV combination.)
...
```

As you can see, our `PRD-63117-003` variant doesn't have the update yet, but other variants have.

You can use this info, to [install the update for a different variant](http://wiki.mbirth.de/know-how/hardware/blackberry-keyone/bb-keyone-ota-updates-for-different-variants.html).
Just make sure to use a variant that has the same model number (`63117` = BBB100-2).


What do those other scripts do?
-------------------------------

(All commands support the `--help` parameter to print out the expected syntax.)


### tclcheck_allfull.py

Checks for the latest FULL (i.e. complete firmwares to install manually) versions available for all
different models and variants.


### tclcheck_allota.py

Checks for the latest OTA (i.e. partial updates for over-the-air installation) versions available
for all different models and variants.


### tclfindprd.py

Scans for not yet known variants of a model.


### tclfindprd2.py

Scans for not yet known models.


### tclfindver.py

Scans for not yet known firmware versions.


### tclgapfill.py

Queries the [database server](https://tclota.birth-online.de/) for known versions and tries to find
OTA files not yet in the database.


### tclcheck.py

Universal tool to query TCL's servers in different ways to manually check for a specific update.


### tclchksum.py

Queries the checksum for a specific FULL file.


### tcldown.py

Downloads a firmware file from given file ID.


### update_db.py

Updates local copy of database.


### upload_logs.py

Uploads all collected server answers to the [database server](https://tclota.birth-online.de/).
