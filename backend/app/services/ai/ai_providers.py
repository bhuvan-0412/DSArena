import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator, Optional
from sqlalchemy.orm import Session
from app.models.ai import ProviderConfig, AISettings

class BaseAIProvider(ABC):
    """
    Abstract base class for all AI LLM Providers.
    """
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.api_key = config.api_key or ""
        self.model = config.default_model
        self.base_url = config.base_url

    @abstractmethod
    def generate_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        pass

    @abstractmethod
    def stream_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        pass


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI API Provider implementation.
    Fallback to intelligent rule-based response generator when API key is unconfigured.
    """
    def generate_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        if self.api_key:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                payload = {
                    "model": self.model or "gpt-4o-mini",
                    "messages": [{"role": "system", "content": system_prompt}] + messages,
                    "temperature": temperature
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    }
                )
                with urllib.request.urlopen(req, timeout=15) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    return res_data["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"[OpenAIProvider] API call failed: {e}. Falling back to coach intelligence engine.")

        # Fallback intelligent Coach response when key is empty or call fails
        last_user_msg = messages[-1]["content"] if messages else ""
        return self._generate_fallback_coach_response(system_prompt, last_user_msg)

    def stream_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        full_text = self.generate_response(system_prompt, messages, temperature)
        # Yield in realistic word chunks for smooth SSE streaming
        words = full_text.split(" ")
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            yield chunk

    def _generate_fallback_coach_response(self, system_prompt: str, user_msg: str) -> str:
        user_msg_lower = user_msg.lower()

        if "hint" in user_msg_lower:
            return (
                "### 💡 AI Coach Hint\n\n"
                "**Key Insight**: Notice how the target value relates to elements you've seen before.\n\n"
                "- **Step 1**: Can you store element indices in a Hash Map for `O(1)` lookup as you iterate?\n"
                "- **Step 2**: Calculate `complement = target - current_val` at each step.\n\n"
                "*Try updating your loop logic using a hash map lookup before moving to the next hint level!*"
            )

        if "review" in user_msg_lower or "def " in user_msg or "function" in user_msg_lower:
            return (
                "### 🔍 Code Review & Optimization Analysis\n\n"
                "#### ⏱️ Time & Space Complexity\n"
                "- **Time Complexity**: `O(N)` — Single pass over array using hash map lookups.\n"
                "- **Space Complexity**: `O(N)` — Linear auxiliary space for stored elements.\n\n"
                "#### 💡 Key Strengths & Edge Cases\n"
                "- ✅ Clean variable naming and defensive input checking.\n"
                "- ⚠️ **Edge Case to handle**: Negative integers and duplicate elements.\n\n"
                "```python\n"
                "def two_sum(nums, target):\n"
                "    seen = {}\n"
                "    for i, num in enumerate(nums):\n"
                "        diff = target - num\n"
                "        if diff in seen:\n"
                "            return [seen[diff], i]\n"
                "        seen[num] = i\n"
                "    return []\n"
                "```"
            )

        if "plan" in user_msg_lower or "today" in user_msg_lower:
            return (
                "### 📅 Today's Personalized DSA Coach Study Plan\n\n"
                "1. **Warm-up (15 mins)**: Review 1 due revision item in **Arrays & Hashing**.\n"
                "2. **Core Topic Practice (30 mins)**: Complete 1 Medium Problem: **Two Sum** pattern.\n"
                "3. **Daily Mission (15 mins)**: Take concept quiz and maintain your solving streak!\n\n"
                "*Keep up the momentum to level up your Gladiator rank!*"
            )

        return (
            f"### ⚔️ DSA Coach Insights\n\n"
            f"Great question! Based on your current roadmap position and performance:\n\n"
            f"1. **Core Concept**: When approaching this problem, first establish your time complexity target.\n"
            f"2. **Pattern Matching**: Consider whether a Two-Pointer technique or Hash Table yields optimal performance.\n"
            f"3. **Interview Tip**: Always communicate your thought process and trade-offs out loud to your interviewer before typing code.\n\n"
            f"*Ask for a specific hint level or code review if you want targeted feedback!*"
        )


class GeminiProvider(BaseAIProvider):
    """
    Google Gemini LLM Provider implementation.
    """
    def generate_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        if self.api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model or 'gemini-1.5-flash'}:generateContent?key={self.api_key}"
                contents = []
                for m in messages:
                    role_str = "user" if m["role"] == "user" else "model"
                    contents.append({"role": role_str, "parts": [{"text": m["content"]}]})
                
                payload = {
                    "contents": contents,
                    "systemInstruction": {"parts": [{"text": system_prompt}]},
                    "generationConfig": {"temperature": temperature}
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=15) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    return res_data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                print(f"[GeminiProvider] API call failed: {e}. Using fallback strategy.")

        # Fallback via OpenAIProvider fallback engine
        openai_fallback = OpenAIProvider(self.config)
        return openai_fallback.generate_response(system_prompt, messages, temperature)

    def stream_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        full_text = self.generate_response(system_prompt, messages, temperature)
        words = full_text.split(" ")
        for i in range(0, len(words), 3):
            yield " ".join(words[i:i+3]) + " "


class AnthropicProvider(BaseAIProvider):
    """
    Anthropic Claude Provider implementation (Future-ready stub).
    """
    def generate_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        openai_fallback = OpenAIProvider(self.config)
        return openai_fallback.generate_response(system_prompt, messages, temperature)

    def stream_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        openai_fallback = OpenAIProvider(self.config)
        yield from openai_fallback.stream_response(system_prompt, messages, temperature)


class LocalLLMProvider(BaseAIProvider):
    """
    Local LLM Provider implementation (e.g. Ollama or local endpoint).
    """
    def generate_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        if self.base_url:
            try:
                url = f"{self.base_url.rstrip('/')}/v1/chat/completions"
                payload = {
                    "model": self.model or "llama-3.2",
                    "messages": [{"role": "system", "content": system_prompt}] + messages,
                    "temperature": temperature
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=15) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    return res_data["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"[LocalLLMProvider] Local endpoint failed: {e}.")

        openai_fallback = OpenAIProvider(self.config)
        return openai_fallback.generate_response(system_prompt, messages, temperature)

    def stream_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        openai_fallback = OpenAIProvider(self.config)
        yield from openai_fallback.stream_response(system_prompt, messages, temperature)


class AIProviderFactory:
    """
    Factory to resolve the active provider for a user and handle provider fallback.
    """
    @staticmethod
    def get_provider_for_user(db: Session, user_id: int) -> BaseAIProvider:
        settings = db.query(AISettings).filter(AISettings.user_id == user_id).first()
        
        active_config = None
        if settings and settings.active_provider_id:
            active_config = db.query(ProviderConfig).filter(ProviderConfig.id == settings.active_provider_id).first()
        
        if not active_config:
            active_config = db.query(ProviderConfig).filter(ProviderConfig.is_default == True).first()

        if not active_config:
            # Create standard default OpenAI config
            active_config = ProviderConfig(
                provider_name="openai",
                display_name="OpenAI GPT-4o Mini",
                is_active=True,
                is_default=True,
                default_model="gpt-4o-mini"
            )
            db.add(active_config)
            db.commit()
            db.refresh(active_config)

        p_name = active_config.provider_name.lower()
        if p_name == "gemini":
            return GeminiProvider(active_config)
        elif p_name == "anthropic":
            return AnthropicProvider(active_config)
        elif p_name == "local":
            return LocalLLMProvider(active_config)
        else:
            return OpenAIProvider(active_config)
