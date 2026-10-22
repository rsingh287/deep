"""
Enterprise LLM Gateway & Cost Autopilot Module
Provides rate limiting, fallback cascades, intelligent model routing, and cost accounting.
"""

import threading
import time


class EnterpriseLLMGateway:
    def __init__(self):
        self.lock = threading.Lock()
        self.request_timestamps = []
        self.rate_limit_max_per_minute = 120

        # Model cost estimates per 1,000 tokens ($)
        self.model_costs = {
            "llama3-8b": {"prompt": 0.0001, "completion": 0.0002},
            "qwen-14b": {"prompt": 0.0002, "completion": 0.0004},
            "claude-3-5-sonnet": {"prompt": 0.0030, "completion": 0.0150},
            "gpt-4o": {"prompt": 0.0050, "completion": 0.0150},
            "ollama-local": {"prompt": 0.0000, "completion": 0.0000},
        }

        # Metrics state
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_estimated_cost_usd = 0.0
        self.active_fallback_chain = [
            "ollama-local",
            "llama3-8b",
            "qwen-14b",
            "claude-3-5-sonnet",
        ]
        self.routing_logs = []

    def check_rate_limit(self) -> bool:
        """Enforces a sliding window rate limit."""
        now = time.time()
        with self.lock:
            # Clean requests older than 60 seconds
            self.request_timestamps = [
                t for t in self.request_timestamps if now - t < 60
            ]
            if len(self.request_timestamps) >= self.rate_limit_max_per_minute:
                return False
            self.request_timestamps.append(now)
            return True

    def calculate_cost(
        self, model_name: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculates estimated request cost in USD."""
        cost_spec = self.model_costs.get(
            model_name, {"prompt": 0.0001, "completion": 0.0002}
        )
        cost = (input_tokens / 1000.0 * cost_spec["prompt"]) + (
            output_tokens / 1000.0 * cost_spec["completion"]
        )
        return round(cost, 6)

    def route_request(self, prompt: str, requested_model: str = None) -> dict:
        """
        Dynamically routes request based on rate limit, complexity score, and cost autopilot.
        """
        if not self.check_rate_limit():
            return {
                "status": "rate_limited",
                "error": "Sliding window rate limit exceeded (120 req/min). Please try again in a few seconds.",
                "model_selected": None,
            }

        # Complexity Scoring based on prompt length and keywords
        complexity = "low"
        prompt_len = len(prompt)
        high_reasoning_keywords = [
            "architecture",
            "prove",
            "theorem",
            "quant",
            "refactor",
            "arbitrage",
            "codebase",
        ]

        if prompt_len > 1000 or any(
            kw in prompt.lower() for kw in high_reasoning_keywords
        ):
            complexity = "high"
        elif prompt_len > 300:
            complexity = "medium"

        # Selection logic based on complexity
        if requested_model and requested_model in self.active_fallback_chain:
            selected_model = requested_model
        else:
            if complexity == "low":
                selected_model = "ollama-local"
            elif complexity == "medium":
                selected_model = "llama3-8b"
            else:
                selected_model = "claude-3-5-sonnet"

        # Simulate token usage estimation
        est_input_tokens = max(10, len(prompt) // 4)
        est_output_tokens = max(50, est_input_tokens * 2)
        est_cost = self.calculate_cost(
            selected_model, est_input_tokens, est_output_tokens
        )

        with self.lock:
            self.total_input_tokens += est_input_tokens
            self.total_output_tokens += est_output_tokens
            self.total_estimated_cost_usd += est_cost
            log_entry = {
                "timestamp": time.time(),
                "complexity": complexity,
                "selected_model": selected_model,
                "fallback_chain": self.active_fallback_chain,
                "input_tokens": est_input_tokens,
                "output_tokens": est_output_tokens,
                "cost_usd": est_cost,
            }
            self.routing_logs.append(log_entry)
            if len(self.routing_logs) > 100:
                self.routing_logs.pop(0)

        return {
            "status": "routed",
            "complexity": complexity,
            "selected_model": selected_model,
            "fallback_chain": self.active_fallback_chain,
            "estimated_input_tokens": est_input_tokens,
            "estimated_output_tokens": est_output_tokens,
            "estimated_cost_usd": est_cost,
        }

    def get_telemetry(self) -> dict:
        """Returns Gateway & Cost Autopilot metrics."""
        with self.lock:
            return {
                "rate_limit_per_min": self.rate_limit_max_per_minute,
                "active_requests_last_minute": len(self.request_timestamps),
                "total_input_tokens": self.total_input_tokens,
                "total_output_tokens": self.total_output_tokens,
                "total_estimated_cost_usd": round(self.total_estimated_cost_usd, 6),
                "fallback_chain": self.active_fallback_chain,
                "recent_routing_count": len(self.routing_logs),
            }


# Singleton instance
enterprise_gateway = EnterpriseLLMGateway()
