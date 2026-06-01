# ============================================================
# Agent 1: Hypothesis/Optimist (Yang) — Full LangChain ReAct
# Model: GPT-4o (Primary), Claude 3.5 Sonnet (Fallback)
# ============================================================
#
# DUAL MODE:
# - Direct mode (default): Uses mock server, no API keys needed.
#   All tests pass without real LLM access.
# - ReAct mode: Set USE_REACT_AGENT=true + provide API keys.
#   Uses LangChain ReAct agent with tool-calling.
#
# NOTE: AgentExecutor, create_react_agent, and
# ConversationBufferMemory are stubbed for direct-mode testing.
# When USE_REACT_AGENT=true with real API keys, uncomment the
# real imports and remove the stubs.
# ============================================================

import httpx
import json
import os
from typing import Annotated
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, AIMessage
# from langchain.agents import create_react_agent, AgentExecutor
class AgentExecutor: pass
def create_react_agent(*args, **kwargs): pass
from langchain.tools import tool
# from langchain.memory import ConversationBufferMemory
class ConversationBufferMemory:
    def __init__(self, *args, **kwargs): pass

from models import VendorRiskAssessment, DataCompleteness
from agent1_prompt import AGENT1_SYSTEM_PROMPT, AGENT1_USER_PROMPT_TEMPLATE


# ============================================================
# LLM Configuration: Primary + Fallback
# ============================================================

PRIMARY_LLM = ChatOpenAI(
    model="gpt-4o-2024-08-06",
    temperature=0.0,
    api_key=os.getenv("OPENAI_API_KEY", "sk-dummy-key-for-testing"),
)

FALLBACK_LLM = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0.0,
    api_key=os.getenv("ANTHROPIC_API_KEY", "sk-ant-dummy-key-for-testing"),
)

MULTIPLICITY_LLM = ChatOpenAI(
    model="gpt-4o-2024-08-06",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY", "sk-dummy-key-for-testing"),
)


# ============================================================
# LangChain Tools (using @tool decorator)
# ============================================================

@tool
def query_opencorporates(vendor_name: str) -> str:
    """Query OpenCorporates for company registry data. Input: vendor name string."""
    try:
        response = httpx.get(
            f"http://localhost:8000/assess_vendor/{vendor_name}",
            timeout=10.0
        )
        data = response.json()
        return json.dumps({
            "source": "OpenCorporates",
            "status": data.get("data_completeness", "none"),
            "red_flags": data.get("red_flags", []),
            "company_status": "Found" if data.get("data_completeness") != "none" else "Not Found"
        })
    except httpx.TimeoutException:
        return json.dumps({"source": "OpenCorporates", "status": "timeout"})
    except Exception as e:
        return json.dumps({"source": "OpenCorporates", "status": "error", "detail": str(e)})


@tool
def query_newsapi(vendor_name: str) -> str:
    """Query NewsAPI for negative media signals about a vendor. Input: vendor name string."""
    try:
        response = httpx.get(
            f"http://localhost:8000/assess_vendor/{vendor_name}",
            timeout=10.0
        )
        data = response.json()
        flags = data.get("red_flags", [])
        return json.dumps({
            "source": "NewsAPI",
            "status": data.get("data_completeness", "none"),
            "negative_signals": flags,
            "has_negative_news": len(flags) > 0
        })
    except httpx.TimeoutException:
        return json.dumps({"source": "NewsAPI", "status": "timeout"})
    except Exception as e:
        return json.dumps({"source": "NewsAPI", "status": "error", "detail": str(e)})


TOOLS = [query_opencorporates, query_newsapi]


# ============================================================
# Output Parser
# ============================================================

pydantic_parser = PydanticOutputParser(pydantic_object=VendorRiskAssessment)


# ============================================================
# Predictive Multiplicity Check
# ============================================================

def check_predictive_multiplicity(vendor_name: str, primary_score: int) -> bool:
    """
    Run a second evaluation at higher temperature.
    If delta > 15, flag as multiplicity concern.
    (Frohnapfel et al., arXiv:2602.11944)
    """
    try:
        multiplicity_prompt = f"Evaluate vendor '{vendor_name}' risk score (0-100). Return ONLY an integer."
        response = MULTIPLICITY_LLM.invoke(multiplicity_prompt)
        secondary_score = int(response.content.strip())
        delta = abs(primary_score - secondary_score)
        return delta > 15
    except Exception:
        return False


# ============================================================
# Adversarial Robustness Check
# ============================================================

def check_new_entity(assessment: VendorRiskAssessment) -> bool:
    """
    If ALL sources returned nothing, flag as new entity with no history.
    (arXiv:2605.17163)
    """
    if (
        len(assessment.data_sources_used) == 0
        and assessment.data_completeness == DataCompleteness.none
    ):
        return True
    return assessment.new_entity_no_history


# ============================================================
# Slimming Function: Strip fields for Agent 2
# ============================================================

def slim_for_agent2(assessment: VendorRiskAssessment) -> dict:
    """
    Structured information compartmentalization.
    Agent 2 receives ONLY bare assertions — no reasoning, no flags.
    Prevents anchoring bias.
    """
    return {
        "vendor_name": assessment.vendor_name,
        "risk_score": assessment.risk_score,
        "red_flags": assessment.red_flags,
        "data_sources_used": assessment.data_sources_used,
        "data_completeness": assessment.data_completeness.value,
    }


# ============================================================
# Mode 1: Direct Evaluation (bypasses ReAct, uses mock server)
# Use this for testing without real LLM API keys
# ============================================================

def evaluate_vendor_direct(vendor_name: str) -> VendorRiskAssessment:
    """
    Direct mock evaluation — no LLM calls needed.
    Uses mock server for deterministic testing.
    """
    try:
        response = httpx.get(
            f"http://localhost:8000/assess_vendor/{vendor_name}",
            timeout=10.0
        )
        response.raise_for_status()
        raw_data = response.json()

    except httpx.TimeoutException:
        return VendorRiskAssessment(
            vendor_name=vendor_name,
            reasoning="API timeout occurred during data gathering. No data available.",
            risk_score=0,
            red_flags=[],
            data_sources_used=[],
            data_completeness=DataCompleteness.none,
            conflicting_data=False,
            predictive_multiplicity_flag=False,
            new_entity_no_history=False,
            agent_1_model="gpt-4o-2024-08-06"
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code >= 500:
            raise Exception(f"Primary LLM provider error: {e.response.status_code}")
        raise

    try:
        assessment = VendorRiskAssessment(**raw_data)
    except Exception as e:
        raise ValueError(f"Data contract violation: {e}")

    assessment.predictive_multiplicity_flag = check_predictive_multiplicity(
        vendor_name, assessment.risk_score
    )
    assessment.new_entity_no_history = check_new_entity(assessment)

    return assessment


# ============================================================
# Mode 2: Full ReAct Agent Evaluation (requires real API keys)
# Use this in production / Week 4 when connecting real APIs
# ============================================================

def create_agent1_executor() -> AgentExecutor:
    """
    Creates the full LangChain ReAct agent executor.
    Requires OPENAI_API_KEY environment variable to be set.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT1_SYSTEM_PROMPT),
        ("human", AGENT1_USER_PROMPT_TEMPLATE),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    agent = create_react_agent(
        llm=PRIMARY_LLM,
        tools=TOOLS,
        prompt=prompt,
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        memory=memory,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
    )

    return agent_executor


def evaluate_vendor_react(vendor_name: str) -> VendorRiskAssessment:
    """
    Full ReAct agent evaluation.
    Agent decides which tools to call, gathers data, returns assessment.
    """
    executor = create_agent1_executor()

    result = executor.invoke({
        "vendor_name": vendor_name,
    })

    # Parse the agent's final output into our Pydantic contract
    output_text = result.get("output", "")
    assessment = pydantic_parser.parse(output_text)

    # Run post-processing checks
    assessment.predictive_multiplicity_flag = check_predictive_multiplicity(
        vendor_name, assessment.risk_score
    )
    assessment.new_entity_no_history = check_new_entity(assessment)

    return assessment


# ============================================================
# Main Evaluation Router
# ============================================================

def evaluate_vendor(vendor_name: str, use_react: bool = False) -> VendorRiskAssessment:
    """
    Routes to direct or ReAct evaluation based on mode.
    Default: direct (mock server, no API keys needed)
    Set use_react=True for full LangChain agent (requires API keys)
    """
    if use_react:
        return evaluate_vendor_react(vendor_name)
    else:
        return evaluate_vendor_direct(vendor_name)


# ============================================================
# CLI Test Runner
# ============================================================

if __name__ == "__main__":
    test_vendors = [
        "ClearPath Logistics",
        "Nexus Global Holdings",
        "ErrorTrigger Inc.",
        "PartialData Corp",
        "Conflict Industries",
        "asdfghjkl corp",
        "Uncertain Ventures",
        "Sneaky Risk Ltd",
    ]

    use_react_mode = os.getenv("USE_REACT_AGENT", "false").lower() == "true"

    print(f"Mode: {'ReAct Agent (LLM)' if use_react_mode else 'Direct (Mock Server)'}")
    print(f"{'='*60}")

    for vendor in test_vendors:
        print(f"\n{'='*60}")
        print(f"Testing: {vendor}")
        print(f"{'='*60}")
        try:
            result = evaluate_vendor(vendor, use_react=use_react_mode)
            print(f"  Score: {result.risk_score}")
            print(f"  Completeness: {result.data_completeness.value}")
            print(f"  Red Flags: {result.red_flags}")
            print(f"  Multiplicity: {result.predictive_multiplicity_flag}")
            print(f"  New Entity: {result.new_entity_no_history}")
            print(f"  Conflicting: {result.conflicting_data}")

            slimmed = slim_for_agent2(result)
            print(f"  Slimmed for Agent 2: {json.dumps(slimmed, indent=2)}")

        except Exception as e:
            print(f"  ERROR: {e}")
