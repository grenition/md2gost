import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestProductionComposeConfig(unittest.TestCase):
    def test_compose_does_not_mount_local_setup_py(self):
        compose_text = (PROJECT_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertNotIn("./setup.py:/app/setup.py:ro", compose_text)

    def test_compose_exposes_configurable_infra_variables(self):
        compose_text = (PROJECT_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        expected_keys = (
            "SESSION_STORE_BACKEND",
            "STORAGE_BACKEND",
            "DATABASE_URL",
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "S3_ENDPOINT",
            "S3_REGION",
            "S3_BUCKET",
            "S3_ACCESS_KEY",
            "S3_SECRET_KEY",
            "S3_USE_SSL",
        )
        for key in expected_keys:
            self.assertIn(key, compose_text)

        self.assertIn("postgres:", compose_text)
        self.assertIn("minio:", compose_text)
        self.assertNotIn("redis:", compose_text)

    def test_env_template_contains_required_keys(self):
        env_template = (PROJECT_ROOT / ".env.production.example").read_text(encoding="utf-8")
        expected_keys = (
            "GATEWAY_PORT=",
            "DOCX_SERVICE_URL=",
            "FILE_SERVICE_URL=",
            "SESSION_SERVICE_URL=",
            "SESSION_STORE_BACKEND=",
            "STORAGE_BACKEND=",
            "DATABASE_URL=",
            "POSTGRES_DB=",
            "POSTGRES_USER=",
            "POSTGRES_PASSWORD=",
            "S3_ENDPOINT=",
            "S3_REGION=",
            "S3_BUCKET=",
            "S3_ACCESS_KEY=",
            "S3_SECRET_KEY=",
            "S3_USE_SSL=",
        )
        for key in expected_keys:
            self.assertIn(key, env_template)


if __name__ == "__main__":
    unittest.main()
