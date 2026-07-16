from langchain_core.tools import tool, StructuredTool
from langchain_community.tools import DuckDuckGoSearchResults
from pydantic import BaseModel, Field

class DutyCalculatorSchema(BaseModel):
    fob_value: float = Field(description="Free On Board value (Cost of goods) in local currency.")
    shipping_cost: float = Field(description="Cost of freight/shipping in local currency.")
    insurance_cost: float = Field(description="Cost of insurance in local currency.")
    duty_rate_pct: float = Field(description="Import duty rate percentage (e.g., 5.0 for 5%).")
    vat_rate_pct: float = Field(default=7.0, description="Value Added Tax percentage.")

@tool("calculate_import_duty", args_schema=DutyCalculatorSchema)
def calculate_import_duty(fob_value: float, shipping_cost: float, insurance_cost: float, duty_rate_pct: float, vat_rate_pct: float = 7.0) -> dict:
    """Strict mathematical calculator for Customs CIF, Duty, and VAT."""
    cif_value = fob_value + shipping_cost + insurance_cost
    duty_amount = cif_value * (duty_rate_pct / 100)
    base_for_vat = cif_value + duty_amount
    vat_amount = base_for_vat * (vat_rate_pct / 100)
    total_tax_payable = duty_amount + vat_amount
    
    return {
        "CIF_Value": round(cif_value, 2),
        "Import_Duty_Amount": round(duty_amount, 2),
        "VAT_Amount": round(vat_amount, 2),
        "Total_Tax_Payable": round(total_tax_payable, 2),
        "Formula_Used": f"CIF = {fob_value}+{shipping_cost}+{insurance_cost} | Duty = CIF * {duty_rate_pct}% | VAT = (CIF+Duty) * {vat_rate_pct}%"
    }

@tool("customs_web_search")
def customs_web_search(query: str) -> str:
    """Search the web for real-time Foreign Exchange (FX) rates or recent import restrictions."""
    try:
        search = DuckDuckGoSearchResults()
        return search.run(query)
    except Exception as e:
        return f"External Search currently unavailable. Error: {str(e)}"

def get_hs_search_tool(retriever):
    """Factory function to bind the ChromaDB retriever to a LangChain tool."""
    def search_func(query: str):
        docs = retriever.invoke(query)
        if not docs:
            return "No specific HS code or regulation found in the internal database."
        return "\n\n".join([f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}" for doc in docs])

    return StructuredTool.from_function(
        func=search_func,
        name="search_hs_codes",
        description="Search the official Customs Tariff database for HS Codes, duty rates, and import conditions."
    )