from typing import Dict


def mock_lead_capture(name: str, email: str, platform: str) -> Dict[str, any]:
    print(f"Lead captured successfully: {name}, {email}, {platform}")
    
    return {
        "success": True,
        "message": f"Lead captured successfully: {name}, {email}, {platform}",
        "data": {
            "name": name,
            "email": email,
            "platform": platform
        }
    }


def validate_lead_data(name: str = None, email: str = None, platform: str = None) -> Dict[str, any]:
    missing_fields = []
    
    if not name or name.strip() == "":
        missing_fields.append("name")
    if not email or email.strip() == "":
        missing_fields.append("email")
    if not platform or platform.strip() == "":
        missing_fields.append("platform")
    
    return {
        "is_complete": len(missing_fields) == 0,
        "missing_fields": missing_fields
    }
