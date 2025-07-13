# backend/app/services/llm_service.py

import os
from typing import Dict, Any, List, Optional
from groq import Groq
import json
from datetime import datetime

class LLMService:
    """Service for interacting with GROQ LLM"""
    
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
        )
        self.model = "llama3-8b-8192"  # Default GROQ model
    
    async def generate_response(self, prompt: str, system_message: str = None) -> str:
        """Generate a response from the LLM"""
        try:
            messages = []
            
            if system_message:
                messages.append({
                    "role": "system",
                    "content": system_message
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                max_tokens=1024
            )
            
            return chat_completion.choices[0].message.content
        
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    async def analyze_staff_allocation(self, staff_data: List[Dict], shift_data: List[Dict]) -> Dict[str, Any]:
        """Analyze staff allocation needs"""
        
        system_message = """
        You are an AI assistant specialized in hospital staff allocation. 
        Your role is to analyze staff capabilities and shift requirements to provide optimal allocation recommendations.
        Always consider:
        1. Staff skill levels and certifications
        2. Shift requirements and priorities
        3. Work-life balance and staff preferences
        4. Department-specific needs
        5. Cost optimization
        
        Respond in JSON format with specific recommendations.
        """
        
        prompt = f"""
        Analyze the following hospital staffing situation and provide allocation recommendations:
        
        STAFF DATA:
        {json.dumps(staff_data, indent=2)}
        
        SHIFT DATA:
        {json.dumps(shift_data, indent=2)}
        
        Please provide:
        1. Recommended staff allocations for each shift
        2. Confidence scores for each recommendation (0-1)
        3. Reasoning for each allocation
        4. Potential conflicts or issues
        5. Alternative options if primary allocation fails
        
        Format your response as JSON with the following structure:
        {{
            "recommendations": [
                {{
                    "shift_id": "string",
                    "staff_allocations": [
                        {{
                            "staff_id": "string",
                            "confidence": 0.95,
                            "reasoning": "detailed explanation",
                            "role": "string"
                        }}
                    ],
                    "potential_issues": ["list of issues"],
                    "alternatives": ["alternative options"]
                }}
            ],
            "overall_analysis": "summary of the allocation strategy",
            "optimization_score": 0.85
        }}
        """
        
        response = await self.generate_response(prompt, system_message)
        
        try:
            # Try to parse JSON response
            return json.loads(response)
        except json.JSONDecodeError:
            # If JSON parsing fails, return a structured error response
            return {
                "recommendations": [],
                "overall_analysis": response,
                "optimization_score": 0.0,
                "error": "Failed to parse JSON response"
            }
    
    async def evaluate_allocation_constraints(self, allocation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate constraints for a specific allocation request"""
        
        system_message = """
        You are an AI constraint evaluator for hospital staff allocation.
        Analyze the given allocation request and identify any constraint violations or potential issues.
        Consider legal, safety, and operational constraints.
        """
        
        prompt = f"""
        Evaluate the following allocation request for constraint violations:
        
        ALLOCATION REQUEST:
        {json.dumps(allocation_request, indent=2)}
        
        Check for:
        1. Maximum working hours violations
        2. Skill level requirements
        3. Department certifications
        4. Staff availability conflicts
        5. Minimum staffing requirements
        6. Union rules and regulations
        
        Provide a JSON response with:
        {{
            "is_valid": boolean,
            "violations": ["list of constraint violations"],
            "warnings": ["list of potential issues"],
            "suggestions": ["list of suggestions to resolve issues"],
            "severity_score": 0.75
        }}
        """
        
        response = await self.generate_response(prompt, system_message)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "is_valid": False,
                "violations": ["Failed to evaluate constraints"],
                "warnings": [],
                "suggestions": ["Manual review required"],
                "severity_score": 1.0,
                "error": "Failed to parse constraint evaluation"
            }
    
    async def optimize_schedule(self, current_schedule: Dict[str, Any], optimization_goals: List[str]) -> Dict[str, Any]:
        """Optimize the current schedule based on given goals"""
        
        system_message = """
        You are an AI schedule optimizer for hospital operations.
        Your goal is to improve the current schedule based on the specified optimization criteria.
        Consider both efficiency and staff satisfaction.
        """
        
        goals_str = ", ".join(optimization_goals)
        
        prompt = f"""
        Optimize the following hospital schedule based on these goals: {goals_str}
        
        CURRENT SCHEDULE:
        {json.dumps(current_schedule, indent=2)}
        
        Provide optimization recommendations in JSON format:
        {{
            "optimized_schedule": {{
                "changes": [
                    {{
                        "type": "reassignment|swap|add|remove",
                        "details": "description of change",
                        "impact": "expected impact",
                        "priority": "high|medium|low"
                    }}
                ]
            }},
            "performance_metrics": {{
                "cost_reduction": "percentage",
                "efficiency_improvement": "percentage",
                "staff_satisfaction": "score 0-10"
            }},
            "implementation_plan": ["step by step plan"],
            "risks": ["potential risks and mitigation strategies"]
        }}
        """
        
        response = await self.generate_response(prompt, system_message)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "optimized_schedule": {"changes": []},
                "performance_metrics": {},
                "implementation_plan": ["Manual optimization required"],
                "risks": ["Failed to generate optimization plan"],
                "error": "Failed to parse optimization response"
            }

# Global LLM service instance
llm_service = LLMService()