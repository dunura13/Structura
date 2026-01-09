import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from src.tools import clean_text_tool


load_dotenv()

# Load API key
_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not _api_key:
    raise ValueError(
        "Missing Gemini API key. Set GOOGLE_API_KEY or GEMINI_API_KEY in your environment/.env file."
    )

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    api_key=_api_key,
)



# System Instructions 
system_prompt = """
You are a Senior Construction QA Agent ("The Auditor").
Your goal is to compare a Subcontractor's Submittal against standard Project Requirements.

THE PROCESS:
1. Receive raw text input.
2. ANALYZE: If the text looks messy (OCR errors, weird symbols), you MUST use the 'clean_text_tool' to fix it.
3. EXTRACT: Identify the Material Name, Grade/Standard, and any Risk Factors.
4. AUDIT: Compare the extracted data against this standard rule: 
   - "All structural concrete must be Type V Sulfate Resistant."
   - "Reinforcement bars must be Grade 60."
5. REPORT: Output a JSON summary of your findings.

Your Final Output must be strictly valid JSON with these keys:
{
  "material": "Name of material",
  "proposed_grade": "Grade found in text",
  "compliant": "Yes/No",
  "risk_level": "High/Medium/Low",
  "explanation": "Brief reason for the risk level"
}

"""

tools = [clean_text_tool]

# Create an agent graph using the new LangChain agents API
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
)


def run_audit_agent(raw_text: str):
    """Entry point for Streamlit. Runs the audit agent on the given text."""
    try:
        # The new agent API expects a state dict with a "messages" list

        state = agent.invoke({"messages": [("user", raw_text)]})
        messages = state.get("messages", [])

        raw_content = messages[-1].content

        final_text = ""

        if isinstance(raw_content, list):
            for block in raw_content:
                if isinstance(block, dict) and "text" in block:
                    final_text += block["text"]
        
        else:
            final_text = str(raw_content)

        # Clean the Markdown (The "Translation Layer")
        clean_json_str = final_text.replace("```json", "").replace("```", "").strip()


        # parse into python dict
        return json.loads(clean_json_str)
    
    except json.JSONDecodeError:

        # If the agent messed up the JSON format, return an error dict
        return {
            "error": "Parsing Error", 
            "explanation": "The Agent failed to return valid JSON.",
            "raw_output": str(raw_content)
        }
    except Exception as e:
        return {"error": f"Error running agent: {str(e)}"}










