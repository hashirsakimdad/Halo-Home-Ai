"""Home agent — IoT and smart home control via Home Assistant and MQTT."""

import json
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

COMMAND_EXTRACTION_PROMPT = (
    "You are a smart home command parser. Given a user request, extract the device action as JSON.\n"
    'If the request is NOT a device control command (just a question about devices), return: {{"action": "none"}}\n\n'
    "For device control, return ONE of:\n"
    '{{"action": "ha_service", "domain": "<domain>", "service": "<service>", "entity_id": "<entity_id>"}}\n'
    '{{"action": "mqtt", "topic": "<topic>", "payload": "<payload>"}}\n\n'
    "Common mappings:\n"
    '- "turn on the lights" -> {{"action": "ha_service", "domain": "light", "service": "turn_on", "entity_id": "light.living_room"}}\n'
    '- "turn off the fan" -> {{"action": "ha_service", "domain": "switch", "service": "turn_off", "entity_id": "switch.fan"}}\n'
    '- "set thermostat to 22" -> {{"action": "ha_service", "domain": "climate", "service": "set_temperature", "entity_id": "climate.thermostat"}}\n\n'
    "User request: {task}\n\n"
    "JSON:"
)


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
        """Handle smart home control requests, executing device commands when possible."""
        system = context.get("system_prompt", self.HOME_SYSTEM)
        history = context.get("history")
        stored = await self.recall("home devices")

        command = await self._extract_command(task)
        action_result = await self._execute_command(command)

        prompt = task
        if stored:
            prompt = f"Known devices:\n{stored}\n\nUser request: {task}"
        if action_result:
            prompt += f"\n\n[Device action result: {action_result}]"

        response = await self.llm.holohome_chat(prompt, extra_system=system, history=history)
        await self.remember("home", f"{task} -> {response}")
        return response

    async def _extract_command(self, task: str) -> dict:
        """Use the LLM to parse a user request into a device command."""
        try:
            raw = await self.llm.chat(COMMAND_EXTRACTION_PROMPT.format(task=task))
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(raw[start:end])
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("Command extraction failed: %s", exc)
        return {"action": "none"}

    async def _execute_command(self, command: dict) -> str | None:
        """Execute an extracted device command and return a status string."""
        action = command.get("action", "none")

        if action == "ha_service":
            domain = command.get("domain", "")
            service = command.get("service", "")
            entity_id = command.get("entity_id", "")
            if domain and service and entity_id:
                ok = await self.call_service(domain, service, entity_id)
                return f"Home Assistant {domain}.{service} on {entity_id}: {'success' if ok else 'failed'}"

        if action == "mqtt":
            topic = command.get("topic", "")
            payload = command.get("payload", "")
            if topic:
                ok = await self.publish_mqtt(topic, payload)
                return f"MQTT publish to {topic}: {'success' if ok else 'failed'}"

        return None

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
