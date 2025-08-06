from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal


# Enums for role-based access control
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"
    EXTERNAL = "external"
    TEAM_MEMBER = "team_member"


class ToolCategory(str, Enum):
    APP = "app"
    PLATFORM = "platform"
    CONTROL_BOARD = "control_board"


class OnboardingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class InductionStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"
    LINK = "link"


# Core User model
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    project_memberships: List["ProjectMembership"] = Relationship(back_populates="user")
    created_projects: List["Project"] = Relationship(back_populates="created_by")
    new_starter_requests: List["NewStarterRequest"] = Relationship(back_populates="manager")
    onboarding_details: List["OnboardingDetails"] = Relationship(back_populates="new_starter")
    induction_progress: List["InductionProgress"] = Relationship(back_populates="user")


# Project model
class Project(SQLModel, table=True):
    __tablename__ = "projects"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    code: str = Field(unique=True, max_length=20)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    created_by_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    settings: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Relationships
    created_by: User = Relationship(back_populates="created_projects")
    memberships: List["ProjectMembership"] = Relationship(back_populates="project")
    tools: List["ProjectTool"] = Relationship(back_populates="project")
    new_starter_requests: List["NewStarterRequest"] = Relationship(back_populates="project")
    induction_content: List["InductionChapter"] = Relationship(back_populates="project")
    dashboards: List["Dashboard"] = Relationship(back_populates="project")


# Project membership with role-based access
class ProjectMembership(SQLModel, table=True):
    __tablename__ = "project_memberships"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    project_id: int = Field(foreign_key="projects.id")
    role: UserRole = Field(default=UserRole.TEAM_MEMBER)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    user: User = Relationship(back_populates="project_memberships")
    project: Project = Relationship(back_populates="memberships")


# Tool catalog
class Tool(SQLModel, table=True):
    __tablename__ = "tools"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    category: ToolCategory
    icon_url: Optional[str] = Field(default=None, max_length=500)
    external_url: Optional[str] = Field(default=None, max_length=500)
    is_embeddable: bool = Field(default=False)
    embed_config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    project_tools: List["ProjectTool"] = Relationship(back_populates="tool")


# Project-specific tool assignments
class ProjectTool(SQLModel, table=True):
    __tablename__ = "project_tools"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    tool_id: int = Field(foreign_key="tools.id")
    is_enabled: bool = Field(default=True)
    configuration: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    required_roles: List[str] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    project: Project = Relationship(back_populates="tools")
    tool: Tool = Relationship(back_populates="project_tools")


# New Starter Request (Manager creates)
class NewStarterRequest(SQLModel, table=True):
    __tablename__ = "new_starter_requests"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    manager_id: int = Field(foreign_key="users.id")
    starter_email: str = Field(max_length=255)
    starter_first_name: str = Field(max_length=100)
    starter_last_name: str = Field(max_length=100)
    start_date: datetime
    role: UserRole = Field(default=UserRole.TEAM_MEMBER)
    department: Optional[str] = Field(default=None, max_length=100)
    position: Optional[str] = Field(default=None, max_length=100)
    line_manager: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None, max_length=1000)
    status: OnboardingStatus = Field(default=OnboardingStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    project: Project = Relationship(back_populates="new_starter_requests")
    manager: User = Relationship(back_populates="new_starter_requests")
    onboarding_details: Optional["OnboardingDetails"] = Relationship(back_populates="request")


# Onboarding Details (New Starter completes)
class OnboardingDetails(SQLModel, table=True):
    __tablename__ = "onboarding_details"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="new_starter_requests.id", unique=True)
    new_starter_id: int = Field(foreign_key="users.id")
    phone_number: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    emergency_contact_name: Optional[str] = Field(default=None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(default=None, max_length=20)
    previous_experience: Optional[str] = Field(default=None, max_length=2000)
    skills: List[str] = Field(default=[], sa_column=Column(JSON))
    certifications: List[str] = Field(default=[], sa_column=Column(JSON))
    accessibility_requirements: Optional[str] = Field(default=None, max_length=1000)
    dietary_requirements: Optional[str] = Field(default=None, max_length=500)
    additional_info: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    request: NewStarterRequest = Relationship(back_populates="onboarding_details")
    new_starter: User = Relationship(back_populates="onboarding_details")


# Induction content structure
class InductionChapter(SQLModel, table=True):
    __tablename__ = "induction_chapters"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    order_index: int = Field(default=0)
    is_required: bool = Field(default=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    project: Project = Relationship(back_populates="induction_content")
    sections: List["InductionSection"] = Relationship(back_populates="chapter")


class InductionSection(SQLModel, table=True):
    __tablename__ = "induction_sections"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    chapter_id: int = Field(foreign_key="induction_chapters.id")
    title: str = Field(max_length=200)
    order_index: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    chapter: InductionChapter = Relationship(back_populates="sections")
    content_items: List["InductionContent"] = Relationship(back_populates="section")


class InductionContent(SQLModel, table=True):
    __tablename__ = "induction_content"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    section_id: int = Field(foreign_key="induction_sections.id")
    content_type: ContentType
    title: Optional[str] = Field(default=None, max_length=200)
    content: Optional[str] = Field(default=None, max_length=10000)  # Rich text, file path, URL
    url: Optional[str] = Field(default=None, max_length=500)
    file_path: Optional[str] = Field(default=None, max_length=500)
    embed_code: Optional[str] = Field(default=None, max_length=2000)
    content_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    order_index: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    section: InductionSection = Relationship(back_populates="content_items")


# User induction progress tracking
class InductionProgress(SQLModel, table=True):
    __tablename__ = "induction_progress"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    chapter_id: int = Field(foreign_key="induction_chapters.id")
    status: InductionStatus = Field(default=InductionStatus.NOT_STARTED)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    completion_percentage: Decimal = Field(default=Decimal("0"), max_digits=5, decimal_places=2)
    notes: Optional[str] = Field(default=None, max_length=1000)

    # Relationships
    user: User = Relationship(back_populates="induction_progress")


# Dashboard configuration
class Dashboard(SQLModel, table=True):
    __tablename__ = "dashboards"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    name: str = Field(max_length=200)
    type: str = Field(max_length=50)  # details, issues, changes, work_packages
    configuration: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    required_roles: List[str] = Field(default=[], sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    project: Project = Relationship(back_populates="dashboards")


# Non-persistent schemas for validation and API
class UserCreate(SQLModel, table=False):
    email: str = Field(max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)


class UserUpdate(SQLModel, table=False):
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)


class ProjectCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    code: str = Field(max_length=20)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)


class ProjectUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    settings: Optional[Dict[str, Any]] = Field(default=None)


class ProjectMembershipCreate(SQLModel, table=False):
    user_id: int
    project_id: int
    role: UserRole = Field(default=UserRole.TEAM_MEMBER)


class ToolCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    category: ToolCategory
    icon_url: Optional[str] = Field(default=None, max_length=500)
    external_url: Optional[str] = Field(default=None, max_length=500)
    is_embeddable: bool = Field(default=False)
    embed_config: Dict[str, Any] = Field(default={})


class NewStarterRequestCreate(SQLModel, table=False):
    project_id: int
    starter_email: str = Field(max_length=255)
    starter_first_name: str = Field(max_length=100)
    starter_last_name: str = Field(max_length=100)
    start_date: datetime
    role: UserRole = Field(default=UserRole.TEAM_MEMBER)
    department: Optional[str] = Field(default=None, max_length=100)
    position: Optional[str] = Field(default=None, max_length=100)
    line_manager: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None, max_length=1000)


class OnboardingDetailsCreate(SQLModel, table=False):
    request_id: int
    phone_number: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    emergency_contact_name: Optional[str] = Field(default=None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(default=None, max_length=20)
    previous_experience: Optional[str] = Field(default=None, max_length=2000)
    skills: List[str] = Field(default=[])
    certifications: List[str] = Field(default=[])
    accessibility_requirements: Optional[str] = Field(default=None, max_length=1000)
    dietary_requirements: Optional[str] = Field(default=None, max_length=500)
    additional_info: Dict[str, Any] = Field(default={})


class InductionChapterCreate(SQLModel, table=False):
    project_id: int
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    order_index: int = Field(default=0)
    is_required: bool = Field(default=True)


class InductionSectionCreate(SQLModel, table=False):
    chapter_id: int
    title: str = Field(max_length=200)
    order_index: int = Field(default=0)


class InductionContentCreate(SQLModel, table=False):
    section_id: int
    content_type: ContentType
    title: Optional[str] = Field(default=None, max_length=200)
    content: Optional[str] = Field(default=None, max_length=10000)
    url: Optional[str] = Field(default=None, max_length=500)
    file_path: Optional[str] = Field(default=None, max_length=500)
    embed_code: Optional[str] = Field(default=None, max_length=2000)
    content_metadata: Dict[str, Any] = Field(default={})
    order_index: int = Field(default=0)


class DashboardCreate(SQLModel, table=False):
    project_id: int
    name: str = Field(max_length=200)
    type: str = Field(max_length=50)
    configuration: Dict[str, Any] = Field(default={})
    required_roles: List[str] = Field(default=[])
