import pytest
from digitalguide.twilio.TwilioUpdate import TwilioUpdate
from werkzeug.datastructures import CombinedMultiDict, ImmutableMultiDict

def test_message_update():
    response = CombinedMultiDict([ImmutableMultiDict([]), ImmutableMultiDict([('SmsMessageSid', 'SM1cea0a82154a503875f26e1898d972f2'), ('NumMedia', '0'), ('ProfileName', 'Sören'), ('SmsSid', 'SM1cea0a82154a503875f26e1898d972f2'), ('WaId', '4917652163847'), ('SmsStatus', 'received'), ('Body', 'Hi'), ('To', 'whatsapp:+14155238886'), ('NumSegments', '1'), ('MessageSid', 'SM1cea0a82154a503875f26e1898d972f2'), ('AccountSid', 'AC8f3944b5604c359ee4e1c882e64765e2'), ('From', 'whatsapp:+4917652163847'), ('ApiVersion', '2010-04-01')])])
    update =  TwilioUpdate(**response)

def test_image_update():
    response = CombinedMultiDict([ImmutableMultiDict([]), ImmutableMultiDict([('MediaContentType0', 'image/jpeg'), ('SmsMessageSid', 'MM94942a74f3cfc4fceed98eb6ec1ab15b'), ('NumMedia', '1'), ('ProfileName', 'Sören'), ('SmsSid', 'MM94942a74f3cfc4fceed98eb6ec1ab15b'), ('WaId', '4917652163847'), ('SmsStatus', 'received'), ('Body', ''), ('To', 'whatsapp:+14155238886'), ('NumSegments', '1'), ('MessageSid', 'MM94942a74f3cfc4fceed98eb6ec1ab15b'), ('AccountSid', 'AC8f3944b5604c359ee4e1c882e64765e2'), ('From', 'whatsapp:+4917652163847'), ('MediaUrl0', 'https://api.whatsapp.com/2010-04-01/Accounts/AC8f3944b5604c359ee4e1c882e64765e2/Messages/MM94942a74f3cfc4fceed98eb6ec1ab15b/Media/ME1eb56f5a20a667e7f4dc8428c04c1c36'), ('ApiVersion', '2010-04-01')])])
    update =  TwilioUpdate(**response)

def test_venue_update():
    response = CombinedMultiDict([ImmutableMultiDict([]), ImmutableMultiDict([('Latitude', '52.406563'), ('Longitude', '12.969897'), ('SmsMessageSid', 'SM69ee3cde6532bdcedc2c44b83ee53f41'), ('NumMedia', '0'), ('ProfileName', 'Sören'), ('SmsSid', 'SM69ee3cde6532bdcedc2c44b83ee53f41'), ('WaId', '4917652163847'), ('SmsStatus', 'received'), ('Body', ''), ('To', 'whatsapp:+14155238886'), ('NumSegments', '1'), ('MessageSid', 'SM69ee3cde6532bdcedc2c44b83ee53f41'), ('AccountSid', 'AC8f3944b5604c359ee4e1c882e64765e2'), ('From', 'whatsapp:+4917652163847'), ('ApiVersion', '2010-04-01')])])
    update =  TwilioUpdate(**response)