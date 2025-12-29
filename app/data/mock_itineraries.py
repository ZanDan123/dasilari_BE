# Dữ liệu mẫu lịch trình du lịch

from datetime import datetime, date

MOCK_ITINERARIES = [
    {
        "id": 1,
        "user_id": 1,
        "destination_id": 1,
        "visit_date": "2025-12-30",
        "time_slot": "morning",
        "emotion_tag": "peaceful",
        "created_at": "2025-12-20T10:35:00"
    },
    {
        "id": 2,
        "user_id": 1,
        "destination_id": 2,
        "visit_date": "2025-12-30",
        "time_slot": "afternoon",
        "emotion_tag": "adventurous",
        "created_at": "2025-12-20T10:36:00"
    },
    {
        "id": 3,
        "user_id": 1,
        "destination_id": 5,
        "visit_date": "2025-12-30",
        "time_slot": "evening",
        "emotion_tag": "romantic",
        "created_at": "2025-12-20T10:37:00"
    },
    {
        "id": 4,
        "user_id": 3,
        "destination_id": 7,
        "visit_date": "2025-12-31",
        "time_slot": "morning",
        "emotion_tag": "curious",
        "created_at": "2025-12-22T09:15:00"
    },
    {
        "id": 5,
        "user_id": 3,
        "destination_id": 14,
        "visit_date": "2025-12-31",
        "time_slot": "afternoon",
        "emotion_tag": "happy",
        "created_at": "2025-12-22T09:16:00"
    },
    {
        "id": 6,
        "user_id": 5,
        "destination_id": 6,
        "visit_date": "2026-01-02",
        "time_slot": "afternoon",
        "emotion_tag": "adventurous",
        "created_at": "2025-12-24T11:25:00"
    },
    {
        "id": 7,
        "user_id": 5,
        "destination_id": 20,
        "visit_date": "2026-01-03",
        "time_slot": "morning",
        "emotion_tag": "peaceful",
        "created_at": "2025-12-24T11:26:00"
    }
]

# Counter để tạo ID mới cho itinerary
_itinerary_id_counter = len(MOCK_ITINERARIES) + 1


def get_all_itineraries():
    """Lấy tất cả lịch trình"""
    return MOCK_ITINERARIES


def get_itinerary_by_id(itinerary_id: int):
    """Lấy lịch trình theo ID"""
    for itinerary in MOCK_ITINERARIES:
        if itinerary["id"] == itinerary_id:
            return itinerary
    return None


def get_itineraries_by_user(user_id: int):
    """Lấy tất cả lịch trình của một người dùng"""
    return [i for i in MOCK_ITINERARIES if i["user_id"] == user_id]


def create_itinerary(user_id: int, destination_id: int, visit_date: str, time_slot: str, emotion_tag: str = None):
    """Tạo lịch trình mới"""
    global _itinerary_id_counter
    
    new_itinerary = {
        "id": _itinerary_id_counter,
        "user_id": user_id,
        "destination_id": destination_id,
        "visit_date": visit_date,
        "time_slot": time_slot,
        "emotion_tag": emotion_tag,
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_ITINERARIES.append(new_itinerary)
    _itinerary_id_counter += 1
    
    return new_itinerary


def delete_itinerary(itinerary_id: int):
    """Xóa lịch trình"""
    global MOCK_ITINERARIES
    MOCK_ITINERARIES = [i for i in MOCK_ITINERARIES if i["id"] != itinerary_id]
    return True


def filter_itineraries(user_id=None, destination_id=None, emotion_tag=None):
    """Lọc lịch trình theo điều kiện"""
    filtered = MOCK_ITINERARIES.copy()
    
    if user_id:
        filtered = [i for i in filtered if i["user_id"] == user_id]
    
    if destination_id:
        filtered = [i for i in filtered if i["destination_id"] == destination_id]
    
    if emotion_tag:
        filtered = [i for i in filtered if i["emotion_tag"] == emotion_tag]
    
    return filtered
