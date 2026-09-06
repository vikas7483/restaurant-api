from pathlib import Path
import yaml
from openapi_spec_validator import validate_spec


def validate_openapi():
    openapi_path = Path(__file__).resolve().parent.parent / "openapi.yaml"

    with open(openapi_path, "r", encoding="utf-8") as file:
        spec = yaml.safe_load(file)

    validate_spec(spec)

    print("OpenAPI validation: PASS")


if __name__ == "__main__":
    validate_openapi()