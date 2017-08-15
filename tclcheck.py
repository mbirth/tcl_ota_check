#!/usr/bin/env python3

import hashlib
import random
import sys
import time
try:
    from defusedxml import ElementTree
except (ImportError, AttributeError):
    from xml.etree import ElementTree
import requests


def prep_sess():
    sess = requests.Session()
    sess.headers.update({"User-Agent": "com.tcl.fota/5.1.0.2.0029.0, Android"})
    return sess


def salt():
    millis = round(time.time() * 1000)
    tail = "{0:06d}".format(random.randint(0, 999999))
    return "{0}{1}".format(str(millis), tail)


def check(sess, serid, curef, fv="AAM481", osvs="7.1.1", mode=4, ftype="Firmware", cltp=2010, cktp=2, rtd=1, chnl=2):
    geturl = "http://g2master-us-east.tctmobile.com/check.php"
    params = {"id": serid, "curef": curef, "fv": fv, "mode": mode, "type": ftype, "cltp": cltp, "cktp": cktp, "rtd": rtd, "chnl": chnl, "osvs": osvs}
    req = sess.get(geturl, params=params)
    if req.status_code == 200:
        return(req.text)
    else:
        print(repr(req))
        print(repr(req.headers))
        print(repr(req.text))
        raise SystemExit


def update_request(sess, serid, curef, tv, fwid, salt, vkh, fv="AAM481", mode=4, ftype="Firmware", cltp=2010):
    posturl = "http://g2master-us-east.tctmobile.com/download_request.php"
    params = {"id": serid, "curef": curef, "fv": fv, "mode": mode, "type": ftype, "tv": tv, "fw_id": fwid, "salt": salt, "vk": vkh, "cltp": cltp}
    req = sess.post(posturl, data=params)
    if req.status_code == 200:
        return req.text
    else:
        print(repr(req))
        print(repr(req.headers))
        print(repr(req.text))
        raise SystemExit


def getcode(sess, url):
    req = sess.head(url)
    return req.status_code


def vkhash(serid, curef, tv, fwid, salt, fv="AAM481", ftype="Firmware", mode=4, cltp=2010):
    vdkey = "1271941121281905392291845155542171963889169361242115412511417616616958244916823523421516924614377131161951402261451161002051042011757216713912611682532031591181861081836612643016596231212872211620511861302106446924625728571011411121471811641125920123641181975581511602312222261817375462445966911723844130106116313122624220514"
    query = "id={0}&salt={1}&curef={2}&fv={3}&tv={4}&type={5}&fw_id={6}&mode={7}&cltp={8}{9}".format(serid, salt, curef, fv, tv, ftype, fwid, mode, cltp, vdkey)
    engine = hashlib.sha1()
    engine.update(bytes(query, "utf-8"))
    return engine.hexdigest()


def parse_check(body):
    root = ElementTree.fromstring(body)
    tv = root.find("VERSION").find("TV").text
    fwid = root.find("FIRMWARE").find("FW_ID").text
    fileinfo = root.find("FIRMWARE").find("FILESET").find("FILE")
    filename = fileinfo.find("FILENAME").text
    filesize = fileinfo.find("SIZE").text
    filehash = fileinfo.find("CHECKSUM").text
    return tv, fwid, filename, filesize, filehash


def parse_request(body):
    root = ElementTree.fromstring(body)
    slave = root.find("SLAVE_LIST").find("SLAVE").text
    dlurl = root.find("FILE_LIST").find("FILE").find("DOWNLOAD_URL").text
    return "http://{0}{1}".format(slave, dlurl)


def main2(sess, serid, curef):
    checktext = check(sess, serid, curef)
    tv, fwid, fn, fs, fh = parse_check(checktext)
    print("{0}: {1}".format(curef, tv))

def main(sess, serid, curef):
    checktext = check(sess, serid, curef)
    print(repr(checktext))
    tv, fwid, filename, filesize, filehash = parse_check(checktext)
    slt = salt()
    vkh = vkhash(serid, curef, tv, fwid, slt)
    updatetext = update_request(sess, serid, curef, tv, fwid, slt, vkh)
    print(repr(updatetext))
    downloadurl = parse_request(updatetext)
    print("{0}: HTTP {1}".format(filename, getcode(sess, downloadurl)))
    print(downloadurl)


if __name__ == "__main__":
    sess = prep_sess()
    serid = "543212345000000"
    if len(sys.argv) > 1:
        if sys.argv[1] == "l":
            with open("prds.txt", "r") as afile:
                prdx = afile.read()
                prds = list(filter(None, prdx.split("\n")))
            for prd in prds:
                try:
                    main2(sess, serid, prd)
                except:
                    print("{} failed.".format(prd))
                    continue
        else:
            curef = sys.argv[1]
            main(sess, serid, curef)
    else:
        curef = "PRD-63764-001"
        main(sess, serid, curef)
