import uuid
from datetime import datetime
import json
from sqlalchemy import Column, String, Text, DateTime, Integer, Enum as SQLEnum
from app.database import Base
import enum

class QueueItemType(str, enum.Enum):
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    TEXT_INPUT = "text_input"
    CONFIRMATION = "confirmation"

class QueueItemStatus(str, enum.Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_HUMAN = "waiting_human"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class QueueItem(Base):
    __tablename__ = "queue_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), nullable=True)  # Optional linked Task id
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    item_type = Column(SQLEnum(QueueItemType), nullable=False, default=QueueItemType.SINGLE_CHOICE)
    _options_json = Column("options", Text, nullable=True)  # JSON serialized list of options
    _response_json = Column("response_data", Text, nullable=True)  # JSON serialized user response
    status = Column(SQLEnum(QueueItemStatus), nullable=False, default=QueueItemStatus.PENDING)
    priority = Column(Integer, default=1)
    source_agent = Column(String(100), default="ai_worker")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    @property
    def options(self):
        if self._options_json:
            try:
                return json.loads(self._options_json)
            except Exception:
                return []
        return []

    @options.setter
    def options(self, value):
        if value is not None:
            self._options_json = json.dumps(value)
        else:
            self._options_json = None

    @property
    def response_data(self):
        if self._response_json:
            try:
                return json.loads(self._response_json)
            except Exception:
                return None
        return None

    @response_data.setter
    def response_data(self, value):
        if value is not None:
            self._response_json = json.dumps(value)
        else:
            self._response_json = None


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    _skills_json = Column("skills", Text, nullable=True)  # JSON array of attached skills
    schedule_cron = Column(String(100), nullable=True)  # e.g. "*/1 * * * *"
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    result_summary = Column(Text, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def skills(self):
        if self._skills_json:
            try:
                return json.loads(self._skills_json)
            except Exception:
                return []
        return []

    @skills.setter
    def skills(self, value):
        if value is not None:
            self._skills_json = json.dumps(value)
        else:
            self._skills_json = None


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(100), primary_key=True)  # e.g. "/web-search"
    name = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(50), default="Globe")  # Lucide icon name
    category = Column(String(50), default="general")
    _schema_json = Column("parameters_schema", Text, nullable=True)

    @property
    def parameters_schema(self):
        if self._schema_json:
            try:
                return json.loads(self._schema_json)
            except Exception:
                return None
        return None

    @parameters_schema.setter
    def parameters_schema(self, value):
        if value is not None:
            self._schema_json = json.dumps(value)
        else:
            self._schema_json = None
