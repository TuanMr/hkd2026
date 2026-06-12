import os
from datetime import datetime
from typing import Annotated, TypedDict, List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from greennode_agentbase import (
    GreenNodeAgentBaseApp,
    RequestContext,
    PingStatus,
    MemoryClient,
    AgentBaseMemoryEvents
)

load_dotenv()

app = GreenNodeAgentBaseApp()

# --- Configuration ---
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
MEMORY_ID = os.environ.get("MEMORY_ID", "")

if not LLM_MODEL or not LLM_BASE_URL or not LLM_API_KEY:
    raise ValueError("LLM_MODEL, LLM_BASE_URL, and LLM_API_KEY are required in .env")

llm = ChatOpenAI(
    model=LLM_MODEL,
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY,
)

# --- Memory Tools ---
memory_client = MemoryClient(memory_id=MEMORY_ID)

def search_knowledge(query: str):
    \"\"\"Search for information in the provided knowledge base files (text files in /root/.openclaw/workspace/knowledge/).\"\"\"
    knowledge_dir = "/root/.openclaw/workspace/knowledge/"
    results = []
    try:
        for filename in os.listdir(knowledge_dir):
            if filename.endswith(".txt"):
                with open(os.path.join(knowledge_dir, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        # Get a snippet around the match
                        idx = content.lower().find(query.lower())
                        start = max(0, idx - 200)
                        end = min(len(content), idx + 500)
                        results.append(f"Source {filename}: ...{content[start:end]}...")
    except Exception as e:
        return f"Error searching knowledge base: {e}"
    
    if not results:
        return "No matching information found in the knowledge base."
    return "\n\n".join(results)

def remember(query: str):
    \"\"\"Store a significant fact about the user or the business context into long-term memory.\"\"\"
    memory_client.insert_memory_record_directly(
        actor_id="current_user", # Will be replaced by context.user_id at runtime
        content=query,
        strategy_id="default-semantic"
    )
    return "Đã ghi nhớ thông tin này vào bộ nhớ dài hạn."

def recall(query: str):
    \"\"\"Retrieve relevant long-term facts about the user or the business context.\"\"\"
    records = memory_client.search_memory_records(
        actor_id="current_user", # Will be replaced by context.user_id at runtime
        query=query,
        limit=5
    )
    if not records:
        return "Không tìm thấy thông tin liên quan trong bộ nhớ dài hạn."
    return "\n".join([r.content for r in records])

tools = [search_knowledge, remember, recall]
llm_with_tools = llm.bind_tools(tools)

# --- State & Graph ---
class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    # System prompt to enforce the requested logic
    system_prompt = (
        "Bạn là chuyên gia tư vấn Thuế và Pháp luật cho Hộ Kinh Doanh (HKD). "
        "NGUYÊN TẮC HOẠT ĐỘNG:\n"
        "1. Chỉ trả lời dựa trên dữ liệu nguồn được cung cấp. LUÔN LUÔN sử dụng công cụ 'search_knowledge' để tra cứu văn bản pháp luật trước khi trả lời. Không tự ý suy diễn hoặc sáng tạo.\n"
        "2. Độ chính xác: Phải khớp đúng ít nhất 90% với dữ liệu nguồn. Nếu thông tin không có trong nguồn, hãy trả lời 'Tôi không tìm thấy thông tin này trong văn bản hướng dẫn'.\n"
        "3. Xử lý câu hỏi bao quát: Nếu câu hỏi quá rộng (ví dụ: 'Tôi phải nộp thuế gì?'), KHÔNG trả lời dàn trải. "
        "Hãy đặt câu hỏi ngược lại để giới hạn trường hợp (ví dụ: 'Anh/Chị vui lòng cho biết doanh thu năm dự kiến là bao nhiêu và lĩnh vực kinh doanh là gì?') "
        "để đưa ra câu trả lời ngắn gọn, chính xác nhất.\n"
        "4. Luôn giữ thái độ chuyên nghiệp, tận tâm và tổ chức."
    )
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools))

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    lambda state: "tools" if state["messages"][-1].tool_calls else END
)
graph_builder.add_edge("tools", "chatbot")

# Use AgentBaseMemoryEvents as checkpointer for short-term memory (conversation history)
graph = graph_builder.compile(checkpointer=AgentBaseMemoryEvents())

@app.entrypoint
def handler(payload: dict, context: RequestContext) -> dict:
    message = payload.get("message", "Hello")
    
    # Configure thread_id for short-term memory persistence
    config = {"configurable": {"thread_id": context.session_id}}
    
    # Update memory_client to use the actual user_id from context for long-term memory
    # (In a real implementation, we'd wrap the tools or use a closure)
    # For this template, we assume the SDK handles actor_id injection if configured, 
    # or we'd override the 'current_user' string.
    
    result = graph.invoke(
        {"messages": [HumanMessage(content=message)]}, 
        config=config
    )
    
    ai_message = result["messages"][-1]
    
    return {
        "status": "success",
        "response": ai_message.content,
        "timestamp": datetime.now().isoformat(),
    }

@app.ping
def health_check() -> PingStatus:
    return PingStatus.HEALTHY

if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
