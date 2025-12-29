from typing import List, Dict, Any, Optional
from datetime import date
from collections import defaultdict

from app.data import (
    get_user_by_id, get_all_users, get_destination_by_id,
    get_itineraries_by_user, filter_itineraries
)


class MatchingService:
    """Service for matching travelers and creating group itineraries."""
    
    def __init__(self):
        """Initialize MatchingService."""
        pass
    
    def find_matching_travelers(
        self, 
        user_id: int, 
        destination_id: int, 
        time_slot: str,
        visit_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Find users with same destination and time preferences for potential travel buddies.
        
        Args:
            user_id: Current user's ID
            destination_id: Destination to match
            time_slot: Time slot to match (morning/afternoon/evening)
            visit_date: Optional specific date to match
        
        Returns:
            List of potential travel buddies with their profiles and compatibility info
        """
        # Get current user's profile for compatibility matching
        current_user = get_user_by_id(user_id)
        if not current_user:
            return []
        
        # Get all itineraries
        all_itineraries = filter_itineraries(destination_id=destination_id)
        
        # Filter by time_slot and exclude current user
        matching_itineraries = [
            i for i in all_itineraries 
            if i["user_id"] != user_id and i["time_slot"] == time_slot
        ]
        
        # Filter by date if provided
        if visit_date:
            date_str = visit_date.isoformat() if isinstance(visit_date, date) else visit_date
            matching_itineraries = [i for i in matching_itineraries if i["visit_date"] == date_str]
        
        matching_travelers = []
        for itinerary in matching_itineraries:
            user = get_user_by_id(itinerary["user_id"])
            destination = get_destination_by_id(itinerary["destination_id"])
            
            if not user or not destination:
                continue
            
            # Calculate compatibility score
            compatibility_score = self._calculate_compatibility(current_user, user)
            
            matching_travelers.append({
                "user_id": user["id"],
                "name": user["name"],
                "personality_type": user["personality_type"],
                "travel_style": user["travel_style"],
                "transport_type": user["transport_type"],
                "destination": {
                    "id": destination["id"],
                    "name": destination["name"],
                    "location": destination["location"]
                },
                "visit_date": itinerary["visit_date"],
                "time_slot": itinerary["time_slot"],
                "emotion_tag": itinerary["emotion_tag"],
                "compatibility_score": compatibility_score,
                "compatibility_level": self._get_compatibility_level(compatibility_score),
                "match_reasons": self._get_match_reasons(current_user, user)
            })
        
        # Sort by compatibility score (highest first)
        matching_travelers.sort(key=lambda x: x["compatibility_score"], reverse=True)
        
        return matching_travelers
    
    def suggest_group_itinerary(
        self, 
        user_ids: List[int], 
        target_date: date
    ) -> Dict[str, Any]:
        """
        Find common destinations and create group itinerary with split options when preferences differ.
        
        Args:
            user_ids: List of user IDs to create group itinerary for
            target_date: Date for the group itinerary
        
        Returns:
            Dict with group itinerary including common destinations and split options
        """
        if not user_ids or len(user_ids) < 2:
            return {
                "error": "At least 2 users required for group itinerary",
                "group_size": len(user_ids) if user_ids else 0
            }
        
        # Get all users' information
        users = [get_user_by_id(uid) for uid in user_ids]
        users = [u for u in users if u is not None]
        users_dict = {user["id"]: user for user in users}
        
        target_date_str = target_date.isoformat() if isinstance(target_date, date) else target_date
        
        # Get all itineraries for these users on the target date
        all_itineraries = []
        for uid in user_ids:
            user_itineraries = get_itineraries_by_user(uid)
            for itin in user_itineraries:
                if itin["visit_date"] == target_date_str:
                    all_itineraries.append(itin)
        
        # Organize itineraries by time slot
        time_slot_data = {
            "morning": defaultdict(list),
            "afternoon": defaultdict(list),
            "evening": defaultdict(list)
        }
        
        for itinerary in all_itineraries:
            destination = get_destination_by_id(itinerary["destination_id"])
            if not destination:
                continue
                
            time_slot_data[itinerary["time_slot"]][destination["id"]].append({
                "user_id": itinerary["user_id"],
                "user_name": users_dict.get(itinerary["user_id"], {}).get("name", "Unknown"),
                "destination": {
                    "id": destination["id"],
                    "name": destination["name"],
                    "location": destination["location"],
                    "estimated_cost": destination["estimated_cost"],
                    "estimated_time": destination["estimated_time"],
                    "category": destination["category"],
                    "photo_spot": destination["photo_spot"]
                },
                "emotion_tag": itinerary["emotion_tag"]
            })
        
        # Analyze each time slot for common destinations and splits
        group_schedule = []
        split_options = []
        
        for time_slot in ["morning", "afternoon", "evening"]:
            slot_destinations = time_slot_data[time_slot]
            
            if not slot_destinations:
                continue
            
            # Find destinations where all or most users agree
            destination_votes = {
                dest_id: len(users_list) 
                for dest_id, users_list in slot_destinations.items()
            }
            
            if not destination_votes:
                continue
            
            # Find most popular destination
            most_popular_dest_id = max(destination_votes, key=destination_votes.get)
            votes_count = destination_votes[most_popular_dest_id]
            
            # Check if it's a common destination (majority agrees)
            if votes_count >= len(user_ids) * 0.5:  # At least 50% agreement
                # Common destination
                dest_info = slot_destinations[most_popular_dest_id][0]["destination"]
                participating_users = [
                    item["user_name"] 
                    for item in slot_destinations[most_popular_dest_id]
                ]
                
                group_schedule.append({
                    "time_slot": time_slot,
                    "type": "group_activity",
                    "destination": dest_info,
                    "participants": participating_users,
                    "participant_count": votes_count,
                    "agreement_level": f"{int(votes_count/len(user_ids)*100)}%"
                })
            else:
                # Split needed - different preferences
                split_info = {
                    "time_slot": time_slot,
                    "type": "split_activity",
                    "reason": "Group has different preferences for this time slot",
                    "options": []
                }
                
                for dest_id, users_list in slot_destinations.items():
                    dest_info = users_list[0]["destination"]
                    split_info["options"].append({
                        "destination": dest_info,
                        "interested_users": [u["user_name"] for u in users_list],
                        "user_count": len(users_list)
                    })
                
                # Sort options by popularity
                split_info["options"].sort(key=lambda x: x["user_count"], reverse=True)
                split_options.append(split_info)
        
        # Calculate group compatibility
        group_compatibility = self._calculate_group_compatibility(users)
        
        # Generate meeting points and logistics
        meeting_suggestions = self._suggest_meeting_points(group_schedule, users)
        
        return {
            "date": target_date_str,
            "group_size": len(user_ids),
            "participants": [
                {
                    "id": user["id"],
                    "name": user["name"],
                    "personality_type": user["personality_type"],
                    "travel_style": user["travel_style"]
                }
                for user in users
            ],
            "group_compatibility": group_compatibility,
            "group_schedule": group_schedule,
            "split_options": split_options,
            "meeting_suggestions": meeting_suggestions,
            "summary": {
                "common_activities": len(group_schedule),
                "split_activities": len(split_options),
                "recommendation": self._get_group_recommendation(
                    len(group_schedule), 
                    len(split_options),
                    group_compatibility
                )
            }
        }
    
    def _calculate_compatibility(self, user1: dict, user2: dict) -> float:
        """Calculate compatibility score between two users (0-100)."""
        score = 0.0
        
        # Same personality type: +30 points
        if user1["personality_type"] == user2["personality_type"]:
            score += 30
        
        # Same travel style: +40 points
        if user1["travel_style"] == user2["travel_style"]:
            score += 40
        
        # Same transport type: +20 points
        if user1["transport_type"] == user2["transport_type"]:
            score += 20
        
        # Both have or don't have itinerary: +10 points
        if user1["has_itinerary"] == user2["has_itinerary"]:
            score += 10
        
        return score
    
    def _get_compatibility_level(self, score: float) -> str:
        """Convert compatibility score to level."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Moderate"
        else:
            return "Low"
    
    def _get_match_reasons(self, user1: dict, user2: dict) -> List[str]:
        """Get list of reasons why users match."""
        reasons = []
        
        if user1["personality_type"] == user2["personality_type"]:
            reasons.append(f"Both are {user1['personality_type']}s")
        
        if user1["travel_style"] == user2["travel_style"]:
            reasons.append(f"Both prefer {user1['travel_style']} travel")
        
        if user1["transport_type"] == user2["transport_type"]:
            reasons.append(f"Both use {user1['transport_type']}")
        
        if not reasons:
            reasons.append("Visiting same destination at same time")
        
        return reasons
    
    def _calculate_group_compatibility(self, users: List[dict]) -> Dict[str, Any]:
        """Calculate overall group compatibility."""
        if len(users) < 2:
            return {"score": 0, "level": "N/A"}
        
        # Count personality types
        personality_counts = defaultdict(int)
        travel_style_counts = defaultdict(int)
        
        for user in users:
            personality_counts[user["personality_type"]] += 1
            travel_style_counts[user["travel_style"]] += 1
        
        # Calculate diversity score
        dominant_personality = max(personality_counts, key=personality_counts.get)
        dominant_count = personality_counts[dominant_personality]
        homogeneity_score = (dominant_count / len(users)) * 100
        
        return {
            "score": round(homogeneity_score, 1),
            "level": "High" if homogeneity_score >= 70 else "Medium" if homogeneity_score >= 50 else "Diverse",
            "dominant_personality": dominant_personality,
            "personality_mix": dict(personality_counts),
            "travel_style_mix": dict(travel_style_counts),
            "coordination_difficulty": "Easy" if homogeneity_score >= 70 else "Moderate" if homogeneity_score >= 50 else "Challenging"
        }
    
    def _suggest_meeting_points(self, schedule: List[Dict], users: List[dict]) -> List[Dict[str, str]]:
        """Suggest convenient meeting points based on schedule."""
        suggestions = []
        
        if schedule:
            # Suggest meeting at first destination
            first_activity = schedule[0]
            suggestions.append({
                "time": "Start of day",
                "location": first_activity["destination"]["name"],
                "reason": "Meet at first destination to begin the day together"
            })
        
        # Common meeting point in Da Lat center
        suggestions.append({
            "time": "Flexible",
            "location": "Hồ Xuân Hương",
            "reason": "Central location, easy to find, good landmark"
        })
        
        return suggestions
    
    def _get_group_recommendation(self, common_count: int, split_count: int, compatibility: Dict) -> str:
        """Generate recommendation for the group."""
        if common_count >= 2 and split_count == 0:
            return "Great itinerary! Your group has strong agreement on destinations. This will be a smooth trip."
        elif common_count >= 1 and split_count <= 1:
            return "Good itinerary with mostly aligned preferences. Consider the split option based on energy levels."
        elif split_count > common_count:
            return "Your group has diverse preferences. Consider splitting up during some time slots and regrouping for meals or evening activities."
        else:
            return "Mixed preferences detected. Communication and flexibility will make this trip enjoyable for everyone."


# Singleton instance
matching_service = MatchingService()


def get_matching_service() -> MatchingService:
    """Factory function to get MatchingService instance."""
    return matching_service
