from thrivve_core.helpers.kafka_producer import Producer


def send_topic(topic, datajson, kafka_configs=None):
    if kafka_configs is None:
        kafka_configs = {}

    kafka_configs.update(
        producer_version=2
    )
    Producer().send_topic(topic=topic, datajson=datajson, **kafka_configs)
