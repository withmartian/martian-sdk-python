"""List of supported LLM models."""

# OpenAI Models
GPT_4_5_PREVIEW = "openai/openai/gpt-4.5-preview"
GPT_4_1 = "openai/openai/gpt-4.1"
GPT_4_1_MINI = "openai/openai/gpt-4.1-mini"
GPT_4_1_NANO = "openai/openai/gpt-4.1-nano"
GPT_4O = "openai/openai/gpt-4o"
GPT_4O_MINI = "openai/openai/gpt-4o-mini"

# Anthropic Models
CLAUDE_3_OPUS = "anthropic/anthropic/claude-3-opus-latest"
CLAUDE_3_5_HAIKU = "anthropic/anthropic/claude-3-5-haiku-latest"
CLAUDE_3_5_SONNET = "anthropic/anthropic/claude-3-5-sonnet-latest"
CLAUDE_3_7_SONNET = "anthropic/anthropic/claude-3-7-sonnet-latest"

# Together Models
DEEPSEEK_R1 = "together/deepseek-ai/DeepSeek-R1"
DEEPSEEK_V3 = "together/deepseek-ai/DeepSeek-V3"
MISTRAL_SMALL_24B = "together/mistralai/Mistral-Small-24B-Instruct-2501"
NEMOTRON_70B = "together/nvidia/Llama-3.1-Nemotron-70B-Instruct-HF"
LLAMA_3_3_70B = "together/meta-llama/Llama-3.3-70B-Instruct-Turbo"
LLAMA_3_1_405B = "together/meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
QWEN_72B = "together/Qwen/Qwen2.5-72B-Instruct-Turbo"
QWEN_CODER_32B = "together/Qwen/Qwen2.5-Coder-32B-Instruct"
GEMMA_2_27B = "together/google/gemma-2-27b-it"

# Gemini Models
GEMINI_1_5_FLASH = "gemini/gemini/gemini-1.5-flash"
GEMINI_1_5_FLASH_8B = "gemini/gemini/gemini-1.5-flash-8b"
GEMINI_1_5_FLASH_8B_LATEST = "gemini/gemini/gemini-1.5-flash-8b-latest"
GEMINI_1_5_FLASH_LATEST = "gemini/gemini/gemini-1.5-flash-latest"
GEMINI_1_5_PRO = "gemini/gemini/gemini-1.5-pro"
GEMINI_1_5_PRO_LATEST = "gemini/gemini/gemini-1.5-pro-latest"
GEMINI_2_0_FLASH = "gemini/gemini/gemini-2.0-flash"

# Model Groups
OPENAI_MODELS = frozenset([
    GPT_4_5_PREVIEW,
    GPT_4_1,
    GPT_4_1_MINI,
    GPT_4_1_NANO,
    GPT_4O,
    GPT_4O_MINI
])

ANTHROPIC_MODELS = frozenset([
    CLAUDE_3_OPUS,
    CLAUDE_3_5_HAIKU,
    CLAUDE_3_5_SONNET,
    CLAUDE_3_7_SONNET,
])

TOGETHER_MODELS = frozenset([
    DEEPSEEK_R1,
    DEEPSEEK_V3,
    MISTRAL_SMALL_24B,
    NEMOTRON_70B,
    LLAMA_3_3_70B,
    LLAMA_3_1_405B,
    QWEN_72B,
    QWEN_CODER_32B,
    GEMMA_2_27B,
])

GEMINI_MODELS = frozenset([
    GEMINI_1_5_FLASH,
    GEMINI_1_5_FLASH_8B,
    GEMINI_1_5_FLASH_8B_LATEST,
    GEMINI_1_5_FLASH_LATEST,
    GEMINI_1_5_PRO,
    GEMINI_1_5_PRO_LATEST,
    GEMINI_2_0_FLASH,
])

# All available models
ALL_MODELS = OPENAI_MODELS | ANTHROPIC_MODELS | TOGETHER_MODELS | GEMINI_MODELS
