from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import DeliveryAttempt, Message, MessageStatus
from app.services.cache import cache_service
from app.services.queue import DLQ_QUEUE, MAIN_QUEUE, RETRY_QUEUE, queue_service


def collect_metrics(db: Session) -> dict:
    now = datetime.now(timezone.utc)
    minute_ago = now - timedelta(minutes=1)
    total = int(db.scalar(select(func.count(Message.id))) or 0)
    recent = int(db.scalar(select(func.count(Message.id)).where(Message.created_at >= minute_ago)) or 0)
    delivered = int(db.scalar(select(func.count(Message.id)).where(Message.status.in_([MessageStatus.delivered, MessageStatus.read]))) or 0)
    failed = int(db.scalar(select(func.count(Message.id)).where(Message.status.in_([MessageStatus.failed, MessageStatus.dead_lettered]))) or 0)
    dead = int(db.scalar(select(func.count(Message.id)).where(Message.status == MessageStatus.dead_lettered)) or 0)
    avg_latency = float(db.scalar(select(func.avg(Message.delivery_latency_ms)).where(Message.delivery_latency_ms.is_not(None))) or 0)
    attempts = int(db.scalar(select(func.count(DeliveryAttempt.id))) or 0)

    recent_failed = db.scalars(
        select(Message).where(Message.status.in_([MessageStatus.failed, MessageStatus.dead_lettered])).order_by(Message.updated_at.desc()).limit(8)
    ).all()

    throughput_series = []
    latency_series = []
    queue_series = []
    for idx in range(10, -1, -1):
        start = now - timedelta(minutes=idx)
        end = start + timedelta(minutes=1)
        bucket_count = int(db.scalar(select(func.count(Message.id)).where(Message.created_at >= start, Message.created_at < end)) or 0)
        bucket_latency = float(db.scalar(select(func.avg(Message.delivery_latency_ms)).where(Message.updated_at >= start, Message.updated_at < end)) or 0)
        label = start.strftime("%H:%M")
        throughput_series.append({"time": label, "messages": bucket_count})
        latency_series.append({"time": label, "latency_ms": round(bucket_latency, 2)})
        queue_series.append({"time": label, "queue_depth": queue_service.local_depth(MAIN_QUEUE)})

    success_rate = (delivered / total * 100) if total else 100.0
    failure_rate = (failed / total * 100) if total else 0.0

    return {
        "total_messages": total,
        "messages_per_second": round(recent / 60, 2),
        "queue_depth": queue_service.local_depth(MAIN_QUEUE),
        "retry_queue_count": max(queue_service.local_depth(RETRY_QUEUE), attempts - delivered - dead),
        "dead_letter_count": max(queue_service.local_depth(DLQ_QUEUE), dead),
        "active_users": cache_service.active_users(),
        "active_rooms": cache_service.active_rooms(),
        "success_rate": round(success_rate, 2),
        "average_delivery_latency_ms": round(avg_latency, 2),
        "failure_rate": round(failure_rate, 2),
        "recent_failed_messages": [
            {
                "id": msg.id,
                "room_id": msg.room_id,
                "status": msg.status.value,
                "retry_count": msg.retry_count,
                "failure_reason": msg.failure_reason,
                "sequence_number": msg.sequence_number,
            }
            for msg in recent_failed
        ],
        "throughput_series": throughput_series,
        "latency_series": latency_series,
        "queue_depth_series": queue_series,
        "success_failed": [{"name": "success", "value": delivered}, {"name": "failed", "value": failed}],
    }


def generate_insights(metrics: dict) -> list[str]:
    insights: list[str] = []
    if metrics["queue_depth"] > 50 and metrics["messages_per_second"] > 5:
        insights.append("Queue depth is increasing faster than consumers are processing messages.")
    if metrics["failure_rate"] > 5:
        insights.append("Failure rate is above the safe threshold; inspect downstream delivery errors and retry pressure.")
    if metrics["retry_queue_count"] > 10:
        insights.append("Retry queue spike detected; exponential backoff is protecting the primary queue but latency may rise.")
    if metrics["dead_letter_count"] > 0:
        insights.append("Dead-lettered messages exist; review failure reasons before replaying traffic.")
    if metrics["average_delivery_latency_ms"] > 1000:
        insights.append("Average delivery latency is elevated; worker delay or downstream persistence may be saturated.")
    if not insights:
        insights.append("System is healthy: queue depth, latency, and failure rate are within safe operating bounds.")
    return insights
