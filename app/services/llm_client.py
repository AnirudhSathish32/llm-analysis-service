import asyncio
import random
import time

class LLMResult:
    def __init__(self, output: dict, tokens: int, cost: float, duration_ms: int):
        self.output = output
        self.tokens = tokens
        self.cost = cost
        self.duration_ms = duration_ms


class LLMClient:
    async def analyze(self, text: str, analysis_type: str, prompt_version: str) -> LLMResult:
        start = time.time()

        # Simulated latency
        await asyncio.sleep(random.uniform(0.2, 0.5))

        output = {
            "analysis_type": analysis_type,
            "content": f"Processed {len(text)} characters"
        }

        duration_ms = int((time.time() - start) * 1000)

        return LLMResult(
            output=output,
            tokens=len(text) // 4,
            cost=0.002,
            duration_ms=duration_ms
        )
