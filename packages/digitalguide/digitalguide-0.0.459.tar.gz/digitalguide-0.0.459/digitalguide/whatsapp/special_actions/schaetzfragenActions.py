from digitalguide.pattern import JAHRESZAHL_PATTERN, KOMMAZAHL_PATTERN

from digitalguide.whatsapp.WhatsAppUpdate import WhatsAppUpdate
import re
import warnings

def whatsapp_eval_jahreszahl(client, update: WhatsAppUpdate, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    echter_wert = int(echter_wert)
    schaetzung = int(re.findall(JAHRESZAHL_PATTERN, update.get_message_text())[0])
    if schaetzung == echter_wert:
        client.send_message(richtig_text, update.get_from())

    differenz = schaetzung - echter_wert
    if differenz == -1:
        client.send_message(spaeter_singular_text, update.get_from())

    elif differenz < -1:
        client.send_message(spaeter_plural_text.format(abs(differenz)), update.get_from())

    elif differenz == 1:
        client.send_message(vorher_singular_text, update.get_from())

    elif differenz > 1:
        client.send_message(vorher_plural_text.format(abs(differenz)), update.get_from())



def whatsapp_eval_prozentzahl(client, update: WhatsAppUpdate, context, echter_wert, richtig_text, falsch_text):
    warnings.warn("twilio_eval_prozentzahl is deprecated", DeprecationWarning)
    return whatsapp_eval_kommazahl(update, context, echter_wert, richtig_text, falsch_text, falsch_text, falsch_text, falsch_text)


def whatsapp_eval_kommazahl(client, update: WhatsAppUpdate, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    echter_wert = float(echter_wert)
    match = re.search(
        KOMMAZAHL_PATTERN, update.get_message_text())

    if match:
        if match.group('vorkomma'):
            schaetzung = int(match.group('vorkomma'))
        else:
            schaetzung = 0

        if match.group('nachkomma'):
            schaetzung += float("0."+match.group('nachkomma'))

        if schaetzung == echter_wert:
            client.send_message(richtig_text, update.get_from())

        differenz = schaetzung - echter_wert
        if differenz == -1:
            client.send_message(spaeter_singular_text, update.get_from())

        elif differenz < -1 or (-1 < differenz < 0):
            client.send_message(spaeter_plural_text.format(abs(differenz)), update.get_from())

        elif differenz == 1:
            client.send_message(vorher_singular_text, update.get_from())

        elif differenz > 1 or (0 < differenz < 1):
            client.send_message(vorher_plural_text.format(abs(differenz)), update.get_from())

def whatsapp_eval_laenge(client, update: WhatsAppUpdate, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    warnings.warn("twilio_eval_laenge is deprecated", DeprecationWarning)
    return whatsapp_eval_kommazahl(client, update, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text)

whatsapp_action_functions = {"eval_jahreszahl": whatsapp_eval_jahreszahl,
                             "eval_prozentzahl": whatsapp_eval_prozentzahl,
                             "eval_kommazahl": whatsapp_eval_kommazahl,
                             "eval_laenge": whatsapp_eval_laenge,
                             }
