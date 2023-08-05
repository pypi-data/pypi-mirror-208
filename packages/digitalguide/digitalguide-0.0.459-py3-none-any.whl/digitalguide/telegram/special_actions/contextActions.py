from telegram import (Update)
from telegram.ext import (CallbackContext)

from digitalguide.twilio.TwilioUpdate import TwilioUpdate


def telegram_default_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.from_user.first_name

def telegram_save_text_to_context(update: Update, context: CallbackContext, key):
    context.user_data[key] = update.message.text

def telegram_save_value_to_context(update: Update, context: CallbackContext, key, value):
    context.user_data[key] = value

telegram_action_functions = {"default_name": telegram_default_name,
                             "save_text_to_context": telegram_save_text_to_context,
                             "save_value_to_context": telegram_save_value_to_context
                             }