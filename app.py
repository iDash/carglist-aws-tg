import boto3
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from datetime import datetime, timedelta
import os

# AWS config
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ["LISTINGS_TABLE"])

# Telegram config
TOKEN = os.environ["TELEGRAM_TOKEN"]

bot = telegram.Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)

def get_latest_listings():
    # Your logic to get the latest listings
    pass

#
def star(update, context):
    listing_id = context.args[0]
    table.update_item(
        Key={'id': listing_id},
        UpdateExpression='SET starred = :val',
        ExpressionAttributeValues={':val': True}

    )

def unstar(update, context):
    listing_id = context.args[0]
    table.update_item(
        Key={'id': listing_id},
        UpdateExpression='SET starred = :val',
        ExpressionAttributeValues={':val': False}
    )

def erasedata(update, context):
    if 'consent' in context.args:
        with table.batch_writer() as batch:
            for item in table.scan()['Items']:
                batch.delete_item(Key={'id': item['id']})

def favorite(update, context):
    starred_items = table.scan(
        FilterExpression=Attr('starred').eq(True)
    )['Items']
    for item in starred_items:
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(item))

def schedule_listings():
    listings = get_latest_listings()
    for listing in listings:
        # Add listing to DynamoDB
        table.put_item(Item={
            'id': listing.id,
            'url': listing.url,
            'starred': False
        })
        # Send listing to Telegram
        bot.send_message(chat_id='YOUR_TELEGRAM_CHAT_ID', text=str(listing))

# Schedule task
scheduler = BackgroundScheduler()
scheduler.add_job(schedule_listings, 'interval', hours=6)
scheduler.start()

# Telegram command handlers
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('star', star))
dispatcher.add_handler(CommandHandler('unstar', unstar))
dispatcher.add_handler(CommandHandler('erasedata', erasedata))
dispatcher.add_handler(CommandHandler('favorite', favorite))

updater.start_polling()