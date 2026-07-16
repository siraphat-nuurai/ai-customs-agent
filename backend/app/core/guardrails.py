class CustomsGuardrails:
    def validate_input(self, user_input: str) -> dict:
        """Blocks prompt injections and smuggling advice."""
        unsafe_keywords = [
            "smuggle", "evade tax", "hide in luggage", 
            "under-declare", "bribe", "ignore previous instructions",
            "fake invoice"
        ]
        
        for word in unsafe_keywords:
            if word in user_input.lower():
                return {
                    "is_safe": False, 
                    "reason": f"Query blocked. Contains prohibited term relating to tax evasion or smuggling: '{word}'"
                }
        return {"is_safe": True, "reason": "Pass"}

    def validate_output(self, agent_output: str) -> dict:
        """Ensures the mandatory disclaimer is present and no illegal guarantees are made."""
        safe_output = agent_output
        
        if "100% guaranteed" in safe_output.lower() or "will definitely pass" in safe_output.lower():
            return {
                "is_safe": False, 
                "reason": "Agent provided an absolute guarantee, which violates customs assessment policy."
            }
            
        disclaimer = "\n\n*Disclaimer: This is an estimated assessment. Final duty and classification are subject to the physical inspection of the Customs Department.*"
        if "Disclaimer:" not in safe_output:
            safe_output += disclaimer
            
        return {"is_safe": True, "output": safe_output}