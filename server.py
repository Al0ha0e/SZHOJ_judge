import socket
import os
import json
import judger
import threading
import shutil
import time

BUFSIZE = 8*1024*1024


# qid
# data
# ucode
# timeLimit
# memoryLimit

class HeartBeatSender(threading.Thread):
    def __init__(self, sock, masterIp):
        threading.Thread.__init__(self)
        self.sock = sock
        self.masterIp = masterIp
        self.hbPack = json.dumps(
            {"qid": 0, "time": 0, "memory": 0, "state": 0}).encode()

    def run(self):
        while True:
            time.sleep(1)
            self.sock.sendto(self.hbPack,self.masterIp)


class MasterListener(threading.Thread):
    def __init__(self, sock, judger, masterIp):
        threading.Thread.__init__(self)
        self.sock = sock
        self.judger = judger
        self.masterIp = masterIp

    def run(self):
        while True:
            req, _ = self.sock.recvfrom(BUFSIZE)
            req = req.decode()
            req = json.loads(req)
            print(req)
            self.setupEnv(str(req['qid']), req['data'],
                          req['ucode'])
            result = {"qid": req["qid"], "time": 0, "memory": 0, "state": 0}
            if self.judger.compile("user") == -1:
                result["state"] = -2  # compile failed
                print("COMPILE FAIL")
                continue
            else:
                result = self.judger.judge(
                    req["timeLimit"], req["memoryLimit"])
                result["qid"] = req["qid"]
            res = json.dumps(result)
            self.sock.sendto(res.encode("utf-8"), self.masterIp)
            self.cleanEnv(str(req['qid']))

    def setupEnv(self, qid, datain,dataout, ucode):
        if os.path.exists(qid):
            shutil.rmtree(qid)
        os.makedirs(qid)
        codef = open(qid + "/standard", "w")
        codef.write(data)
        codef.close()
        ucodef = open(qid + "/user.cpp", "w")
        ucodef.write(ucode)
        ucodef.close()
        self.judger.init(qid+"/", "data")

    def cleanEnv(self, qid):
        shutil.rmtree(qid)
        # print(data.decode(), client_addr)


class JudgeServer:
    def __init__(self, selfIp, masterIp):
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSock.bind(selfIp)
        self.masterIp = masterIp
        self.judger = judger.Judger()
        self.hbSender = HeartBeatSender(self.serverSock, self.masterIp)
        self.msListener = MasterListener(
            self.serverSock, self.judger, self.masterIp)

    def connect(self):
        initPack = {"qid": -1, "time": 0, "memory": 0, "state": 0}
        initJSON = json.dumps(initPack)
        self.serverSock.sendto(initJSON.encode("utf-8"), self.masterIp)

    def run(self):
        self.hbSender.start()
        self.msListener.start()
