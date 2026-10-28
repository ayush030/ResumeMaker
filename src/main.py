from pathlib import Path

from dotenv import load_dotenv

from src.agents.profile_extractor import extract_candidate_profile
from src.ingestion.resume_parser import extract_resume_text
from src.persistence.profile_repository import ProfileRepository


load_dotenv()


def get_or_create_candidate_profile(
    resume_path: Path,
    candidate_id: str,
    repository: ProfileRepository,
):
    # Hash the source before parsing it.
    resume_hash = repository.calculate_file_hash(resume_path)

    cached_profile = repository.get_profile(
        candidate_id=candidate_id,
        source_sha256=resume_hash,
    )

    if cached_profile is not None:
        print("Cache hit: reusing the saved candidate profile.")
        return cached_profile

    print("Cache miss: extracting resume text.")
    resume_text = extract_resume_text(resume_path)

    print("Calling CrewAI profile extraction agent.")
    profile = extract_candidate_profile(resume_text)

    # Only persist a successfully parsed Pydantic profile.
    repository.save_profile(
        candidate_id=candidate_id,
        source_sha256=resume_hash,
        profile=profile,
    )

    print("Candidate profile saved successfully.")
    return profile


if __name__ == "__main__":
    repository = ProfileRepository()
    repository.initialize()

    resume_path = Path("data/base_resume.pdf")
    candidate_id = "candidate-001"

    profile = get_or_create_candidate_profile(
        resume_path=resume_path,
        candidate_id=candidate_id,
        repository=repository,
    )

    print("\nExtracted candidate profile")
    print(profile.model_dump_json(indent=2))