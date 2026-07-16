from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage, AIMessage

from app.tools.customs_tools import calculate_import_duty, customs_web_search, get_hs_search_tool
from app.services.retriever import RetrieverService

class CustomsAgentService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        self.retriever_service = RetrieverService()
        
        hs_tool = get_hs_search_tool(self.retriever_service.get_retriever())
        self.tools = [calculate_import_duty, customs_web_search, hs_tool]
        
    def create_executor(self):
        system_prompt = """
        ROLE:
        You are a Senior Customs and Import Duty Assessor. 
        Your job is to classify goods, calculate exact taxes, and determine import eligibility.

        STRICT ASSESSMENT HIERARCHY:
        1. PROHIBITED (Decline): HIGHEST PRIORITY. If a good is banned (e.g., narcotics, e-cigarettes), the final decision is PROHIBITED. No taxes are calculated.
        2. RESTRICTED (Requires License): 2nd PRIORITY. If a good requires a permit, state "RESTRICTED" and list the required authority.
        3. ALLOWED: 3rd PRIORITY. If allowed, you MUST use the `calculate_import_duty` tool to provide the exact tax breakdown.

        STRICT RULES:
        - NEVER provide advice on how to evade taxes, under-declare values, or smuggle goods.
        - If a user provides foreign currency, use `customs_web_search` to find the current exchange rate before calculating duty.
        - Base HS Codes strictly on the `search_hs_codes` tool.

        RESPONSE STRUCTURE (Markdown):
        ### 📦 Classification & Status
        ### 🧮 Tax & Duty Breakdown
        ### 🏁 Final Customs Recommendation
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )