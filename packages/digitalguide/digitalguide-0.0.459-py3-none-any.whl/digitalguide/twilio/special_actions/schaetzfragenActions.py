from digitalguide.pattern import JAHRESZAHL_PATTERN, KOMMAZAHL_PATTERN

from digitalguide.twilio.TwilioUpdate import TwilioUpdate
import re
import warnings

def twilio_eval_jahreszahl(client, update: TwilioUpdate, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    echter_wert = int(echter_wert)
    schaetzung = int(re.findall(JAHRESZAHL_PATTERN, update.Body)[0])
    if schaetzung == echter_wert:
        client.messages.create(
            body=richtig_text,
            from_=update.To,
            to=update.From
        )

    differenz = schaetzung - echter_wert
    if differenz == -1:
        client.messages.create(
            body=spaeter_singular_text,
            from_=update.To,
            to=update.From
        )

    elif differenz < -1:
        client.messages.create(
            body=spaeter_plural_text.format(abs(differenz)),
            from_=update.To,
            to=update.From
        )

    elif differenz == 1:
        client.messages.create(
            body=vorher_singular_text,
            from_=update.To,
            to=update.From
        )

    elif differenz > 1:
        client.messages.create(
            body=vorher_plural_text.format(abs(differenz)),
            from_=update.To,
            to=update.From
        )


def twilio_eval_prozentzahl(client, update: TwilioUpdate, context, echter_wert, richtig_text, falsch_text):
    warnings.warn("twilio_eval_prozentzahl is deprecated", DeprecationWarning)
    return twilio_eval_kommazahl(update, context, echter_wert, richtig_text, falsch_text, falsch_text, falsch_text, falsch_text)

def twilio_eval_kommazahl(client, update: TwilioUpdate, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    echter_wert = float(echter_wert)
    match = re.search(
        KOMMAZAHL_PATTERN, update.Body)

    if match:
        if match.group('vorkomma'):
            schaetzung = int(match.group('vorkomma'))
        else:
            schaetzung = 0

        if match.group('nachkomma'):
            schaetzung += float("0."+match.group('nachkomma'))

        if schaetzung == echter_wert:
            client.messages.create(
                body=richtig_text,
                from_=update.To,
                to=update.From
            )

        differenz = schaetzung - echter_wert
        if differenz == -1:
            client.messages.create(
                body=spaeter_singular_text,
                from_=update.To,
                to=update.From
            )

        elif differenz < -1 or (-1 < differenz < 0):
            client.messages.create(
                body=spaeter_plural_text.format(abs(differenz)),
                from_=update.To,
                to=update.From
            )

        elif differenz == 1:
            client.messages.create(
                body=vorher_singular_text,
                from_=update.To,
                to=update.From
            )

        elif differenz > 1 or (0 < differenz < 1):
            client.messages.create(
                body=vorher_plural_text.format(abs(differenz)),
                from_=update.To,
                to=update.From
            )

def twilio_eval_laenge(client, update: TwilioUpdate, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text):
    warnings.warn("twilio_eval_laenge is deprecated", DeprecationWarning)
    return twilio_eval_kommazahl(client, update, context, echter_wert, richtig_text, vorher_singular_text, vorher_plural_text, spaeter_singular_text, spaeter_plural_text)

twilio_action_functions = {"eval_jahreszahl": twilio_eval_jahreszahl,
                             "eval_prozentzahl": twilio_eval_prozentzahl,
                             "eval_kommazahl": twilio_eval_kommazahl,
                             "eval_laenge": twilio_eval_laenge,
                             }
