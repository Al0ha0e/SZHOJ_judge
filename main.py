import server


svr = server.JudgeServer(("", 8040), ("192.168.58.1", 8040))

svr.connect()

svr.run()
