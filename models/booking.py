from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Booking:
	id: Optional[int] = None
	user_id: Optional[int] = None
	table_id: Optional[int] = None
	start_time: Optional[datetime] = None
	end_time: Optional[datetime] = None
	guests: Optional[int] = None
	status: str = "pending"
	notes: Optional[str] = None
	created_at: Optional[datetime] = None
