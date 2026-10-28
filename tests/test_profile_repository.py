import hashlib
import tempfile
import unittest

from pathlib import Path

from src.persistence.profile_repository import ProfileRepository
from src.schemas.candidate import CandidateProfile


class TestProfileRepository(unittest.TestCase):
    def test_save_and_retrieve_profile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_profiles.db"

            repository = ProfileRepository(db_path)
            repository.initialize()

            profile = CandidateProfile(
                professional_headline="Senior Backend Engineer",
                skills=["Go", "AWS", "Kafka"],
            )

            source_hash = hashlib.sha256(
                b"sample resume"
            ).hexdigest()

            repository.save_profile(
                candidate_id="candidate-001",
                source_sha256=source_hash,
                profile=profile,
            )

            retrieved = repository.get_profile(
                candidate_id="candidate-001",
                source_sha256=source_hash,
            )

            self.assertIsNotNone(retrieved)
            self.assertEqual(
                retrieved.professional_headline,
                "Senior Backend Engineer",
            )
            self.assertEqual(
                retrieved.skills,
                ["Go", "AWS", "Kafka"],
            )

    def test_cache_miss_for_different_resume_hash(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = ProfileRepository(
                Path(temp_dir) / "test_profiles.db"
            )
            repository.initialize()

            profile = CandidateProfile(
                professional_headline="Software Engineer"
            )

            repository.save_profile(
                candidate_id="candidate-001",
                source_sha256="hash-version-1",
                profile=profile,
            )

            result = repository.get_profile(
                candidate_id="candidate-001",
                source_sha256="hash-version-2",
            )

            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
