# MQTT Integration

`HomeAgent` includes an MQTT publish helper:

- Broker: `.env` → `MQTT_BROKER`, `MQTT_PORT`
- Publish: `HomeAgent.publish_mqtt(topic, payload)`

Use this for lightweight device control when Home Assistant isn’t the direct control path.

