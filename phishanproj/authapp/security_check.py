from datetime import timedelta
from django.utils.timezone import now
from django.core.cache import cache


MAX_ATTEMPTS = 3
LOCK_TIME = timedelta(minutes=5)

def try_code(code, obj):
    if obj.attempts_counter >= MAX_ATTEMPTS:
        if obj.last_attempt_at and now() - obj.last_attempt_at < LOCK_TIME:
            return False, "! Too many attempts. Try later."
        else:
            obj.attempts_counter = 0

    if obj.code == code:
        return True, "Success"
    
    obj.attempts_counter += 1
    obj.last_attempt_at = now()
    obj.save()

    return False, "! Incorrect code. Try again."

def count_login_attempt(email):
    attempts = cache.get(f"login_attempts:{email}", 0)

    if attempts > 4:
        return False, "! Too many failed attempts. Try later."

    cache.set(f"login_attempts:{email}", attempts + 1, timeout=300)
    return True, "Success."

def set_zero_attempts(email):
    cache.delete(f"login_attempts:{email}")