from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class User:
	id: Optional[int] = None
	name: str = ""
	email: Optional[str] = None
	phone: Optional[str] = None
	age: Optional[int] = None
	is_active: bool = True
	created_at: Optional[datetime] = None

	def as_dict(self) -> Dict[str, Any]:
		return {
			"id": self.id,
			"name": self.name,
			"email": self.email,
			"phone": self.phone,
			"age": self.age,
			"is_active": self.is_active,
			"created_at": self.created_at,
		}

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> "User":
		return cls(
			id=data.get("id"),
			name=data.get("name", ""),
			email=data.get("email"),
			phone=data.get("phone"),
			age=data.get("age"),
			is_active=data.get("is_active", True),
			created_at=data.get("created_at"),
		)

