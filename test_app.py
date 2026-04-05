import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app

print("\n=== Testing Flask App ===")
print(f"App name: {app.name}")
print(f"\nRegistered routes:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")
print("\n=== Test Complete ===\n")
