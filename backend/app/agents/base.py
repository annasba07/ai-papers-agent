"""
Base Agent Classes

Implements core agent functionality with:
- Standardized communication protocol
- Reflection capabilities (Reflexion pattern)
- Memory integration
- Multi-provider LLM support (Claude, GPT-4, Gemini)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
from app.utils.logger import LoggerMixin
from app.agents.memory import TemporalMemory
from app.agents.config import AgentConfig
from app.agents.llm_providers import get_llm_provider, BaseLLMProvider


class BaseAgent(LoggerMixin, ABC):
    """
    Base class for all agents

    Implements:
    - Standard communication interface
    - Reflection capabilities
    - Memory integration
    - Error handling and retries
    - Multi-provider LLM support
    """

    def __init__(
        self,
        name: str,
        role: str,
        config: AgentConfig,
        memory: Optional[TemporalMemory] = None
    ):
        self.name = name
        self.role = role
        self.config = config
        self.memory = memory

        # Initialize LLM provider using factory
        self.llm: BaseLLMProvider = get_llm_provider(
            provider=config.llm_provider,
            model=config.llm_model
        )

        self.log_info(
            f"Initialized {name} agent with {self.llm.provider_name} "
            f"({self.llm.get_model_name()})"
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using LLM with retry logic (multi-provider support)"""

        for attempt in range(self.config.max_retries):
            try:
                messages = [{"role": "user", "content": prompt}]

                # Use the provider abstraction
                response = await self.llm.generate(
                    messages=messages,
                    system_prompt=system_prompt or self._get_system_prompt(),
                    temperature=temperature or self.config.temperature,
                    max_tokens=max_tokens or self.config.max_tokens
                )

                # Extract text from standardized response
                text = response.text

                self.log_debug(
                    f"Generated {len(text)} chars",
                    tokens=response.input_tokens + response.output_tokens
                )

                return text

            except Exception as e:
                self.log_error(
                    f"Generation failed (attempt {attempt + 1}/{self.config.max_retries})",
                    error=e
                )

                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    raise

    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the agent's primary task"""
        pass

    async def reflect(
        self,
        task: str,
        result: Dict[str, Any],
        outcome: str  # "success" or "failure"
    ) -> Optional[str]:
        """
        Reflect on task outcome for future learning (Reflexion pattern)

        Args:
            task: Description of what was attempted
            result: The result data
            outcome: Whether it was successful

        Returns:
            Reflection text to store in memory
        """
        if outcome == "success":
            # Light reflection on success
            reflection_prompt = f"""You just successfully completed this task:
            {task}

            Result summary: {result.get('summary', 'N/A')}

            Briefly reflect (2-3 sentences):
            1. What approach worked well?
            2. What pattern should you remember for similar tasks?

            Be concise and actionable.
            """
        else:
            # Deep reflection on failure
            reflection_prompt = f"""You failed at this task:
            {task}

            Error: {result.get('error', 'Unknown')}

            Deeply reflect (4-5 sentences):
            1. What did you misunderstand?
            2. What assumptions were wrong?
            3. What should you check next time?
            4. What specific approach would work better?

            Be specific and actionable for your future self.
            """

        try:
            reflection = await self.generate(
                reflection_prompt,
                system_prompt=f"You are {self.name}, reflecting on your work to improve.",
                temperature=0.7
            )

            # Store in memory
            if self.memory:
                await self.memory.add_reflection(
                    agent=self.name,
                    reflection=reflection,
                    task_type=task.split()[0],  # Extract task type
                    context={
                        "outcome": outcome,
                        "task": task,
                        "result_summary": str(result.get('summary', ''))[:200]
                    }
                )

            self.log_info(f"Reflection stored for {outcome}")
            return reflection

        except Exception as e:
            self.log_error("Failed to generate reflection", error=e)
            return None

    async def get_past_learnings(
        self,
        task_type: str,
        max_results: int = 3
    ) -> str:
        """Retrieve past reflections for this type of task"""
        if not self.memory:
            return "No past learnings available."

        reflections = await self.memory.get_reflections(
            agent=self.name,
            task_type=task_type,
            max_age_days=30,
            max_results=max_results
        )

        if not reflections:
            return "No past learnings available."

        # Format reflections
        learnings = []
        for i, r in enumerate(reflections, 1):
            age_days = r.get('age_days', 0)
            learnings.append(
                f"{i}. ({age_days} days ago): {r['reflection']}"
            )

        return "\n".join(learnings)


class AgentMessage:
    """
    Standard message format for agent communication
    Based on Agent Communication Protocol (ACP) principles
    """

    def __init__(
        self,
        sender: str,
        receiver: str,
        message_type: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = asyncio.get_event_loop().time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class AgentCommunicationBus:
    """
    Simple communication bus for agent-to-agent messaging
    Implements basic pub/sub pattern
    """

    def __init__(self):
        self.messages: List[AgentMessage] = []
        self.subscribers: Dict[str, List[callable]] = {}

    async def send(self, message: AgentMessage):
        """Send a message"""
        self.messages.append(message)

        # Notify subscribers
        if message.receiver in self.subscribers:
            for callback in self.subscribers[message.receiver]:
                await callback(message)

    def subscribe(self, agent_name: str, callback: callable):
        """Subscribe to messages for an agent"""
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(callback)

    def get_conversation_history(
        self,
        agent1: str,
        agent2: str,
        limit: int = 10
    ) -> List[AgentMessage]:
        """Get conversation history between two agents"""
        relevant = [
            m for m in self.messages
            if (m.sender == agent1 and m.receiver == agent2)
            or (m.sender == agent2 and m.receiver == agent1)
        ]
        return relevant[-limit:]
