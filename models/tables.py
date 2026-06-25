from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Table:
	id: Optional[int] = None
	number: Optional[int] = None
	capacity: Optional[int] = None
	location: Optional[str] = None
	is_outdoor: bool = False
	is_reserved: bool = False
	description: Optional[str] = None
	created_at: Optional[datetime] = None
