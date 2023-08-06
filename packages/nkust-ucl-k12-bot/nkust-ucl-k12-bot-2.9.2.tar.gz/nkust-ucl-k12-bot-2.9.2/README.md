# K12

# **NKUST UCL K12 ChatBot**

## **簡介**

NKUST UCL K12 ChatBot 是一個基於 K12 API 的 ChatBot，它能夠自動發送文字訊息、圖片、文件，接收到來自聊天室的訊息，支援消息歷史查詢。

## **安裝**

使用 pip 安裝：

```bash
pip install nkust-ucl-k12-bot

```

## **用法**
### 一個簡單的所有範例
```python
from nkust_ucl.k12 import BOT as K12
from nkust_ucl.k12 import MsgType, CommandHandler
custom_k12 = K12(config_file='example/config/k12.yaml')
custom_k12.set_chat_bot_info(
    SendUserID="1234567890987654321",
    SendUserName="test_bot",
    SendUserImage="https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/512px-ChatGPT_logo.svg.png"
)


@K12.on_connect
def my_custom_on_connect(self, client, userdata, flags, rc):
    # ... 自定義的 on_connect 行為 ...
    client.subscribe(self.client.mqttSubscribe)
    print("開始訂閱")


@K12.on_processed_message
def my_custom_on_processed_message(self, chat_msg):
    # ... 自定義的 on_processed 行為 ...
    # 這邊就是當收到訊息要做什麼事情
    # 可以調用chat_msg的屬性
    # chat_msg.send_user_name: 發送者的名字
    # chat_msg.send_user_id: 發送者的id
    # chat_msg.send_user_image: 發送者的頭像
    # chat_msg.msg_body: 訊息內容
    # chat_msg.room_id: 房間id
    # chat_msg.msg_type: 訊息類型
    # chat_msg.timestamp: 訊息時間戳
    # chat_msg.mode: 訊息模式
    # chat_msg.msg_id: 訊息id
    if chat_msg.send_user_id == "1234567890987654321":
        return
    command_handler.handle_command(chat_msg)


# 註冊指令
command_handler = CommandHandler()


def reply_chatgpt(message):
    message.reply("test")


command_handler.register_command("/chatgpt", MsgType.TEXT, reply_chatgpt)

# run要在最後面
custom_k12.run()
```
## v2.9.0更新
* 快速回復新增了以下方法，支援本地檔案與網路檔案
```python
reply_text(msg: str)
reply_image(image_path: str)
reply_document(file_path: str)
```
usage:
```python
@K12.on_processed_message
def my_custom_on_processed_message(self, chat_msg: ChatMessage):
    # ... 自定義的 on_processed 行為 ...
    if chat_msg.send_user_id == "1234567890987654321":
        return
    chat_msg.reply_text("test")
    chat_msg.reply_image("test.png")
    chat_msg.reply_image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/512px-ChatGPT_logo.svg.png")
    chat_msg.reply_document("test.txt")
```

## v2.8.3更新
我們在ChatMessage的類別中新增了reply方法，可以直接回覆訊息
```python
reply(self, msg: str, msg_type: MsgType = MsgType.TEXT)
```
```python
@K12.on_processed_message
def my_custom_on_processed_message(self, chat_msg: ChatMessage):
    # ... 自定義的 on_processed 行為 ...
    if chat_msg.send_user_id == "1234567890987654321":
        return
    chat_msg.reply("test")
```
### **建立CommandHandler**
在CommandHandler中可以註冊指令，並且指定指令的類型，當收到指定類型的指令時，會呼叫指定的函式
* register_command(command: str, msg_type: MsgType, func: Callable[[ChatMessage], None])
    * command: 指令
    * msg_type: 指令類型
    * func: 當收到指令時要呼叫的函式
```python
from nkust_ucl.k12 import CommandHandler
command_handler = CommandHandler()

def reply_chatgpt(message):
    message.reply("test")


command_handler.register_command("/chatgpt", MsgType.TEXT, reply_chatgpt)
```
我們必須在on_processed_message中呼叫command_handler.handle_command來處理指令，這樣就可以在收到指令時呼叫指定的函式
```python
@K12.on_processed_message
def my_custom_on_processed_message(self, chat_msg: ChatMessage):
    # ... 自定義的 on_processed 行為 ...
    if chat_msg.send_user_id == "1234567890987654321":
        return
    command_handler.handle_command(chat_msg)
```

## v2.8.0以前
### **初始化 K12 Bot**

```python
from nkust_ucl.k12 import BOT as K12
from nkust_ucl.k12 import MsgType, CommandHandler
custom_k12 = K12(config_file='example/config/k12.yaml')
custom_k12.set_chat_bot_info(
    SendUserID="1234567890987654321",
    SendUserName="test_bot",
    SendUserImage="https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/512px-ChatGPT_logo.svg.png"
)
```

### **發送文字訊息**

```python
custom_k12.send_text(roomid="12345", text="你好！")

```

### **發送圖片**

```python
# image_path可以是網址或是本地路徑
custom_k12.send_image(roomid="12345", image_path="/path/to/image.png")

```

### **發送文件**

```
# doc_path可以是網址或是本地路徑
custom_k12.send_document(roomid="12345", doc_path="/path/to/document.pdf")

```

### **接收訊息**

註冊 **`on_processed_message`** 處理方法以接收來自聊天室的訊息：

```

@K12.on_processed_message
def my_custom_on_processed_message(self, chat_msg):
    # ... 自定義的 on_processed 行為 ...
    # ChatMsg 為訊息物件

```

### **自定義 on_connect 行為**

```

@K12.on_connect
def my_custom_on_connect(self, client, userdata, flags, rc):
    # ... 自定義的 on_connect 行為 ...
    # self.client.mqttSubscribe為訂閱的主題
    client.subscribe(self.client.mqttSubscribe)
    print("開始訂閱")

```

## **如何貢獻**

1. Fork 專案
2. 創建新的分支 (**`git checkout -b feature/fooBar`**)
3. 提交你的修改 (**`git commit -am 'Add some fooBar'`**)
4. 推送到分支 (**`git push origin feature/fooBar`**)
5. 創建一個新的 Merge Request

## **License**

**[MIT](https://choosealicense.com/licenses/mit/)**