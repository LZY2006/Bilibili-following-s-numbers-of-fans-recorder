import requests
from pprint import pprint
import json
import time
import pickle
import traceback

import win32con
import win32gui

def get_dicts(debug, cookie):
    result = []
    url = "https://api.bilibili.com/x/relation/followings?vmid=253119876&pn={}&ps=20&order=desc"
    headers = {"Cookie":cookie}
    pn = 1
    while True:
        r = requests.get(url.format(pn), headers=headers, timeout=5) # 获取json格式数据
        time.sleep(1.2)
        #############
##        if debug:
##            print(r.status_code, r.encoding)
        #############
        dic = json.loads(r.text)     # 用json载入
##        print(dic)
        if len(dic["data"]["list"]) < 1:
            return result
        info = dic["data"]["list"]
        result.append(info)
        pn += 1

def lDict2lData(dicts):
    result = []
    for i in dicts:
        for j in i:
            mid = j["mid"]
            uname = j["uname"]
##            print([mid, uname])
            result.append({"mid":mid, "uname":uname})
    return result

def dFollower(data, cookie):
    api = "https://api.bilibili.com/x/relation/stat?vmid={}"
    result = {}
    for i in data:
        url = api.format(i["mid"])
        headers = {"Cookie":cookie}

        # 从API获取数据
        while True:
            try:
                r = requests.get(url, headers=headers, timeout=5)
                break
            except:
                print("发生了一个错误:\n", traceback.format_exc())
                continue
            
        dic = json.loads(r.text)
        nFollower = dic["data"]["follower"]
##        result.append(
##            {
##                i["mid"]: [ i["uname"], nFollower, time.time() ]
##             }
##        )
        result[i["mid"]] = [i["uname"], nFollower, time.time()]
                      

        # 打印调试信息
        print("mid:", i["mid"], "uname:", i["uname"], "follower:", nFollower)
        write_log(
            "mid:{}, uname:{}, follower:{}".format( i["mid"], i["uname"], nFollower)
                  )

        #防止服务器屏蔽IP，暂停1.2秒
        time.sleep(1.2)
    return result

def write_log(text):
    pass
##    log_file = open(r"C:\learn\py\我关注的UP的粉丝数\debug.log", "a")
##    log_file.write(text+"\n")
##    log_file.close()
##    del log_file

# 主程序
def main(debug, cookie):
    while True:
##        log_file = open(r"C:\learn\py\我关注的UP的粉丝数\debug.log", "w")
        try:
            print("start")
            write_log("start")
            dicts = get_dicts(debug, cookie)
            # 把数据变成[mid, uname]
            data = lDict2lData(dicts)
            
            # 把处理过的数据变成{mid: [uname, 粉丝数, timestamp]}
            result = dFollower(data, cookie)
            # 打印结果
##            pprint(result)
            
            with open(r".\record.pkl", "rb+") as f:
                try:
                    before = pickle.load(f)
                except EOFError:
                    print("Can't read the file.")
                    before = []
                write_obj = before + [result]
                f.seek(0)
                pickle.dump(write_obj, f)
            print("Done.")
            write_log("Done.")
            for i in range(600):
                time.sleep(1)
        except Exception:
            err = traceback.format_exc()
            print("There's something wrong:", err)
            write_log("There's something wrong:"+ err)

            result = win32gui.MessageBox(0, err+"\r"+"想要终止程序吗？", "Error", win32con.MB_YESNO | win32con.MB_ICONWARNING)
            if result == 6:
                quit()
            

            time.sleep(60)
            continue
        except KeyboardInterrupt:
            quit()

if __name__ == "__main__":

    cookie = "" # your cookie
    main(debug=True, cookie=cookie)
