class WhatsAppUpdate:

    def __init__(self, object, entry) -> None:
        self.object = object
        self.entry = [WhatsAppEntry(**e) for e in entry]

    def get_from(self):
        return self.entry[0].changes[0].value.contacts[0].wa_id

    def get_message(self):
        return self.entry[0].changes[0].value.messages[0]

    def get_message_text(self):
        message = self.entry[0].changes[0].value.messages[0]
        if message._type == "text":
            return message.text
        elif message._type == "interactive":
            if message.interactive["type"] == "button_reply":
                print("Interactive Message Text: {}".format(
                    message.interactive["button_reply"]["title"]))
                return message.interactive["button_reply"]["title"]
            elif message.interactive["type"] == "list_reply":
                if "description" in message.interactive["list_reply"]:
                    print("Interactive Message List: {}{}".format(
                        message.interactive["list_reply"]["title"], message.interactive["list_reply"]["description"]))
                    return "{} {}".format(message.interactive["list_reply"]["title"], message.interactive["list_reply"]["description"])
                else:
                    print("Interactive Message List: {}".format(
                        message.interactive["list_reply"]["title"]))
                    return "{}".format(message.interactive["list_reply"]["title"])
            else:
                print("There is no message text defined for this interactive type: {}".format(
                    message.interactive["type"]))
                return ""
        else:
            print("There is no message text defined for this message type: {}".format(
                message._type))

    def get_delivery(self):
        if self.entry[0].changes[0].value.statuses:
            return self.entry[0].changes[0].value.statuses[0].status


class WhatsAppEntry:
    def __init__(self, id, changes) -> None:
        self.id = id
        self.changes = [WhatsAppChange(**change) for change in changes]


class WhatsAppChange:
    def __init__(self, value, field):
        self.value = WhatsAppValue(**value)
        self.field = field


class WhatsAppValue:
    def __init__(self, metadata, contacts=[], messaging_product="whatsapp", messages=[], statuses=[]):
        self.contacts = [WhatsAppContact(**contact) for contact in contacts]
        self.messaging_product = messaging_product
        messages_list = []
        for message in messages:
            message["_from"] = message["from"]
            del message["from"]
            messages_list.append(message)
        self.messages = [WhatsAppMessage(**message)
                         for message in messages_list]
        self.metadata = WhatsAppMetadata(**metadata)
        self.statuses = [WhatsAppStatus(**status) for status in statuses]


class WhatsAppContact:
    def __init__(self, wa_id, profile) -> None:
        self.wa_id = wa_id
        self.profile_name = profile["name"]


class WhatsAppError:
    def __init__(self, code, title, href="") -> None:
        self.code = code
        self.title = title
        self.href = href


class WhatsAppMessage:
    def __init__(self, _from, id, timestamp, type, audio=None, button=None, context=None, document=None, errors=None, identity=None, image=None, interactive=None, order=None, referral=None, sticker=None, system=None, text=None, video=None) -> None:
        if type == "audio":
            self.audio = WhatsAppAudio(**audio)
        elif type == "button":
            self.button = WhatsAppButton(**button)
        elif type == "text":
            self.text = text["body"]
        self.context = context
        self.document = document
        self.errors = errors
        self._from = _from
        self.id = id
        self.identity = identity
        self.image = image
        self.interactive = interactive
        self.order = order
        self.referral = referral
        self.sticker = sticker
        self.system = system
        self.timestamp = timestamp
        self._type = type
        self.video = video


class WhatsAppAudio:
    def __init__(self, id, mime_type) -> None:
        self.id = id
        self.mime_type = mime_type


class WhatsAppButton:
    def __init__(self, payload, text) -> None:
        self.payload = payload
        self.text = text


class WhatsAppMetadata:
    def __init__(self, display_phone_number, phone_number_id) -> None:
        self.display_phone_number = display_phone_number
        self.phone_number_id = phone_number_id


class WhatsAppStatus:
    def __init__(self, id, recipient_id, status, timestamp, errors=[], conversation=None, pricing=None) -> None:
        if conversation:
            self.conversation = WhatsAppConversation(**conversation)
        self.id = id
        if pricing:
            self.pricing_category = pricing["category"]
            self.pricing_model = pricing["pricing_model"]
        self.errors = [WhatsAppError(**error) for error in errors]
        self.recipient_id = recipient_id
        self.status = status
        self.timestamp = timestamp


class WhatsAppConversation:
    def __init__(self, id, origin, expiration_timestamp=None) -> None:
        self.id = id
        self.origin_type = origin["type"]
        if expiration_timestamp:
            self.expiration_timestamp = expiration_timestamp
