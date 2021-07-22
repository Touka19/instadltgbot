import logging, urllib.request, json, os, shutil
import time

from datetime import datetime
from telegram import Update, ForceReply
from telegram.utils.request import Request
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def user_log(user_id: int):
    return False
    #@TODO Guardar la petición del usuario

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    context.bot.send_message(chat_id=update.effective_chat.id, text='¡Hola! 👋\nCon este bot puedes descargar contenido de Instagram. Simplemente envíame una URL de publicación de Instagram y te la enviaré como archivo para que la puedas guardar.')
    update.message.reply_photo(photo=open('img/start_img.jpg', 'rb'), caption='En Instagram, pulsa el icono de tres puntos (⋮) y elige "Compartir en...", selecciona Telegram y envíamelo. También puedes copiar el enlace y enviármelo manualmente.')
    #@TODO Configuración para que el usuario elija si quiere las fotos como imágenes o como archivos

def echo(update: Update, context: CallbackContext) -> None:
    #@TODO Detección de perfil, post, reel. Cada uno irá a una función distinta
    #Aquí solo se detectará el tipo de URL enviada (y si es o no de Instagram)
    """Echo the user message."""
    url = update.message.text
    logger.info('[USER] \t %s: %s', update.message.from_user.username, url)
    if not url.startswith('https://www.instagram.com/'):
        update.message.reply_text('Esto no es una URL de Instagram... 😕')

    if not url.endswith('/'):
        url = url+'/'

    # Detectamos si la URL es de un post
    if not (url.startswith('https://www.instagram.com/p') or url.startswith('https://www.instagram.com/reel')):
        update.message.reply_text('No hemos podido descargar contenido de esta URL. Revisa que sea correcta o contacta.')
        return

    url = url.split('?', 1)
    url = url[0]
    url = url+'?__a=1'
    req = urllib.request.Request(url, data=None, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
    r = urllib.request.urlopen(req).read()
    cont = json.loads(r.decode('utf-8'))

    content = []


    update.message.reply_text('Descargando...')
    owner = cont['graphql']['shortcode_media']['owner']['username']
    id = cont['graphql']['shortcode_media']['shortcode']
    #Detectamos si es una imagen, un vídeo o una colección
    if cont['graphql']['shortcode_media']['__typename'] == 'GraphImage':
        content.append([cont['graphql']['shortcode_media']['shortcode'], cont['graphql']['shortcode_media']['display_url'], '.jpg'])
    if cont['graphql']['shortcode_media']['__typename'] == 'GraphVideo':
        content.append([cont['graphql']['shortcode_media']['shortcode'], cont['graphql']['shortcode_media']['video_url'], '.mp4'])
    elif cont['graphql']['shortcode_media']['__typename'] == 'GraphSidecar':
        for c in cont['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']:
            if c['node']['__typename'] == 'GraphImage':
                content.append([c['node']['shortcode'], c['node']['display_url'], '.jpg'])
            elif c['node']['__typename'] == 'GraphVideo':
                content.append([c['node']['shortcode'], c['node']['video_url'], '.mp4'])

    #@TODO stories
    #if url.startswith('https://www.instagram.com/stories'):
    #   content = cont['graphql']['shortcode_media']['display_url']

    #Creamos un directorio para la descarga con la ID del chat con el usuario y el timestamp actual
    now = time.time()
    #path = os.path.join(pathlib.Path(__file__).parent.resolve())
    path = str(update.effective_chat.id)+str(now)
    os.mkdir(path)
    if not content:
        update.message.reply_text('No se han podido recuperar fotos ni vídeos de esa publicación 😣')
        return
    update.message.reply_text('¡Ya está! Aquí lo tienes 😋')
    for c in content: #Descargamos los archivos
        urllib.request.urlretrieve(c[1], path + '/' + str(owner + '_' + c[0] + c[2]))
        update.message.reply_document(document=open(path+'/'+str(owner+'_'+c[0]+c[2]), 'rb'))
        logger.info('\x1b[31;1mEnviado el archivo %s al usuario %s', str(owner+'_'+c[0]+c[2]), update.message.from_user.username)

    shutil.rmtree(path)
    return





def main() -> None:
    # Config read
    with open('bot_config.json') as config_json:
        config_data = json.load(config_json)

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config_data['API_key'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()