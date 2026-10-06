from datetime import timedelta

from flask import jsonify
from sqlalchemy import func, select

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import HIGH_PRIORITY_MAX, calculate_percentage, utc_now


def summary_report():
    total_tasks = db.session.scalar(select(func.count()).select_from(Task)) or 0
    total_users = db.session.scalar(select(func.count()).select_from(User)) or 0
    total_categories = db.session.scalar(select(func.count()).select_from(Category)) or 0

    status_rows = db.session.execute(select(Task.status, func.count()).group_by(Task.status)).all()
    by_status = {status: count for status, count in status_rows}
    priority_rows = db.session.execute(select(Task.priority, func.count()).group_by(Task.priority)).all()
    by_priority = {priority: count for priority, count in priority_rows}

    tasks = db.session.scalars(select(Task)).all()
    overdue_list = []
    for task in tasks:
        if not task.is_overdue():
            continue
        overdue_list.append({
            "id": task.id,
            "title": task.title,
            "due_date": str(task.due_date),
            "days_overdue": (utc_now() - task.due_date).days,
        })

    seven_days_ago = utc_now() - timedelta(days=7)
    recent_tasks = db.session.scalar(
        select(func.count()).select_from(Task).where(Task.created_at >= seven_days_ago)
    ) or 0
    recent_done = db.session.scalar(
        select(func.count()).select_from(Task).where(Task.status == "done", Task.updated_at >= seven_days_ago)
    ) or 0

    productivity_rows = db.session.execute(
        select(Task.user_id, Task.status, func.count()).group_by(Task.user_id, Task.status)
    ).all()
    by_user = {}
    for user_id, status, count in productivity_rows:
        by_user.setdefault(user_id, {})[status] = count

    user_stats = []
    users = db.session.scalars(select(User).order_by(User.id)).all()
    for user in users:
        bucket = by_user.get(user.id, {})
        total = sum(bucket.values())
        completed = bucket.get("done", 0)
        user_stats.append({
            "user_id": user.id,
            "user_name": user.name,
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": calculate_percentage(completed, total),
        })

    report = {
        "generated_at": str(utc_now()),
        "overview": {
            "total_tasks": total_tasks,
            "total_users": total_users,
            "total_categories": total_categories,
        },
        "tasks_by_status": {
            "pending": by_status.get("pending", 0),
            "in_progress": by_status.get("in_progress", 0),
            "done": by_status.get("done", 0),
            "cancelled": by_status.get("cancelled", 0),
        },
        "tasks_by_priority": {
            "critical": by_priority.get(1, 0),
            "high": by_priority.get(2, 0),
            "medium": by_priority.get(3, 0),
            "low": by_priority.get(4, 0),
            "minimal": by_priority.get(5, 0),
        },
        "overdue": {
            "count": len(overdue_list),
            "tasks": overdue_list,
        },
        "recent_activity": {
            "tasks_created_last_7_days": recent_tasks,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }
    return jsonify(report), 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "Usuário não encontrado"}), 404

    tasks = db.session.scalars(select(Task).where(Task.user_id == user_id)).all()
    done = pending = in_progress = cancelled = overdue = high_priority = 0
    for task in tasks:
        if task.status == "done":
            done += 1
        elif task.status == "pending":
            pending += 1
        elif task.status == "in_progress":
            in_progress += 1
        elif task.status == "cancelled":
            cancelled += 1
        if task.priority <= HIGH_PRIORITY_MAX:
            high_priority += 1
        if task.is_overdue():
            overdue += 1

    total = len(tasks)
    return jsonify({
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "statistics": {
            "total_tasks": total,
            "done": done,
            "pending": pending,
            "in_progress": in_progress,
            "cancelled": cancelled,
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": calculate_percentage(done, total),
        },
    }), 200
