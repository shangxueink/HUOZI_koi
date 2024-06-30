from flask import Flask, request, render_template, make_response, jsonify, url_for
from huoZiYinShua import *
import time
import secrets
from os import remove, listdir
from threading import Thread, Lock
import logging
import sys
import os

# 临时文件存放目录
tempOutputPath = "./static/tempAudioOutput/"
# 确保目录存在
if not os.path.exists(tempOutputPath):
    os.makedirs(tempOutputPath)

# 进程锁
locker = Lock()
queueRecord = {
    "time": 0,
    "place": 0
}

# 启动日志
hzysLogger = logging.getLogger()
hzysFileHandler = logging.FileHandler("record.log", encoding="utf8", mode="a")
hzysFormatter = logging.Formatter("%(asctime)s, %(message)s")
hzysFileHandler.setFormatter(hzysFormatter)
hzysLogger.addHandler(hzysFileHandler)
hzysLogger.addHandler(logging.StreamHandler(sys.stdout))
hzysLogger.setLevel(logging.DEBUG)

# 生成ID
def makeid():
    locker.acquire()
    currentSec = str(int(time.time()))
    # 若进入下一秒，重置次序
    if queueRecord["time"] != currentSec:
        queueRecord["time"] = currentSec
        queueRecord["place"] = 0
    # ID=时间+次序+随机数
    id = currentSec + "_" + str(queueRecord["place"]) + "_" + secrets.token_hex(8)
    queueRecord["place"] += 1
    locker.release()
    return id

# 清理临时文件
def clearCache():
    while True:
        currentTime = int(time.time())  # 当前时间
        # 输出目录下的所有文件
        for fileName in listdir(tempOutputPath):
            # 文件名符合格式
            try:
                timeCreated = int(fileName.split("_")[0])  # 创建时间
                if (currentTime - timeCreated) > 600:  # 间隔时间(秒)
                    if fileName.endswith(".wav"):
                        remove(tempOutputPath + fileName)
            # 若文件名不符合格式，(currentTime - timeCreated)会报错
            except:
                pass
        time.sleep(60)

# 核心代码
app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template("home.html")

# 用户发出生成音频的请求（POST方法）
@app.route('/make', methods=['POST'])
def HZYSS():
    # 生成选项
    rawData = request.form.get("text")
    inYsddMode = (request.form.get("inYsddMode") == "true")
    norm = (request.form.get("norm") == "true")
    reverse = (request.form.get("reverse") == "true")
    speedMult = float(request.form.get("speedMult"))
    pitchMult = float(request.form.get("pitchMult"))
    # 记录日志
    app.logger.debug("%s", request.form)
    # 特殊情况不予生成音频并返回错误代码
    if len(rawData) > 100:
        return jsonify({"code": 400, "message": "憋刷辣！"}), 400
    if (speedMult < 0.5) or (speedMult > 2) or (pitchMult < 0.5) or (pitchMult > 2):
        return jsonify({"code": 400, "message": "你在搞什么飞机？"}), 400
    try:
        # 获取ID
        id = makeid()
        # 活字印刷实例
        HZYS = huoZiYinShua("./settings.json")
        # 导出音频
        file_path = os.path.join(tempOutputPath, id + ".wav")
        HZYS.export(rawData,
                    filePath=file_path,
                    inYsddMode=inYsddMode,
                    norm=norm,
                    reverse=reverse,
                    speedMult=speedMult,
                    pitchMult=pitchMult)
        # 返回URL
        file_url = url_for('static', filename='tempAudioOutput/' + id + '.wav', _external=True)
        return jsonify({"code": 200, "id": id, "file_url": file_url}), 200
    except Exception as e:
        print(e)
        return jsonify({"code": 400, "message": "生成失败"}), 400

# 用户发出下载音频的请求
@app.route('/get/<id>.wav')
def get_audio(id):
    try:
        with open(tempOutputPath + id + ".wav", 'rb') as f:
            audio = f.read()
        response = make_response(audio)
        response.content_type = "audio/wav"
        return response
    except:
        return render_template("fileNotFound.html"), 404

# 新增API接口，通过GET请求生成音频并返回本地文件的绝对地址
@app.route('/api/make', methods=['GET', 'POST'])
def api_make():
    if request.method == 'POST':
        rawData = request.form.get("text")
        inYsddMode = request.form.get("inYsddMode") == "true"
        norm = request.form.get("norm") == "true"
        reverse = request.form.get("reverse") == "true"
        speedMult = float(request.form.get("speedMult", 1.0))
        pitchMult = float(request.form.get("pitchMult", 1.0))
    else:
        rawData = request.args.get("text")
        inYsddMode = request.args.get("inYsddMode") == "true"
        norm = request.args.get("norm") == "true"
        reverse = request.args.get("reverse") == "true"
        speedMult = float(request.args.get("speedMult", 1.0))
        pitchMult = float(request.args.get("pitchMult", 1.0))
    if len(rawData) > 100:
        return jsonify({"code": 400, "message": "憋刷辣！"}), 400
    if (speedMult < 0.5) or (speedMult > 2) or (pitchMult < 0.5) or (pitchMult > 2):
        return jsonify({"code": 400, "message": "你在搞什么飞机？"}), 400
    try:
        id = makeid()
        HZYS = huoZiYinShua("./settings.json")
        file_path = os.path.join(tempOutputPath, id + ".wav")
        HZYS.export(rawData,
                    filePath=file_path,
                    inYsddMode=inYsddMode,
                    norm=norm,
                    reverse=reverse,
                    speedMult=speedMult,
                    pitchMult=pitchMult)
        file_url = url_for('static', filename='tempAudioOutput/' + id + '.wav', _external=True)
        return jsonify({"code": 200, "id": id, "file_url": file_url}), 200
    except Exception as e:
        print(e)
        return jsonify({"code": 400, "message": "生成失败"}), 400

if __name__ == '__main__':
    Thread(target=clearCache, args=()).start()
    app.run(port=8989, host='0.0.0.0')
