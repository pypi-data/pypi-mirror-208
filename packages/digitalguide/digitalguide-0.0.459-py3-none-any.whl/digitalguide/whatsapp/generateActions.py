import requests
import logging
import os
from collections import defaultdict
from digitalguide.whatsapp.WhatsAppUpdate import WhatsAppUpdate
import yaml

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')


def read_action_yaml(filename, action_functions={}, log_user=True, log_interaction=True):
    with open(filename) as file:
        yaml_dict = yaml.load(file, Loader=yaml.FullLoader)

    actions_dict = {}

    for key, value in yaml_dict.items():
        actions_dict[key] = Action(
            value, action_functions=action_functions, log_user=log_user, log_interaction=log_interaction)

    return actions_dict


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def send_interactive_list(self, recipient_id, body_text, button_text, sections, header_text=None, footer_text=None):
    """
    Sends an interactive list message to a WhatsApp user
    Args:
        recipient_id[str]: Phone number of the user with country code wihout +
    check https://github.com/Neurotech-HQ/heyoo#sending-interactive-reply-buttons for an example.
    """
    interactive_dict = {}
    if header_text:
        interactive_dict["header"] = {"type": "text", "text": header_text}
    if footer_text:
        interactive_dict["footer"] = {"text": footer_text}
    if body_text:
        interactive_dict["body"] = {"text": body_text}

    interactive_dict["type"] = "list"
    interactive_dict["action"] = {}
    interactive_dict["action"]["button"] = button_text

    interactive_dict["action"]["sections"] = sections

    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "interactive",
        "interactive": interactive_dict,
    }
    logging.info(f"Sending buttons to {recipient_id}")
    r = requests.post(self.url, headers=self.headers, json=data)
    if r.status_code == 200:
        logging.info(f"Buttons sent to {recipient_id}")
        return r.json()
    logging.info(f"Buttons not sent to {recipient_id}")
    logging.info(f"Status code: {r.status_code}")
    logging.info(f"Response: {r.json()}")
    return r.json()

def send_sticker(client, sticker : str, recipient_id: str, link=True):
    if link:
        data = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "sticker",
            "sticker": {"link": sticker},
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "sticker",
            "sticker": {"id": sticker},
        }
    logging.info(f"Sending sticker to {recipient_id}")
    r = requests.post(client.url, headers=client.headers, json=data)
    if r.status_code == 200:
        logging.info(f"Sticker sent to {recipient_id}")
        return r.json()
    logging.info(f"Sticker not sent to {recipient_id}")
    logging.info(f"Status code: {r.status_code}")
    logging.error(f"Response: {r.json()}")
    return r.json()


class Action():
    def __init__(self, actions, action_functions={}, log_user=True, log_interaction=True):
        self.actions = actions
        self.action_functions = action_functions
        self.log_user = log_user
        self.log_interaction = log_interaction
        if log_user or log_interaction:
            import mongoengine
            dbname = config["bot"]["bot_name"]
            if os.getenv('DATABASE_CERT', None):
                # This can be remove in the future
                with open("ca-certificate.crt", "w") as text_file:
                    text_file.write(os.getenv('DATABASE_CERT'))
                mongoengine.connect(alias=dbname, host="mongodb+srv://" + os.getenv("DATABASE_USERNAME")+":" + os.getenv("DATABASE_PASSWORD") +
                                    "@" + os.getenv("DATABASE_HOST") + "/"+dbname+"?authSource=admin&tls=true&tlsCAFile=ca-certificate.crt")
            else:
                mongoengine.connect(alias=dbname, host=os.getenv("DATABASE_URL"))

    def __call__(self, client, update: WhatsAppUpdate, context):
        if self.log_user and not ("user_id" in context.keys()):
            from digitalguide.whatsapp.db_objects import WhatsAppUser
            db_user = WhatsAppUser(ProfileName=update.entry[0].changes[0].value.contacts[0].profile_name,
                                   WaId=update.get_from())
            db_user.save()
            context["user_id"] = db_user

        if self.log_interaction:
            from digitalguide.whatsapp.db_objects import WhatsAppInteraction

            WhatsAppInteraction(user=context["user_id"],
                                ProfileName=update.entry[0].changes[0].value.contacts[0].profile_name,
                                WaId=update.get_from(),
                                text=update.get_message_text(),
                                ).save()

        for item in self.actions:
            if item["type"] == "return":
                return item["state"]

            elif item["type"] == "message":
                placeholder_dict = {**context}
                placeholder_dict["profile_name"] = update.entry[0].changes[0].value.contacts[0].profile_name
                placeholder_dict["echo"] = update.get_message_text()

                if "reply_buttons" in item.keys():
                    buttons = []

                    for button in item["reply_buttons"]:
                        buttons.append({
                            "type": "reply",
                            "reply": {
                                "id": button["id"],
                                "title": button["text"]
                            }
                        })

                    button_dict = {
                        "type": "button",
                                "body": {
                                    "text": item["text"].format(**placeholder_dict)
                                },
                        "action": {
                                    "buttons": buttons
                                }
                    }

                    if "footer" in item.keys():
                        button_dict["footer"] = {"text": item["footer"]}

                    client.send_reply_button(recipient_id=update.get_from(),
                                             button=button_dict)

                elif "button" in item.keys() and "section_title" in item.keys():
                    section_dict = [
                        {
                            "title": item["section_title"],
                            "rows": [],
                        }
                    ]

                    for row in item["rows"]:
                        row_dict = {"id": row["id"],
                                    "title": row["title"],
                                    "description": row.get("description", "")}
                        section_dict[0]["rows"].append(
                            row_dict)

                    send_interactive_list(client,
                                          recipient_id=update.get_from(),
                                          body_text=item["text"].format(
                                              **placeholder_dict),
                                          button_text=item["button"],
                                          sections=section_dict,
                                          header_text=item.get("header", None),
                                          footer_text=item.get("footer", None))

                else:
                    client.send_message(item["text"].format(
                        **placeholder_dict), update.get_from())

            elif item["type"] == "venue":
                client.send_location(
                    name=item["title"],
                    lat=item["latitude"],
                    long=item["longitude"],
                    address=item["address"],
                    recipient_id=update.get_from()
                )
            elif item["type"] == "photo":
                print("ITEM: ", item)
                if "url" in item.keys():
                    client.send_image(
                        item["url"],
                        update.get_from()
                    )
                else:
                    client.send_image(
                        item["id"],
                        update.get_from(),
                        link=False
                    )
            elif item["type"] == "video":
                client.send_video(
                    item["url"],
                    update.get_from()
                )
            elif item["type"] == "sticker":
                send_sticker(client,
                    item["url"],
                    update.get_from()
                )
            elif item["type"] == "media_group":
                pass
                # message = client.messages.create(
                #    media_url=item["urls"],
                #    from_=update.To,
                #    to=update.From
                # )
            elif item["type"] == "audio" or item["type"] == "voice":
                if "url" in item.keys():
                    client.send_audio(
                        item["url"],
                        update.get_from()
                    )
                else:
                    client.send_audio(
                        item["id"],
                        update.get_from(),
                        link=False
                    )
            elif item["type"] == "poll":
                message = item["question"] + "\n"
                for option in item["options"]:
                    message += option + "\n"
                client.send_message(message, update.get_from())

            elif item["type"] == "function":
                arguments = {i: item[i]
                             for i in item if i != 'type' and i != 'func'}
                self.action_functions[item["func"]](
                    client, update, context, **arguments)
