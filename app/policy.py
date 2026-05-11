import yaml
import os

_policy = None


def load_policy(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "policy.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def get_policy():
    global _policy
    if _policy is None:
        _policy = load_policy()
    return _policy
