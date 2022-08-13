from telethon import TelegramClient, events, sync
import config

api_id = config.telegram['id']
api_hash = config.telegram['hash']
bot_token = config.telegram['bot_token']
chat_id = config.telegram['chat_id']

client = TelegramClient('cashconverters', api_id, api_hash).start(bot_token=bot_token)
client.start()

def send_message(message,url):
    client.send_message(chat_id, '**'+message+'** '+url, link_preview=False)

def send_image(thumb):
    client.send_file(chat_id, thumb)

if __name__ == "__main__":
    send_image("https://images.cashconverters.es/productslive/thermomix/vorwerk-tm31_CC066_E336418-0_0.jpg")
    send_message("Thermomix Vorwerk Tm31 287,95€","https://www.cashconverters.es/es/es/segunda-mano/thermomix-vorwerk-tm31/CC066_E336418_0.html")