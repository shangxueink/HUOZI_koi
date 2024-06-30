
# HUOZI
电棍活字印刷后端
基于 Flask 框架
## 食用方法
### Python 版本
- 3.8.x
### 部署步骤（仅以Windows为例）
1. 克隆项目仓库：
```bash
git clone <仓库地址>
cd <项目目录>
```
2. 创建虚拟环境：
```bash
python -m venv venv
```

激活虚拟环境
```cmd
venv\Scripts\activate.bat
```

3. 安装必要的构建工具：
```bash
pip install setuptools wheel
```
4. 安装依赖模块：
```bash
pip install -r requirements.txt
```
5. 配置文件路径：
- 如果有需要，你可以根据 `settings.json` 修改文件路径（注意，Linux 与 Windows 路径写法不一致）
6. 运行服务：

```cmd
python app.py
```

7. 访问服务：
- 在浏览器中访问 [http://127.0.0.1:8989](http://127.0.0.1:8989) (默认端口为 8989，可以在 `app.py` 中更改)
## 使用 API 调用
你可以通过 API 来生成音频，以下是使用示例：
### API 端点
- `GET /api/make`
### 请求参数
- `text` (字符串): 要转换的文本
- `inYsddMode` (布尔值): 是否启用 Ysdd 模式 (`true`/`false`)
- `norm` (布尔值): 是否启用 norm 模式 (`true`/`false`)
- `reverse` (布尔值): 是否启用反转模式 (`true`/`false`)
- `speedMult` (浮点数): 速度倍增器 (0.5 - 2.0)
- `pitchMult` (浮点数): 音高倍增器 (0.5 - 2.0)
### 示例请求
**GET 请求示例：**
```
http://127.0.0.1:8989/api/make?text=你好啊&inYsddMode=false&norm=false&reverse=false&speedMult=1.0&pitchMult=1.0
```
### 响应格式
- 成功响应：
```json
{
    "code": 200,
    "id": "<生成的文件ID>",
    "file_path": "<生成的文件路径>"
}
```
- 错误响应：
```json
{
    "code": 400,
    "message": "<错误信息>"
}
```
## 其他注意事项
- 请确保在使用 API 时正确处理路径及参数。
- 项目默认使用 8989 端口，你可以在 `app.py` 文件中更改端口配置。