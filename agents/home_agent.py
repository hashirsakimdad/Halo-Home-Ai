"""Home agent — IoT and smart home control via Home Assistant and MQTT."""

import logging

import httpx
import paho.mqtt.client as mqtt

from agents.base_agent import BaseAgent
from config.settings import (
    HOME_ASSISTANT_TOKEN,
    HOME_ASSISTANT_URL,
    MQTT_BROKER,
    MQTT_PORT,
)

logger = logging.getLogger(__name__)


class HomeAgent(BaseAgent):
    """Controls lights, switches, and other IoT devices."""

    def __init__(self):
        """Initialize home agent."""
        super().__init__("HomeAgent")

    HOME_SYSTEM = (
        "You are HoloHome's smart home controller. Parse device control requests "
        "and confirm actions clearly. Mention device names when responding."
    )

    async def run(self, task: str, context: dict) -> str:
        """Handle smart home control requests."""
        system = context.get("system_prompt", self.HOME_SYSTEM)
        stored = await self.recall("home devices")
        prompt = task
        if stored:
            prompt = f"Known devices:\n{stored}\n\nUser request: {task}"

        response = await self.llm.holohome_chat(prompt, extra_system=system)
        await self.remember("home", f"{task} -> {response}")
        return response

    async def call_service(self, domain: str, service: str, entity_id: str) -> bool:
        """Call a Home Assistant service for a given entity."""
        if not HOME_ASSISTANT_TOKEN:
            logger.warning("HOME_ASSISTANT_TOKEN not set — skipping HA call")
            return False
        url = f"{HOME_ASSISTANT_URL.rstrip('/')}/api/services/{domain}/{service}"
        headers = {"Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}"}
        payload = {"entity_id": entity_id}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return True
        except httpx.HTTPError as exc:
            logger.error("Home Assistant call failed: %s", exc)
            return False

    async def publish_mqtt(self, topic: str, payload: str) -> bool:
        """Publish an MQTT message to control devices."""
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.publish(topic, payload)
            client.disconnect()
            return True
        except Exception as exc:
            logger.error("MQTT publish failed: %s", exc)
            return False
