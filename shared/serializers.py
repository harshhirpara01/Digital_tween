from shared.models import BehaviorLog


def behavior_log_to_dict(log: BehaviorLog) -> dict:
    return {
        "log_id": log.id,
        "user_id": log.user_id,
        "log_date": log.log_date.isoformat() if log.log_date else None,
        "log_hour": log.log_hour,
        "activity": log.activity,
        "mood": log.mood,
        "energy_level": log.energy_level,
        "study_hour": log.study_hour,
        "work_hour": log.work_hour,
        "mobile_usage_hour": log.mobile_usage_hour,
        "sleep_hours": log.sleep_hours,
        "social_intreaction_minutes": log.social_intreaction_minutes,
        "is_weekend": log.is_weekend,
        "productivy_score": log.productivy_score,
    }
