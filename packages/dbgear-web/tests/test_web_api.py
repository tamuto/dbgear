#!/usr/bin/env python3
"""
Test script for Web API endpoints using test schema
"""

import requests
import json
import sys
import subprocess
import time
import signal
import os

def start_web_server():
    """Start the web server in background"""
    # Change to web package directory (already in correct directory when run from tests)

    # Start server with test project
    env = os.environ.copy()
    env['DBGEAR_PROJECT_PATH'] = '../../../etc/test'

    cmd = [
        'poetry', 'run', 'python', '../dbgear_web/backend.py'
    ]

    print("Starting web server...")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)

    # Wait for server to start up
    time.sleep(3)

    return process

def test_dependencies_api():
    """Test the dependencies API endpoints"""
    base_url = "http://localhost:5001/api"

    print("=== Testing Dependencies API ===\n")

    # Test 1: Basic dependencies
    print("Test 1: Basic table dependencies")
    try:
        response = requests.get(f"{base_url}/schemas/main/tables/test_table/dependencies")
        if response.status_code == 200:
            data = response.json()
            print("✅ Status: 200 OK")
            print(f"✅ Response structure: {list(data.keys())}")
            if 'data' in data:
                target = data['data']['target_table']
                print(f"✅ Target table: {target['schema_name']}.{target['table_name']}")

                left_deps = data['data']['left']
                right_deps = data['data']['right']
                print(f"✅ Left levels: {list(left_deps.keys())}")
                print(f"✅ Right levels: {list(right_deps.keys())}")

                if 'level_1' in left_deps:
                    print(f"✅ Left level 1 items: {len(left_deps['level_1'])}")
                if 'level_1' in right_deps:
                    print(f"✅ Right level 1 items: {len(right_deps['level_1'])}")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    print("\n" + "="*50 + "\n")

    # Test 2: Dependencies with custom levels
    print("Test 2: Custom level dependencies")
    try:
        response = requests.get(f"{base_url}/schemas/main/tables/test_table/dependencies?left_level=2&right_level=1")
        if response.status_code == 200:
            data = response.json()
            print("✅ Status: 200 OK")
            left_deps = data['data']['left']
            if 'level_2' in left_deps:
                print(f"✅ Level 2 dependencies found: {len(left_deps['level_2'])}")
            else:
                print("✅ No level 2 dependencies")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    print("\n" + "="*50 + "\n")

    # Test 3: Dependencies summary
    print("Test 3: Dependencies summary")
    try:
        response = requests.get(f"{base_url}/schemas/main/tables/tbl_child/dependencies/summary")
        if response.status_code == 200:
            data = response.json()
            print("✅ Status: 200 OK")
            summary = data['data']
            print(f"✅ Target: {summary['target_table']['table_name']}")
            print(f"✅ Left total: {summary['left_summary']['total']}")
            print(f"✅ Right total: {summary['right_summary']['total']}")
            print(f"✅ Left by type: {summary['left_summary']['by_type']}")
            print(f"✅ Right by type: {summary['right_summary']['by_type']}")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    print("\n" + "="*50 + "\n")

    # Test 4: Schema dependency graph
    print("Test 4: Schema dependency graph")
    try:
        response = requests.get(f"{base_url}/schemas/main/dependencies/graph?max_level=2")
        if response.status_code == 200:
            data = response.json()
            print("✅ Status: 200 OK")
            graph = data['data']
            print(f"✅ Nodes: {len(graph['nodes'])}")
            print(f"✅ Edges: {len(graph['edges'])}")
            print(f"✅ Schema: {graph['schema_name']}")
            print(f"✅ Max level: {graph['max_level']}")

            # Show some node types
            node_types = {}
            for node in graph['nodes']:
                node_type = node['type']
                node_types[node_type] = node_types.get(node_type, 0) + 1
            print(f"✅ Node types: {node_types}")

        else:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    print("\n" + "="*50 + "\n")

    # Test 5: Error handling
    print("Test 5: Error handling")

    # Test invalid schema
    try:
        response = requests.get(f"{base_url}/schemas/invalid/tables/test_table/dependencies")
        print(f"✅ Invalid schema status: {response.status_code} (expected 404)")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    # Test invalid table
    try:
        response = requests.get(f"{base_url}/schemas/main/tables/invalid_table/dependencies")
        print(f"✅ Invalid table status: {response.status_code} (expected 404)")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    # Test invalid parameters
    try:
        response = requests.get(f"{base_url}/schemas/main/tables/test_table/dependencies?left_level=5")
        print(f"✅ Invalid level status: {response.status_code} (expected 400)")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def main():
    # Start web server
    server_process = None
    try:
        server_process = start_web_server()

        # Check if server started successfully
        if server_process.poll() is not None:
            stdout, stderr = server_process.communicate()
            print(f"❌ Server failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return

        print("✅ Web server started successfully")
        print()

        # Wait a bit more for server to be fully ready
        time.sleep(2)

        # Test API endpoints
        test_dependencies_api()

    except KeyboardInterrupt:
        print("\n✋ Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up server process
        if server_process:
            print("\n🔄 Stopping web server...")
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()
            print("✅ Web server stopped")

if __name__ == "__main__":
    main()
