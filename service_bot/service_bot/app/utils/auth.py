import re

def validate_email(email):

    if not email:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):

    if not phone:
        return False

    clean_phone = re.sub(r'[\s\-()]', '', phone)

    if clean_phone.startswith('+'):
        clean_phone = clean_phone[1:]

    return clean_phone.isdigit() and 10 <= len(clean_phone) <= 15

def format_phone_for_api(phone):

    if not phone:
        return ""

    clean_phone = re.sub(r'[\s\-()]', '', phone)

    if clean_phone.startswith('+7'):
        clean_phone = clean_phone[2:]  
    elif clean_phone.startswith('7') and len(clean_phone) > 10:
        clean_phone = clean_phone[1:]  
    elif clean_phone.startswith('8') and len(clean_phone) > 10:
        clean_phone = clean_phone[1:]  

    return clean_phone