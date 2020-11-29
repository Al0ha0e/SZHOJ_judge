#import _judger
import os


class Judger:
    def __init__(self):
        pass

    def init(self, workdir, dataname):
        self.workdir = workdir
        self.dataname = dataname

    def compile(self, filename):
        self.filename = filename
        if os.system("g++ " + self.workdir + filename + ".cpp" + " -o " + self.workdir + filename):
            return - 1
        return 0

    #time_limit (ms)
    #memory_limit (KB)
    def judge(self, time_limit, memory_limit):
        running_result = _judger.run(max_cpu_time=time_limit,
                                     max_real_time=2*time_limit,
                                     max_memory=memory_limit * 1024,
                                     max_process_number=200,
                                     max_output_size=10000,
                                     max_stack=32 * 1024 * 1024,
                                     # five args above can be _judger.UNLIMITED
                                     exe_path=self.workdir+self.filename,  # "./test/main",
                                     input_path=self.workdir+self.dataname+".in",  # "./test/1.in",
                                     output_path=self.workdir+self.dataname+".out",  # "./test/1.out",
                                     error_path=self.workdir+self.dataname+".out",
                                     args=[],
                                     # can be empty list
                                     env=[],
                                     log_path=self.workdir+"judger.log",
                                     # can be None
                                     seccomp_rule_name="c_cpp",
                                     uid=0,
                                     gid=0)
        # print(running_result.result)
        result = {"qid": 0, "time": running_result['real_time'],
                  "memory": running_result['memory'], "state": running_result['result']}
        if running_result['result'] != 0:
            return result
        with open(self.workdir + "standard") as ansf:
            ans = ansf.read().strip()
            with open(self.workdir + self.dataname + ".out") as usrf:
                usrans = usrf.read().strip()
                if usrans != ans:
                    result["state"] = -1  # WA
        return result

        # while ans[-1] == '\t' or ans[-1] == '\n' or ans
        # if ans !=
