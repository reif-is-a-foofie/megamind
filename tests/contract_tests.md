import os, sys, json

contracts_dir = "contracts"
tests_dir = "tests"

missing = []

for file in os.listdir(contracts_dir):
    if file.endswith(".json"):
        contract_name = os.path.splitext(file)[0]
        test_file = f"test_{contract_name}.py"
        if test_file not in os.listdir(tests_dir):
            missing.append(test_file)

if missing:
    print("❌ Missing test files for contracts:", ", ".join(missing))
    sys.exit(1)

print("✅ All contracts have tests.")

