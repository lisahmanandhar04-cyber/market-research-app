from pydantic import BaseModel, Field


class Source(BaseModel):
    title: str
    url: str
    snippet: str = ""


class ResearchFindings(BaseModel):
    query: str
    sources: list[Source] = Field(default_factory=list)
    is_sample_data: bool = False  # True when we fall back to sample data
    notes: str = ""               # Anything the researcher couldn't find


class Competitor(BaseModel):
    name: str
    description: str


class Brief(BaseModel):
    summary: str
    competitors: list[Competitor] = Field(default_factory=list)  # max 2
    key_observations: list[str] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


class CriticFeedback(BaseModel):
    approved: bool
    issues: list[str] = Field(default_factory=list)
    requested_changes: list[str] = Field(default_factory=list)


class ResearchState(BaseModel):
    """Everything passed between roles, in one place."""
    query: str
    findings: ResearchFindings | None = None
    draft: Brief | None = None
    feedback: CriticFeedback | None = None
    revision_count: int = 0