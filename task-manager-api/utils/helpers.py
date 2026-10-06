from datetime import datetime, timezone
import re
import uuid

VALID_STATUSES = ["pending", "in_progress", "done", "cancelled"]
VALID_ROLES = ["user", "admin", "manager"]
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 4
MIN_PRIORITY = 1
MAX_PRIORITY = 5
HIGH_PRIORITY_MAX = 2
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = "#000000"
CLOSED_STATUSES = ("done", "cancelled")


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_date(date_obj):
    if date_obj:
        return str(date_obj)
    return None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return re.match(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", email) is not None


def sanitize_string(value):
    if value:
        return value.strip()
    return value


def generate_id():
    return str(uuid.uuid4())


def log_action(action, details=None):
    timestamp = utc_now()
    print(f"[{timestamp}] ACTION: {action}")
    if details:
        print(f"  DETAILS: {details}")


def parse_date(date_string):
    for pattern in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_string, pattern)
        except ValueError:
            continue
    return None


def is_valid_color(color):
    return bool(color) and len(color) == 7 and color[0] == "#"


def process_task_data(data, existing_task=None):
    result = {}

    if "title" in data:
        title = data["title"]
        if title:
            title = title.strip()
            if MIN_TITLE_LENGTH <= len(title) <= MAX_TITLE_LENGTH:
                result["title"] = title
            else:
                return None, "Título deve ter entre 3 e 200 caracteres"
        else:
            return None, "Título não pode ser vazio"

    if "description" in data:
        result["description"] = data["description"]

    if "status" in data:
        if data["status"] in VALID_STATUSES:
            result["status"] = data["status"]
        else:
            return None, "Status inválido"

    if "priority" in data:
        try:
            priority = int(data["priority"])
        except (TypeError, ValueError):
            return None, "Prioridade inválida"
        if MIN_PRIORITY <= priority <= MAX_PRIORITY:
            result["priority"] = priority
        else:
            return None, "Prioridade deve ser entre 1 e 5"

    if "due_date" in data:
        if data["due_date"]:
            parsed = parse_date(data["due_date"])
            if parsed:
                result["due_date"] = parsed
            else:
                return None, "Data inválida"
        else:
            result["due_date"] = None

    if "tags" in data:
        tags = data["tags"]
        if isinstance(tags, list):
            result["tags"] = ",".join(tags)
        else:
            result["tags"] = tags

    return result, None
