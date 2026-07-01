# Specialist Agents

All agents inherit from `agents/base_agent.py` and implement:

- `async def run(self, task: str, context: dict) -> str`

## Current agents

- `VoiceAgent`: conversational responses + STT/TTS helpers
- `HomeAgent`: smart home reasoning + HA/MQTT helpers
- `EducationAgent`: tutoring and explanations (Urdu/English)
- `ScheduleAgent`: reminders, calendar-style interactions
- `InteriorAgent`: design suggestions
- `SecurityAgent`: safety and monitoring responses

