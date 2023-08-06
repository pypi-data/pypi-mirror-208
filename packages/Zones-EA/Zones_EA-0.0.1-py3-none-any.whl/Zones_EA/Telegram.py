import urllib3


class TelegramBot:
    def __init__(self, token):
        self.TypingText = None
        self.updater = self.Updater(token)

        self.actions = {
            "start": self.start,
            "stop": self.stop,
            "run": self.run,
            "SendMessage": self.send_message,
            "SendPhoto": self.send_photo,
            "SendAudio": self.send_audio,
            "SendDocument": self.send_document,
            "SendVideo": self.send_video,
            "SendVoice": self.send_voice,
            "SendVideoNote": self.SendVideoNote,
            "SendLocation": self.SendLocation,
            "SendVenue": self.SendVenue,
            "SendContact": self.SendContact,
            "SendChatAction": self.SendChatAction,
            "Typing": self.TypingText,

        }

    def start(self):
        self.updater.start_polling()

    def stop(self):
        self.updater.stop()

    def run(self):
        self.start()
        self.updater.idle()
        self.stop()

    def send_message(self, chat_id, message):
        self.updater.bot.send_message(chat_id=chat_id, text=message)

    def send_photo(self, chat_id, photo):
        self.updater.bot.send_photo(chat_id=chat_id, photo=photo)

    def send_audio(self, chat_id, audio):
        self.updater.bot.send_audio(chat_id=chat_id, audio=audio)

    def send_document(self, chat_id, document):
        self.updater.bot.send_document(chat_id=chat_id, document=document)

    def send_video(self, chat_id, video):
        self.updater.bot.send_video(chat_id=chat_id, video=video)

    def send_voice(self, chat_id, voice):
        self.updater.bot.send_voice(chat_id=chat_id, voice=voice)

    def SendVideoNote(self, chat_id, video_note):
        self.updater.bot.send_video_note(chat_id=chat_id, video_note=video_note)

    def SendLocation(self, chat_id, location):
        self.updater.bot.send_location(chat_id=chat_id, location=location)

    def SendVenue(self, chat_id, venue):
        self.updater.bot.send_venue(chat_id=chat_id, venue=venue)

    def SendContact(self, chat_id, contact):
        self.updater.bot.send_contact(chat_id=chat_id, contact=contact)

    def SendChatAction(self, chat_id, action):
        self.updater.bot.send_chat_action(chat_id=chat_id, action=action)

    def getMe(self, token):
        http = urllib3.PoolManager()
        return http.connection_from_url('https://api.telegram.org/bot' + token + '/getMe')

    def Updater(self, token):
        # Making bot http request

        http = urllib3.PoolManager()
        return http.connection_from_url('https://api.telegram.org/bot' + token + '/getUpdates')
