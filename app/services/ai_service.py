import os
from google import genai
from google.genai import types
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class AIService:
    def __init__(self):
        """Initialize AIService with Google Gemini client."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.0-flash'
    
    def chat_with_gemini(self, message: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Chat with Google Gemini assistant for travel-related queries.
        
        Args:
            message: User's message/question
            user_context: Optional context about user (personality_type, travel_style, etc.)
        
        Returns:
            AI assistant's response as string
        """
        # Build system prompt for travel assistant role
        system_prompt = """You are DasiLari, a friendly and knowledgeable travel assistant specializing in Da Lat, Vietnam.
Your role is to help travelers discover the beauty of Da Lat and create memorable experiences.

IMPORTANT: You must ALWAYS respond in English only, regardless of what language the user uses to ask questions.

Key responsibilities:
- Provide helpful information about Da Lat attractions, activities, and local insights
- Recommend destinations based on user preferences and personality
- Suggest itineraries that match travel styles (solo/group, introvert/extrovert)
- Offer practical advice on costs, timing, and transportation
- Be warm, enthusiastic, and culturally sensitive

Communication style:
- Friendly and conversational
- Use simple, clear English
- Provide specific, actionable recommendations
- Include practical details (costs, time, location)
- Be encouraging and supportive
- Always reply in English, even if the user asks in Vietnamese or another language"""

        # Add user context to system prompt if available
        if user_context:
            context_info = "\n\nUser Profile:"
            if "personality_type" in user_context:
                context_info += f"\n- Personality: {user_context['personality_type']}"
            if "travel_style" in user_context:
                context_info += f"\n- Travel Style: {user_context['travel_style']}"
            if "transport_type" in user_context:
                context_info += f"\n- Transport: {user_context['transport_type']}"
            if "has_itinerary" in user_context:
                itinerary_status = "Yes" if user_context['has_itinerary'] else "No"
                context_info += f"\n- Has existing itinerary: {itinerary_status}"
            
            system_prompt += context_info
        
        try:
            # Combine system prompt and user message for Gemini
            full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                )
            )
            
            return response.text.strip()
        
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def suggest_destinations_by_emotion(self, emotion: str, destinations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze user emotion and suggest 3-5 suitable Da Lat destinations with reasoning.
        
        Args:
            emotion: User's current emotion (happy, sad, stressed, excited, etc.)
            destinations: List of available destinations from database
        
        Returns:
            Dict with suggested destinations and reasoning
        """
        # Create prompt for emotion-based destination matching
        destinations_info = "\n".join([
            f"- {dest['name']}: {dest['description']} (Category: {dest['category']}, "
            f"Photo spot: {dest.get('photo_spot', False)}, Cost: {dest.get('estimated_cost', 0)} VND)"
            for dest in destinations[:15]  # Limit to avoid token limits
        ])
        
        prompt = f"""Based on the user's current emotion: "{emotion}", analyze and recommend 3-5 suitable destinations from Da Lat.

Available destinations:
{destinations_info}

Consider:
- For "happy" emotions: Suggest vibrant, social places with photo opportunities
- For "sad" emotions: Suggest peaceful, healing places in nature
- For "stressed" emotions: Suggest quiet, relaxing spots away from crowds
- For "excited" emotions: Suggest adventurous, energetic activities
- For "romantic" emotions: Suggest beautiful, intimate locations

Provide your response in JSON format:
{{
    "emotion_analysis": "Brief explanation of why these destinations match the emotion",
    "recommendations": [
        {{
            "destination_name": "Name",
            "reason": "Why this destination suits the emotion",
            "priority": "high/medium"
        }}
    ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert travel psychologist who matches destinations to emotional states."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=600
            )
            
            import json
            result = json.loads(response.choices[0].message.content.strip())
            return result
        
        except Exception as e:
            # Fallback recommendations if API fails
            return {
                "emotion_analysis": f"Analyzing destinations for {emotion} emotion",
                "recommendations": [
                    {
                        "destination_name": dest["name"],
                        "reason": f"Suitable for {emotion} mood",
                        "priority": "medium"
                    }
                    for dest in destinations[:3]
                ]
            }
    
    def generate_itinerary(
        self, 
        user_preferences: Dict[str, Any], 
        selected_destinations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a day plan itinerary with time slots, costs, and directions.
        
        Args:
            user_preferences: User profile (personality_type, travel_style, transport_type)
            selected_destinations: List of destinations to include in itinerary
        
        Returns:
            Dict with complete itinerary including time slots, costs, and routing
        """
        destinations_info = "\n".join([
            f"- {dest['name']}: Location: {dest['location']}, "
            f"Estimated time: {dest.get('estimated_time', 60)} minutes, "
            f"Cost: {dest.get('estimated_cost', 0)} VND"
            for dest in selected_destinations
        ])
        
        personality = user_preferences.get('personality_type', 'balanced')
        travel_style = user_preferences.get('travel_style', 'solo')
        transport = user_preferences.get('transport_type', 'motorbike')
        
        prompt = f"""Create a detailed day itinerary for a traveler visiting Da Lat with these preferences:
- Personality: {personality}
- Travel Style: {travel_style}
- Transportation: {transport}

Selected destinations to visit:
{destinations_info}

Requirements:
- Organize destinations by optimal time slots (morning/afternoon/evening)
- Consider travel time between locations
- Include break times for meals
- Calculate total estimated cost
- Provide brief directions and tips
- Adjust pace based on personality (introverts: slower, more breaks; extroverts: active, social)

Provide response in JSON format:
{{
    "itinerary_title": "Your Da Lat Day Trip",
    "total_estimated_cost": 0,
    "total_duration": "X hours",
    "schedule": [
        {{
            "time_slot": "morning/afternoon/evening",
            "time_range": "09:00 - 11:00",
            "destination": "Destination Name",
            "activity": "What to do",
            "duration": "X minutes",
            "cost": 0,
            "directions": "How to get there",
            "tips": "Helpful advice"
        }}
    ],
    "meal_suggestions": [
        {{
            "time": "12:00",
            "suggestion": "Lunch recommendation",
            "estimated_cost": 0
        }}
    ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Da Lat travel planner who creates optimized, personalized itineraries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            import json
            result = json.loads(response.choices[0].message.content.strip())
            return result
        
        except Exception as e:
            # Fallback basic itinerary if API fails
            basic_schedule = []
            time_slots = ["morning", "afternoon", "evening"]
            total_cost = 0
            
            for idx, dest in enumerate(selected_destinations[:3]):
                cost = dest.get('estimated_cost', 0)
                total_cost += cost
                basic_schedule.append({
                    "time_slot": time_slots[min(idx, 2)],
                    "destination": dest['name'],
                    "activity": f"Visit {dest['name']}",
                    "duration": f"{dest.get('estimated_time', 90)} minutes",
                    "cost": cost,
                    "directions": f"Located at {dest['location']}",
                    "tips": "Enjoy the experience!"
                })
            
            return {
                "itinerary_title": "Your Da Lat Day Trip",
                "total_estimated_cost": total_cost,
                "total_duration": "8 hours",
                "schedule": basic_schedule,
                "meal_suggestions": []
            }


# Singleton instance
ai_service = AIService()
