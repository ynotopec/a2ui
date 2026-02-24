#!/usr/bin/env python3

### A2UI Project - Quick Start Script
### Python implementation for users who prefer Python scripts

import os
import sys
import subprocess
import time
import json
from pathlib import Path

def check_command(command):
    """Check if a command is available."""
    return subprocess.run(["which", command], capture_output=True).returncode == 0

def check_service(url):
    """Check if a service is running."""
    try:
        response = subprocess.run(
            ["curl", "-s", url],
            capture_output=True,
            text=True,
            timeout=5
        )
        return response.returncode == 0
    except subprocess.TimeoutExpired:
        return False

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*50}")
    print(f"|  {title}")
    print(f"{'='*50}\n")

def main():
    print("🚀 A2UI Project - Quick Start (Python)")
    print("="*50)

    # Check requirements
    print_section("1️⃣ Verifying requirements")

    docker_available = check_command("docker")
    curl_available = check_command("curl")

    if not docker_available:
        print("❌ Docker not found. Please install Docker first.")
        return 1

    print("✅ Docker found")

    if not curl_available:
        print("❌ curl not found. Please install curl first.")
        return 1

    print("✅ curl found")

    # Check services
    print_section("2️⃣ Checking services")

    vllm_running = check_service("http://localhost:8000/v1/models")

    if vllm_running:
        print("✅ vLLM service already running (port 8000)")
    else:
        print("⚠️  Starting vLLM and Agent services...")

        # Start services
        subprocess.run(["docker", "compose", "up", "-d", "vllm"], check=True)
        print("  → vLLM starting...")

        time.sleep(5)

        subprocess.run(["docker", "compose", "up", "-d", "agent"], check=True)
        print("  → Agent starting...")

        time.sleep(3)

    print("✅ All services are ready")

    # Check model
    print_section("3️⃣ Model check")

    model_path = Path("models/Qwen2.5-72B-Instruct")
    if not model_path.exists():
        print("⚠️  Model directory not found")
        print(f"\n   Expected path: {model_path}")
        print("\n   Download options:")
        print("   1. Full HuggingFace download (16GB):")
        print("      wget https://huggingface.co/Qwen/Qwen2.5-72B-Instruct/resolve/main/anything.txt")
        print("   2. Use HF cache: ./hf_cache")
    else:
        print(f"✅ Model directory found: {model_path}")

    # Quick tests
    print_section("4️⃣ Quick tests")

    # Test vLLM
    print("Testing: GET http://localhost:8000/v1/models")
    response = subprocess.run(
        ["curl", "-s", "http://localhost:8000/v1/models"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if response.returncode == 0:
        print(response.stdout[:200] if len(response.stdout) > 200 else response.stdout)
    else:
        print("⚠️  vLLM test failed")

    # Test agent
    print("\nTesting: GET /a2ui?q=Hello")
    print("Response preview:")
    response = subprocess.run(
        ["curl", "-s", "http://localhost:8080/a2ui?q=Hello"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if response.returncode == 0:
        parts = response.stdout.split('\n')[:3]
        print(json_str := '\n'.join(f'    {line}' for line in parts))
    else:
        print("⚠️  Agent test failed")

    # Show status
    print_section("5️⃣ Service status")

    result = subprocess.run(
        ["docker", "compose", "ps"],
        capture_output=True,
        text=True
    )
    print(result.stdout if result.returncode == 0 else "⚠️  Could not get status")

    # Documentation
    print_section("📚 Documentation")

    print("Available documentation files:")
    docs_files = {
        "README.md": "Quick start guide",
        "docs/overview.md": "Technical overview",
        "docs/architecture.md": "System architecture",
        "USE_CASE.md": "Use case scenarios",
        "VALUE.md": "Business value & ROI",
        "INNOVATION_STATUS.md": "Maturity roadmap"
    }

    for file, desc in docs_files.items():
        exists = "✅" if Path(file).exists() else "❌"
        print(f"{exists} {file:<40} - {desc}")

    print("\n📚 Client interface:")
    print("   Open index.html in your browser")
    print("   Or check client/public/index.html")

    print("\n📊 Quick API tests:")
    print("   curl http://localhost:8000/v1/models")
    print("   curl 'http://localhost:8080/a2ui?q=Test'")
    print("   curl -N 'http://localhost:8080/a2ui?q=Astuce'")

    return 0

if __name__ == "__main__":
    sys.exit(main())