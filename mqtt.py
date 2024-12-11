import paho.mqtt.client as mqtt
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.connections.mqtt import MQTTClient
from app.config import settings
from app.controllers.mqtt import scoreboard

scheduler = BackgroundScheduler()

contest_id = 1

sc_intervals = {}
sc_intervals['scoreboard'] = IntervalTrigger(seconds=5)

def main():
    mqtt_client = MQTTClient("ByteBlitz", settings.MQTT_HOST, settings.MQTT_PORT, settings.MQTT_USER, settings.MQTT_PASS)
    mqtt_client.connect()
    mqtt_client.start()

    scheduler.add_job(
        func=scoreboard,
        trigger=sc_intervals['scoreboard'],
        id='scoreboard',
        replace_existing=True,
        args=(mqtt_client, contest_id)
    )

    scheduler.start()


    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        mqtt_client.stop()

if __name__ == '__main__':
    main()