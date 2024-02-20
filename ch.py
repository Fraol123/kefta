from telegram.ext import Updater

updater = Updater(token='6776764805:AAHYBhmXIjqP-ixR_20K8cKEvwqjFjgMXFg', use_context=True)
updater.bot.delete_webhook()
