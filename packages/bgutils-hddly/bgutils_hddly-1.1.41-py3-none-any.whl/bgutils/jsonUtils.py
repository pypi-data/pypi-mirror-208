class checkJSON(object):
    def getKeys(self, data):
        keysAll_list = []

        def getkeys(data):  # 遍历json所有key
            if (type(data) == type({})):
                keys = data.keys()
                for key in keys:
                    value = data.get(key)
                    if (type(value) != type({}) and type(value) != type([])):
                        keysAll_list.append(key)
                    elif (type(value) == type({})):
                        keysAll_list.append(key)
                        getkeys(value)
                    elif (type(value) == type([])):
                        keysAll_list.append(key)

                for para in value:
                    if (type(para) == type({}) or type(para) == type([])):
                        getkeys(para)
                    else:
                        keysAll_list.append(para)

        getkeys(data)
        return keysAll_list

    def isExtend(self, data, tagkey):  # 检测目标字段tagkey是否在data(json数据)中
        if (type(data) != type({})):
            print('please input a json!')
        else:
            key_list = self.getKeys(data)
            for key in key_list:
                if (key == tagkey):
                    return True
        return False
    def isExistKey(self, data, keyname):
        if (keyname in data):
            return True
        else:
            return False
