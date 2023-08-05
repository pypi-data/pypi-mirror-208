from digitalguide.twilio.TwilioUpdate import TwilioUpdate

def twilio_default_name(client, update: TwilioUpdate, context):
    context["name"] = update.ProfileName

def twilio_save_text_to_context(client, update: TwilioUpdate, context, key):
    context[key] = update.Body

def twilio_save_value_to_context(client, update: TwilioUpdate, context, key, value):
    context[key] = value

twilio_action_functions = {"default_name": twilio_default_name,
                             "save_text_to_context": twilio_save_text_to_context,
                             "save_value_to_context": twilio_save_value_to_context
                             }
