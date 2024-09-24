import logging
import configparser
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from googletrans import Translator
import speech_recognition as sr
from pydub import AudioSegment
import os

# Configura il logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Inizializza il traduttore
translator = Translator()
recognizer = sr.Recognizer()

# Funzione per gestire i messaggi di testo
def handle_text_message(update: Update, context: CallbackContext) -> None:
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

# Funzione per gestire i messaggi vocali
def handle_voice_message(update: Update, context: CallbackContext) -> None:
    voice = update.message.voice
    chat_id = update.message.chat_id
    message_id = update.message.message_id

    # Scarica il file audio
    file = context.bot.get_file(voice.file_id)
    file_path = f"voice_{voice.file_id}.ogg"
    file.download(file_path)

    # Converti il file audio in formato WAV
    audio = AudioSegment.from_ogg(file_path)
    wav_path = f"voice_{voice.file_id}.wav"
    audio.export(wav_path, format="wav")

    # Trascrivi l'audio
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            detected_lang = translator.detect(text).lang

            # Traduci il testo trascritto
            if detected_lang == 'fr':
                translated_text = translator.translate(text, dest='it').text
                response = f"Trascrizione:\n{text}\n\nItaliano:\n{translated_text}"
            elif detected_lang == 'it':
                translated_text = translator.translate(text, dest='fr').text
                response = f"Trascrizione:\n{text}\n\nFrançais:\n{translated_text}"
            elif detected_lang == 'en':
                translated_text_fr = translator.translate(text, dest='fr').text
                translated_text_it = translator.translate(text, dest='it').text
                response = f"Trascrizione:\n{text}\n\nItaliano:\n{translated_text_it}\n\nFrançais:\n{translated_text_fr}"
            else:
                response = "Lingua non supportata per la traduzione."

            # Rispondi al messaggio con la trascrizione e la traduzione
            context.bot.send_message(chat_id=chat_id, text=response, reply_to_message_id=message_id)
        except sr.UnknownValueError:
            context.bot.send_message(chat_id=chat_id, text="Non sono riuscito a capire l'audio.", reply_to_message_id=message_id)
        except sr.RequestError as e:
            context.bot.send_message(chat_id=chat_id, text=f"Errore nel servizio di riconoscimento vocale: {e}", reply_to_message_id=message_id)

    # Rimuovi i file temporanei
    os.remove(file_path)
    os.remove(wav_path)

def main() -> None:
    # Leggi il token dal file config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')
    token = config['telegram']['token']

    # Crea l'updater e il dispatcher
    updater = Updater(token, allowed_updates=['message', 'voice'])
    dispatcher = updater.dispatcher

    # Aggiungi un handler per i messaggi di testo
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text_message))

    # Aggiungi un handler per i messaggi vocali
    dispatcher.add_handler(MessageHandler(Filters.voice, handle_voice_message))

    # Avvia il bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()