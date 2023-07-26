import os
import sys
import toml
from packaging import version
from pathlib import Path
from google.cloud import artifactregistry_v1beta2

VERSION_FILE = f"VERSION-{os.getenv('CI_COMMIT_REF_SLUG')}"
ARTIFACT_PROJECT_ID = os.getenv('ARTIFACT_PROJECT_ID')
ARTIFACT_REGION = os.getenv('ARTIFACT_REGION')
ARTIFACT_IMAGE_NAME = os.getenv('ARTIFACT_IMAGE_NAME')


def save_version(new_version):
    print(f"[INFO] Updating {VERSION_FILE} to {new_version}")
    with open(VERSION_FILE, 'w') as f:
        f.write(new_version)
    with open(VERSION_FILE, 'r') as f:
        VERIFY_VERSION = f.readline().strip()
    if new_version != VERIFY_VERSION:
        print("[ERROR] New version was not saved. Please fix before continuing.")
        sys.exit(1)
    else:
        print(f"[INFO] {VERSION_FILE} update successful")


if os.getenv('CI_COMMIT_BRANCH') != os.getenv('CI_DEFAULT_BRANCH'):
    save_version(os.getenv('CI_COMMIT_REF_SLUG'))
    sys.exit()


def increment(ver):
    ver = version.parse(ver)
    next_ver = version.parse(f"{ver.major}.{ver.minor}.{ver.micro + 1}")
    return str(next_ver)


def find_tag(tag):
    client = artifactregistry_v1beta2.ArtifactRegistryClient()
    parent = f"projects/{ARTIFACT_PROJECT_ID}/locations/{ARTIFACT_REGION}/repositories/{ARTIFACT_IMAGE_NAME}"
    request = artifactregistry_v1beta2.ListTagsRequest({'parent': parent})
    response = client.list_tags(request=request)
    for tag in response:
        if tag.endswith(tag):
            return tag
    return None


def latest_version(ver1, ver2):
    return str(max(version.parse(ver1), version.parse(ver2)))


if not Path('pyproject.toml').is_file():
    print("[ERROR] pyproject.toml does not exist.")
    sys.exit(1)

with open('pyproject.toml') as f:
    pyproject = toml.load(f)
    VERSION = pyproject.get('tool', {}).get('poetry', {}).get('version')

if not VERSION:
    print("[ERROR] pyproject.toml does not contain a version property")
    sys.exit(1)

print(f"[INFO] Version in pyproject.toml: {VERSION}")

CURRENT = VERSION
if Path(VERSION_FILE).is_file():
    with open(VERSION_FILE, 'r') as f:
        CURRENT = f.readline().strip()
    print(f"[INFO] Version in {VERSION_FILE}: {CURRENT}")
    LATEST = latest_version(VERSION, CURRENT)
    if LATEST == VERSION:
        CURRENT = VERSION
        print(
            f"[INFO] Version in pyproject.toml ({VERSION}) is greater than the version in {VERSION_FILE} ({CURRENT}). Using {VERSION} as current.")
    else:
        if not CURRENT:
            print(f"[WARN] File {VERSION_FILE} empty. Setting current version to {VERSION}")
            CURRENT = VERSION
else:
    print(f"[WARN] File {VERSION_FILE} does not exist. Setting current version to {CURRENT}")

print(f"[INFO] Using version {CURRENT} as the current version")
NEXT = increment(CURRENT)
print(f"[INFO] Incrementing {CURRENT} to {NEXT}")

print(f"[INFO] Checking if image tag {NEXT} already exists...")
EXISTS = find_tag(NEXT)
while EXISTS is not None:
    NEXT = increment(NEXT)
    print(f"[WARN] Version {EXISTS} is already a used image tag. Incrementing to {NEXT}.")
    EXISTS = find_tag(NEXT)

print(f"[INFO] Using Image tag {NEXT}")
save_version(NEXT)
