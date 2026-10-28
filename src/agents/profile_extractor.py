import os

from crewai import Agent, Crew, LLM, Process, Task

from src.schemas.candidate import CandidateProfile


def create_profile_extraction_crew() -> Crew:
    llm = LLM(
        model=os.getenv(
            "PROFILE_MODEL",
            "gemini/gemini-3.1-flash-lite",
        ),
        temperature=0,
    )

    extractor = Agent(
        role="Candidate Profile Extraction Specialist",
        goal=(
            "Extract a complete, accurate, structured candidate "
            "profile from the supplied original resume."
        ),
        backstory=(
            "You specialize in resume data extraction. You preserve "
            "the candidate's actual experience, qualifications, "
            "skills, dates, and achievements. You never invent "
            "facts or improve claims beyond what the source supports."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )

    extraction_task = Task(
        description="""
Extract the candidate profile from the resume text below.

RESUME TEXT:
{resume_text}

RULES:
1. Treat the resume as the only source of candidate facts.
2. Do not tailor the profile to a particular job description.
3. Preserve company names, job titles, dates, qualifications,
   technologies, and numerical achievements accurately.
4. Do not infer missing dates, metrics, certifications, or skills.
5. Use null for missing optional scalar fields and empty lists
   for missing collections.
6. Preserve the meaning of each responsibility and achievement.
7. Include evidence records for material claims. Each evidence
   record must have a unique evidence_id, a category, a claim,
   and source_text copied from the resume.
8. Where possible, associate work experience and project claims
   with the IDs of their supporting evidence records.
9. If a fact is ambiguous, preserve only what the source supports.
10. Return structured output matching CandidateProfile.

The profile will be reused for future job applications, so factual
accuracy is more important than persuasive wording.
""",
        expected_output=(
            "A validated CandidateProfile containing the candidate's "
            "contact details, summary, skills, work experience, "
            "education, projects, certifications, and evidence."
        ),
        agent=extractor,
        output_pydantic=CandidateProfile,
    )

    return Crew(
        agents=[extractor],
        tasks=[extraction_task],
        process=Process.sequential,
        verbose=True,
    )


def extract_candidate_profile(
    resume_text: str,
) -> CandidateProfile:
    """Extract and validate a candidate profile using CrewAI."""

    if not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    crew = create_profile_extraction_crew()

    result = crew.kickoff(
        inputs={"resume_text": resume_text}
    )

    if result.pydantic is not None:
        return CandidateProfile.model_validate(
            result.pydantic.model_dump()
        )

    # Fail safely instead of saving unstructured or invalid output.
    raise RuntimeError(
        "CrewAI did not return a CandidateProfile. "
        "Check the task's structured output and model configuration."
    )
