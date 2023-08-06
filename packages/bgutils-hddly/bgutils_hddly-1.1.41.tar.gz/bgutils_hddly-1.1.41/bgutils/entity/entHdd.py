from typing import List


class entResult(object):
    rlt=dict(key=0,value=None)
    rlt = {"code": 0, "result": ""}
    # def __init__(self, rltcode, rltdesc, *args, **kwargs):
    #     self.rlt["code"] = rltcode
    #     self.rlt["desc"] = rltdesc

    def __new__(self, code, result):
        self.rlt["code"] = code
        self.rlt["result"] = result
        return self.rlt