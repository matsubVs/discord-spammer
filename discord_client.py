import json

import requests as req
import websocket
from apscheduler.schedulers.background import BackgroundScheduler
from websocket import WebSocketApp
from dotenv import load_dotenv
import os

load_dotenv()


class DiscordConnection:
    def __init__(self):
        self.ws = None
        self.session_id = None
        self.token = os.getenv('CLIENT_TOKEN')
        self.spam_channel = os.getenv('SPAM_CHANNEL_ID')
        self.last_seq = None
        self.restart = False
        self.scheduler = BackgroundScheduler()
        self.start_scheduler()

    def send_spam(self):
        message = """ ```
Проходит набор в семью Bush.
 
У нас в семье:
1. Некогда скучать, контента выше крыши;
2. Блат в любой Crime фракции;
3. Каждый день тренировки по улучшению стрельбы;
4. Бесплатное снаряжение абсолютно всего;
5. Война семей с самым сильным союзом на сервере;
6. Семейные автомобили, начиная с Mersedes G63;
7. Свой собственный особняк;
8. Взаимопомощь в понимании игровых процессов;
9. Дружный коллектив, друг за друга рвем на клочья;
10. Понятный и простой Discord сервер.
 
Хмм...я вижу ты заинтересован.
Но, от тебя тоже кое-что нужно...
А именно: 

1. Возраст 16+;
2. Быть адекватным и активным игроком;
3. Поменять фамилию на "Bush";
4. Пятый уровень персонажа;
5. Желание расти как стрелок (семья расположена полностью в КРАЙМ сторону);
6. Не терять духа, и всегда быть в хорошем настроение и с холодной головой. ```
        """
        files = {"files[0]": open("unknown.png", "rb")}
        headers = {"authorization": self.token}
        files["payload_json"] = (None, json.dumps({"content": message}))
        x = req.post(
            f"https://discordapp.com/api/v9/channels/{self.spam_channel}/messages",
            headers=headers,
            files=files,
        )
        print('spam req', x.content)

    def on_open(self, ws: WebSocketApp):
        if self.restart:
            data = {
                "op": 6,
                "d": {
                    "token": self.token,
                    "session_id": self.session_id,
                    "seq": self.last_seq,
                },
            }
        else:
            data = {
                "op": 2,
                "d": {
                    "token": self.token,
                    "intents": 4096,
                    "properties": {
                        "$os": "linux",
                        "$browser": "ubuntu",
                        "$device": "ubuntu",
                    },
                },
            }

        self.restart = True
        self.ws.send(json.dumps(data))

    def send_dm_message(self, channel_id):
        message = """
        Салют!

Вижу ты заинтересован в нашей семье, поэтому расскажу тебе кратко:

Семья состоит в союзе с семьями:
LosZetas, Gidra, Asatryan, Romashki и Hefner.

Особняк у нас под номером 12, если смотреть по карте. 

Функционалом можно в семью попасть имея 5 уровень, если его нет или Вам менее 16 лет - заявку отправлять не нужно.

Фамилию одобрят сменить строго после прохождение испытательного срока, об этом подробнее расскажут, в случае одобрения Вашей заявки. Поэтому не нужно заранее менять фамилию.

Семья расположена полностью в криминальное направление, есть случаи, когда одобряют находится в гос структурах.

Здесь царит порядок и поставлена жесткая дисциплина. Тем самым находится в этой семье приятно. 

Оставляйте свою заявку в Гугл документе, и, с вами свяжутся при первой возможности

https://docs.google.com/forms/d/e/1FAIpQLSe88ZrDxBBZ8PupvHwuz8EkzZZDE1j0_blXhfMKLR2BEXNzQQ/viewform?usp=sf_link

На сообщение отвечать не нужно"""
        headers = {"authorization": self.token, "Content-Type": "application/json"}
        payload = {"content": message, "tts": False}
        x = req.post(
            f"https://discordapp.com/api/v9/channels/{channel_id}/messages",
            headers=headers,
            json=payload,
        )

    def _message_handler(self, message):
        if message["t"] == "MESSAGE_CREATE":
            print("new message reg")
            if message["d"]["author"]["id"] == "979645154308796496":
                return
            author_id = message["d"]["channel_id"]
            self.send_dm_message(author_id)

    def on_message(self, ws: WebSocketApp, message: str) -> None:
        message = json.loads(message)

        if message["op"] == 9:
            print("restart")
            self.restart = True
            self.ws.close()

        self.last_seq = message["s"]

        if not self.session_id and message["t"] == "READY":
            self.session_id = message["d"]["session_id"]

        else:
            self._message_handler(message)

    def restart_connection(self, ws, code, msg) -> None:
        self.restart = True
        self.ws = websocket.WebSocketApp(
            "wss://gateway.discord.gg/",
            on_message=self.on_message,
            on_close=self.restart_connection,
            on_open=self.on_open,
        )

        self.ws.run_forever()

    def create_connection(self) -> None:
        self.ws = websocket.WebSocketApp(
            "wss://gateway.discord.gg/",
            on_message=self.on_message,
            on_close=self.restart_connection,
            on_open=self.on_open,
        )

        self.ws.run_forever()

    def start_scheduler(self):
        self.scheduler.add_job(self.send_spam, "interval", minutes=30)
        print('scheduler set up')
        self.scheduler.start()


conn = DiscordConnection()
conn.create_connection()

