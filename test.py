import judger
import server

# jd = judger.Judger("./test/", "test")


# jd.compile("main")

# print(jd.judge(1000, 1024))


sv = server.JudgeServer(("", 8040), ("127.0.0.1", 8080))

sv.run()
