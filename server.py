import socket
import os
import json
import judger
import shutil

BUFSIZE = 8*1024*1024


# qid
# data
# ucode
# timeLimit
# memoryLimit


class JudgeServer:
    def __init__(self, selfIp, masterIp):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(selfIp)
        self.masterIp = masterIp
        self.judger = judger.Judger()

    def connect(self):
        pass

    def run(self):
        while True:
            req, _ = self.server.recvfrom(BUFSIZE)
            req = req.decode()
            req = json.loads(req)
            print(req)
            self.setupEnv(str(req['qid']), req['data'],
                          req['ucode'])
            result = [0, 0, 0]
            if self.judger.compile("user") == -1:
                result[3] = -2  # compile failed
            else:
                result = self.judger.judge(
                    req["timeLimit"], req["memoryLimit"])
            res = json.dumps(result)
            self.client.sendto(res.endcode("utf-8"), self.masterIp)
            self.cleanEnv(str(req['qid']))

    def setupEnv(self, qid, data, ucode):
        if os.path.exists(qid):
            shutil.rmtree(qid)
        os.makedirs(qid)
        codef = open(qid + "/standard", "w")
        codef.write(data)
        codef.close()
        ucodef = open(qid + "/user", "w")
        ucodef.write(ucode)
        ucodef.close()
        self.judger.init(qid+"/", "data")

    def cleanEnv(self, qid):
        shutil.rmtree(qid)
        #print(data.decode(), client_addr)
