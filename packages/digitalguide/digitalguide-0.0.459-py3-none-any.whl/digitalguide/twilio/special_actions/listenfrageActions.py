from digitalguide.twilio.TwilioUpdate import TwilioUpdate

def twilio_loop_list(client, update: TwilioUpdate, context,  key, value, doppelte_antwort):
    if not key in context:
        context[key] = []

    if value in context[key]:
        client.messages.create(
            body=doppelte_antwort,
            from_=update.To,
            to=update.From
        )
        return "{}_FRAGE".format(key.upper())
    else:
        context[key].append(value)

def twilio_loop_list_fertig(client, update, context, key, answer_id_list, fertig_antwort):
    if set(answer_id_list).issubset(set(context[key])):
        client.messages.create(
            body=fertig_antwort,
            from_=update.To,
            to=update.From
        )

def twilio_eval_list(client, update: TwilioUpdate, context, answer_id_name_list, poi, response_text):
    if not poi in context:
        context[poi] = []

    response_text += "\n"

    for id, name in answer_id_name_list:
        if id in context[poi]:
            response_text += "✅ {}\n".format(name)
        else:
            response_text += "◽ {}\n".format(name)

    client.messages.create(
        body=response_text,
        from_=update.To,
        to=update.From
    )


twilio_action_functions = {"loop_list": twilio_loop_list,
                             "eval_list": twilio_eval_list,
                             "loop_list_fertig": twilio_loop_list_fertig
                             }
