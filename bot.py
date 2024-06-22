import logging
from telegram.ext import Updater, CommandHandler, MessageHandler
import requests
from bs4 import BeautifulSoup
import clickfly

logging.basicConfig(level=logging.INFO)

TOKEN = '7281444672:AAFWvju0iapnOKpSjsCyDvIe6d6_-V5gRfk'  # replace with your bot token
CLICKFLY_API_KEY = '03f543783354959d96cf3fce5b67c620231394eb'  # replace with your ClickFly API key

clickfly.set_api_key(CLICKFLY_API_KEY)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Welcome to Movie Downloader!')

def search_movie(update, context):
    query = update.message.text
    url = f'https://mkvcinemas.com/search/{query}'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        movie_list = soup.find_all('div', class_='movie-list-item')
        if movie_list:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Found {} movies:\n'.format(len(movie_list)))
            for movie in movie_list:
                title = movie.find('h2', class_='movie-title').text.strip()
                download_links = []
                quality_links = movie.find_all('a', class_='download-link')
                for link in quality_links:
                    quality = link.get_text().strip()
                    download_link = link.get('href')
                    shortened_link = clickfly.shorten(download_link)
                    download_links.append((quality, shortened_link))
                context.bot.send_message(chat_id=update.effective_chat.id, text=title + '\n')
                for quality, shortened_link in download_links:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f'{quality}: {shortened_link}')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='No movies found.')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Error: Could not retrieve movie list.')

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, search_movie))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()