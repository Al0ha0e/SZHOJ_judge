# SZHOJ　V１.0.0 判题节点
# 孙梓涵编写
# 本文件提供Worker服务器类
# 服务器使用同一个Socket，利用两个线程处理消息收发

import socket
import os
import json
import judger
import threading
import shutil
import time

BUFSIZE = 8*1024*1024


#  心跳信号发送线程类
class HeartBeatSender(threading.Thread):
    def __init__(self, sock, masterIp):
        threading.Thread.__init__(self)  # 初始化线程库
        self.sock = sock
        self.masterIp = masterIp
        self.hbPack = json.dumps(
            {"qid": 0, "time": 0, "memory": 0, "state": 0}).encode()

    def run(self):
        while True:
            time.sleep(1)  # 每秒发送一次心跳信号
            self.sock.sendto(self.hbPack, self.masterIp)


# 任务接受，结果发送类
class MasterListener(threading.Thread):
    def __init__(self, sock, judger, masterIp):
        threading.Thread.__init__(self)  # 初始化线程
        self.sock = sock
        self.judger = judger
        self.masterIp = masterIp

    def run(self):
        while True:
            req, _ = self.sock.recvfrom(BUFSIZE)
            req = req.decode()
            req = json.loads(req)
            print(req)
            self.setupEnv(str(req['qid']), req['datain'],
                          req['dataout'], req['ucode'])
            result = {"qid": req["qid"], "time": 0, "memory": 0, "state": 0}
            if self.judger.compile("user") == -1:
                result["state"] = 7  # compile failed
                print("COMPILE FAIL")
            else:
                result = self.judger.judge(
                    int(req["timeLimit"]), int(req["memoryLimit"]))
                result["qid"] = req["qid"]
            res = json.dumps(result)
            self.sock.sendto(res.encode("utf-8"), self.masterIp)  # 发送评测结果
            self.cleanEnv(str(req['qid']))

    def setupEnv(self, qid, datain, dataout, ucode):  # 在本地建立评测目录，创建相关文件
        if os.path.exists(qid):
            shutil.rmtree(qid)
        os.makedirs(qid)
        codef = open(qid + "/data.in", "w")
        codef.write(datain)
        codef.close()
        codef = open(qid + "/standard", "w")
        codef.write(dataout)
        codef.close()
        ucodef = open(qid + "/user.cpp", "w")
        ucodef.write(ucode)
        ucodef.close()
        self.judger.init(qid+"/", "data")

    def cleanEnv(self, qid):  # 清除评测痕迹
        shutil.rmtree(qid)
        # print(data.decode(), client_addr)


# 判题服务器类
class JudgeServer:
    # 初始化socket及线程
    def __init__(self, selfIp, masterIp):
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSock.bind(selfIp)
        self.masterIp = masterIp
        self.judger = judger.Judger()
        self.hbSender = HeartBeatSender(self.serverSock, self.masterIp)
        self.msListener = MasterListener(
            self.serverSock, self.judger, self.masterIp)

    # 连接调度器
    def connect(self):
        initPack = {"qid": -1, "time": 0, "memory": 0, "state": 0}
        initJSON = json.dumps(initPack)
        self.serverSock.sendto(initJSON.encode("utf-8"), self.masterIp)

    def run(self):
        self.hbSender.start()
        self.msListener.start()
