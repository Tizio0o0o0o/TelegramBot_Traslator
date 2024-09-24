import logging
import configparser
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from googletrans import Translator

# Configura il logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Inizializza il traduttore
translator = Translator()

# Funzione per gestire i messaggi
def handle_message(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    chat_id = update.message.chat_id
    message_id = update.message.message_id

    # Rileva la lingua del messaggio
    detected_lang = translator.detect(message).lang

    # Traduci il messaggio in base alla lingua rilevata
    if detected_lang == 'fr':
        translated_text = translator.translate(message, dest='it').text
        response = f"Italiano:\n{translated_text}"
    elif detected_lang == 'it':
        translated_text = translator.translate(message, dest='fr').text
        response = f"Français:\n{translated_text}"
    elif detected_lang == 'en':
        translated_text_fr = translator.translate(message, dest='fr').text
        translated_text_it = translator.translate(message, dest='it').text
        response = f"Italiano:\n{translated_text_it}\n\nFrançais:\n{translated_text_fr}"
    else:
        response = "Language not supported for translation."

    # Rispondi al messaggio con la traduzione
    context.bot.send_message(chat_id=chat_id, text=response, reply_to_message_id=message_id)

def main() -> None:
    # Leggi il token dal file config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')
    token = config['telegram']['token']

    # Crea l'updater e il dispatcher
    updater = Updater(token)

    dispatcher = updater.dispatcher

    # Aggiungi un handler per i messaggi
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Avvia il bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()