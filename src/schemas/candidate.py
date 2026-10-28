from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ContactDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class Evidence(BaseModel):
    """A source-backed fact from the candidate's original resume."""

    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    category: str
    claim: str
    source_text: str
    source_section: Optional[str] = None


class WorkExperience(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company: str
    job_title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    responsibilities: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class Education(BaseModel):
    model_config = ConfigDict(extra="forbid")

    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class Project(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: Optional[str] = None
    technologies: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class Certification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None


class CandidateProfile(BaseModel):
    """Canonical profile extracted from the original resume."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = 1
    contact: ContactDetails = Field(default_factory=ContactDetails)

    professional_headline: Optional[str] = None
    professional_summary: Optional[str] = None

    skills: list[str] = Field(default_factory=list)
    work_experience: list[WorkExperience] = Field(
        default_factory=list
    )
    education: list[Education] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[Certification] = Field(
        default_factory=list
    )

    evidence: list[Evidence] = Field(default_factory=list)
