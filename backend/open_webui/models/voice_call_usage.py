"""Reserve daily voice minutes before connecting to a metered provider."""

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from math import ceil
from time import monotonic
from zoneinfo import ZoneInfo

from sqlalchemy import Boolean, Column, Integer, String, Text, update
from sqlalchemy.exc import IntegrityError

from open_webui.internal.db import Base, get_async_db

DAILY_SECONDS = 15 * 60
EASTERN = ZoneInfo('America/New_York')


class VoiceCallUsage(Base):
    __tablename__ = 'voice_call_usage'

    user_id = Column(Text, primary_key=True)
    day = Column(String(10), primary_key=True)
    used_seconds = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False)


class VoiceLimitReached(Exception):
    pass


class VoiceCallAlreadyActive(Exception):
    pass


@dataclass(frozen=True)
class VoiceReservation:
    user_id: str
    day: str
    previous_seconds: int
    reset_in: float
    reserved_at: float

    @property
    def remaining(self) -> int:
        return DAILY_SECONDS - self.previous_seconds

    async def release(self, connected_at: float | None, ended_at: float):
        # Keep partial seconds so repeated short calls cannot evade the quota.
        seconds = min(self.remaining, ceil(max(0, ended_at - connected_at))) if connected_at is not None else 0
        async with get_async_db() as db:
            await db.execute(
                update(VoiceCallUsage)
                .where(VoiceCallUsage.user_id == self.user_id, VoiceCallUsage.day == self.day)
                .values(used_seconds=self.previous_seconds + seconds, active=False)
            )
            await db.commit()


async def reserve_voice_call(user_id: str) -> VoiceReservation:
    now = datetime.now(EASTERN)
    reserved_at = monotonic()
    day = now.date().isoformat()
    midnight = datetime.combine(now.date() + timedelta(days=1), time.min, tzinfo=EASTERN)
    reset_in = midnight.timestamp() - now.timestamp()

    # A call reserves the rest of the day's allowance. Other workers and devices see
    # the reservation immediately. A worker crash keeps the reservation until midnight.
    async with get_async_db() as db:
        try:
            db.add(VoiceCallUsage(user_id=user_id, day=day, used_seconds=0, active=True))
            await db.commit()
            return VoiceReservation(user_id, day, 0, reset_in, reserved_at)
        except IntegrityError:
            await db.rollback()

        usage = await db.get(VoiceCallUsage, (user_id, day))
        if usage is None or usage.used_seconds >= DAILY_SECONDS:
            raise VoiceLimitReached
        if usage.active:
            raise VoiceCallAlreadyActive
        current = usage.used_seconds
        result = await db.execute(
            update(VoiceCallUsage)
            .where(
                VoiceCallUsage.user_id == user_id,
                VoiceCallUsage.day == day,
                VoiceCallUsage.used_seconds == current,
                VoiceCallUsage.active.is_(False),
            )
            .values(active=True)
        )
        if result.rowcount != 1:
            raise VoiceCallAlreadyActive
        await db.commit()
        return VoiceReservation(user_id, day, current, reset_in, reserved_at)
