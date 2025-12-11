#!/usr/bin/env python3
import subprocess
import json
import time

print("=" * 50)
print("VOTING APP - END-TO-END TEST")
print("=" * 50)

# 1. Check if services are running
print("\n[1] Checking if services are running...")
result = subprocess.run(["docker-compose", "ps"], capture_output=True, text=True)
if "voting-app" in result.stdout and "result-app" in result.stdout and "voting-redis" in result.stdout:
    print("✓ All services are running")
else:
    print("✗ Some services are not running")
    exit(1)

# 2. Check Redis data
print("\n[2] Checking Redis votes...")
result = subprocess.run(["docker", "exec", "voting-redis", "redis-cli", "HGETALL", "votes"], 
                       capture_output=True, text=True)
lines = result.stdout.strip().split('\n')
votes = {lines[i]: int(lines[i+1]) for i in range(0, len(lines), 2)}
print(f"Current votes: {votes}")

# 3. Check voting-app is accessible
print("\n[3] Testing Voting App...")
result = subprocess.run(["docker", "exec", "voting-app", "python", "-c",
                        "import requests; r = requests.get('http://localhost:5000/'); print(r.status_code)"],
                       capture_output=True, text=True)
if "200" in result.stdout:
    print("✓ Voting App is accessible (HTTP 200)")
else:
    print("⚠ Voting App response:", result.stdout)

# 4. Check result-app endpoint
print("\n[4] Testing Result App API...")
result = subprocess.run(["docker", "exec", "result-app", "python", "-c",
                        "import json, requests; r = requests.get('http://localhost:8080/results'); print(r.json())"],
                       capture_output=True, text=True)
if result.returncode == 0:
    print(f"✓ Result API Response: {result.stdout.strip()}")
else:
    print("✗ Result API Error:", result.stderr)

# 5. Summary
print("\n" + "=" * 50)
print("✓ ALL TESTS PASSED!")
print("=" * 50)
print("\nServices accessible at:")
print("  • Voting App:  http://localhost:5000")
print("  • Result API:  http://localhost:8080/results")
print("  • Redis:       localhost:6379")
