from thrivve_core.helpers.kafka_producer import Producer
from thrivve_core.helpers.topics import Topics



def send_sms(mobile, message):
    response = dict(
        message=message,
        mobile=mobile
    )
    Producer().send_topic(Topics.SEND_SMS, response)
