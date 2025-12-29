# Dữ liệu mẫu người dùng

from datetime import datetime

MOCK_USERS = [
    {
        "id": 1,
        "name": "Nguyễn Văn An",
        "personality_type": "extrovert",
        "travel_style": "group",
        "transport_type": "motorbike",
        "has_itinerary": True,
        "created_at": "2025-12-20T10:30:00"
    },
    {
        "id": 2,
        "name": "Trần Thị Bình",
        "personality_type": "introvert",
        "travel_style": "solo",
        "transport_type": "car",
        "has_itinerary": False,
        "created_at": "2025-12-21T14:15:00"
    },
    {
        "id": 3,
        "name": "Lê Minh Cường",
        "personality_type": "extrovert",
        "travel_style": "group",
        "transport_type": "walk",
        "has_itinerary": True,
        "created_at": "2025-12-22T09:00:00"
    },
    {
        "id": 4,
        "name": "Phạm Thu Duyên",
        "personality_type": "introvert",
        "travel_style": "solo",
        "transport_type": "bicycle",
        "has_itinerary": False,
        "created_at": "2025-12-23T16:45:00"
    },
    {
        "id": 5,
        "name": "Hoàng Minh Đức",
        "personality_type": "extrovert",
        "travel_style": "group",
        "transport_type": "motorbike",
        "has_itinerary": True,
        "created_at": "2025-12-24T11:20:00"
    },
    {
        "id": 6,
        "name": "Võ Thị Hương",
        "personality_type": "introvert",
        "travel_style": "solo",
        "transport_type": "car",
        "has_itinerary": False,
        "created_at": "2025-12-25T13:30:00"
    }
]

# Counter để tạo ID mới cho user
_user_id_counter = len(MOCK_USERS) + 1


def get_all_users():
    """Lấy tất cả người dùng"""
    return MOCK_USERS


def get_user_by_id(user_id: int):
    """Lấy người dùng theo ID"""
    for user in MOCK_USERS:
        if user["id"] == user_id:
            return user
    return None


def create_user(name: str, personality_type: str, travel_style: str, transport_type: str, has_itinerary: bool):
    """Tạo người dùng mới"""
    global _user_id_counter
    
    new_user = {
        "id": _user_id_counter,
        "name": name,
        "personality_type": personality_type,
        "travel_style": travel_style,
        "transport_type": transport_type,
        "has_itinerary": has_itinerary,
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_USERS.append(new_user)
    _user_id_counter += 1
    
    return new_user


def filter_users_by_preferences(personality_type=None, travel_style=None):
    """Lọc người dùng theo tính cách và phong cách du lịch"""
    filtered = MOCK_USERS.copy()
    
    if personality_type:
        filtered = [u for u in filtered if u["personality_type"] == personality_type]
    
    if travel_style:
        filtered = [u for u in filtered if u["travel_style"] == travel_style]
    
    return filtered
