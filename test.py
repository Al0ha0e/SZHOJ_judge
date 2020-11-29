import judger


jd = judger.Judger("./test/", "test")


jd.compile("main")

print(jd.judge(1000, 1024))
