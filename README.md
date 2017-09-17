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

After downloading or cloning the repository, edit the `tclcheck_all.py` and change the `fc.fv`
variable to your current firmware version. Let's assume you have a UK BBB100-2, so your PRD would
be `PRD-63117-003` and as of September 2017, your firmware version would be `AAM481`. So change the
line with `fc.fv` to:

    fc.fv = "AAM481"

Also change the `fc.mode` line to:

    fc.mode = fc.MODE_OTA

Now run the script. You'll get an output like this:

```
List of latest OTA (from AAM481) firmware by PRD:
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
