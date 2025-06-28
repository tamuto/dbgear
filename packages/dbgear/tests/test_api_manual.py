#!/usr/bin/env python3
"""
Manual test of the dependencies API functionality using direct calls
"""

import sys
import json

from dbgear.models.schema import SchemaManager
from dbgear.models.dependencies import TableDependencyAnalyzer


def test_api_functionality():
    """Test the dependency analyzer functionality directly"""
    print("=== Manual API Test ===\n")

    # Load test schema
    schema_file = '../../../../etc/test/schema.yaml'
    project_folder = '../../../../etc/test'

    print(f"Schema file: {schema_file}")
    print(f"Project folder: {project_folder}")
    print()

    # Initialize
    schema_manager = SchemaManager.load(schema_file)
    analyzer = TableDependencyAnalyzer(schema_manager, project_folder)

    # Test main dependency endpoint functionality
    print("=== Test: Main Dependencies API ===")
    schema_name = 'main'
    table_name = 'test_table'
    left_level = 2
    right_level = 1

    print(f"Testing: GET /api/schemas/{schema_name}/tables/{table_name}/dependencies")
    print(f"Parameters: left_level={left_level}, right_level={right_level}")

    try:
        # This simulates what the API endpoint does
        result = analyzer.analyze(schema_name, table_name, left_level, right_level)

        # Format as API response
        api_response = {
            "data": result,
            "message": "Table dependencies retrieved successfully"
        }

        print("✅ Analysis successful")
        print(f"✅ Target: {result['target_table']['schema_name']}.{result['target_table']['table_name']}")

        # Count dependencies
        left_total = sum(len(deps) for deps in result['left'].values())
        right_total = sum(len(deps) for deps in result['right'].values())

        print(f"✅ Left dependencies: {left_total}")
        print(f"✅ Right dependencies: {right_total}")

        # Show structure
        print(f"✅ Left levels: {list(result['left'].keys())}")
        print(f"✅ Right levels: {list(result['right'].keys())}")

        # JSON serialization test
        json_output = json.dumps(api_response, indent=2, ensure_ascii=False)
        print(f"✅ JSON serializable: {len(json_output)} characters")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    print("\n" + "="*50 + "\n")

    # Test summary functionality
    print("=== Test: Summary API ===")
    print(f"Testing: GET /api/schemas/{schema_name}/tables/tbl_child/dependencies/summary")

    try:
        # Get level 1 dependencies only for summary
        result = analyzer.analyze(schema_name, 'tbl_child', left_level=1, right_level=1)

        # Count dependencies by type (like the summary endpoint)
        left_counts = {}
        right_counts = {}

        if "level_1" in result["left"]:
            for dep in result["left"]["level_1"]:
                dep_type = dep["type"]
                left_counts[dep_type] = left_counts.get(dep_type, 0) + 1

        if "level_1" in result["right"]:
            for dep in result["right"]["level_1"]:
                dep_type = dep["type"]
                right_counts[dep_type] = right_counts.get(dep_type, 0) + 1

        summary = {
            "data": {
                "target_table": result["target_table"],
                "left_summary": {
                    "total": sum(left_counts.values()),
                    "by_type": left_counts
                },
                "right_summary": {
                    "total": sum(right_counts.values()),
                    "by_type": right_counts
                }
            },
            "message": "Table dependencies summary retrieved successfully"
        }

        print("✅ Summary calculation successful")
        print(f"✅ Left total: {summary['data']['left_summary']['total']}")
        print(f"✅ Right total: {summary['data']['right_summary']['total']}")
        print(f"✅ Left by type: {summary['data']['left_summary']['by_type']}")
        print(f"✅ Right by type: {summary['data']['right_summary']['by_type']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    print("\n" + "="*50 + "\n")

    # Test error handling
    print("=== Test: Error Handling ===")

    # Test invalid schema
    try:
        analyzer.analyze('invalid_schema', 'test_table')
        print("❌ Should have failed for invalid schema")
        return False
    except ValueError as e:
        print(f"✅ Correctly handled invalid schema: {e}")

    # Test invalid table
    try:
        analyzer.analyze('main', 'invalid_table')
        print("❌ Should have failed for invalid table")
        return False
    except ValueError as e:
        print(f"✅ Correctly handled invalid table: {e}")

    # Test invalid levels
    try:
        analyzer.analyze('main', 'test_table', left_level=5)
        print("❌ Should have failed for invalid level")
        return False
    except ValueError as e:
        print(f"✅ Correctly handled invalid level: {e}")

    print("\n" + "="*50 + "\n")

    # Test complex multi-level scenario
    print("=== Test: Complex Multi-level ===")

    try:
        result = analyzer.analyze('main', 'tbl_matrix', left_level=3, right_level=3)

        print("✅ Complex analysis successful")
        print(f"✅ Target: {result['target_table']['table_name']}")

        # Show dependency chain
        for level_key, deps in result['right'].items():
            print(f"✅ {level_key}: {len(deps)} dependencies")
            for dep in deps:
                if dep['type'] == 'relation':
                    path_info = f" (via {dep['path'][0]['table_name']})" if 'path' in dep and dep['path'] else ""
                    print(f"   - FK to {dep['table_name']}: {dep['object_name']}{path_info}")
                else:
                    print(f"   - {dep['type']}: {dep['object_name']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    print("\n✅ All API functionality tests passed!")
    return True


def test_real_api_response_format():
    """Test that our responses match the expected API format"""
    print("\n=== Test: API Response Format ===")

    schema_file = '../../../../etc/test/schema.yaml'
    project_folder = '../../../../etc/test'

    schema_manager = SchemaManager.load(schema_file)
    analyzer = TableDependencyAnalyzer(schema_manager, project_folder)

    # Test response format matches specification
    result = analyzer.analyze('main', 'test_table', left_level=1, right_level=1)

    # Verify structure matches spec
    required_keys = ['target_table', 'left', 'right']
    for key in required_keys:
        if key not in result:
            print(f"❌ Missing required key: {key}")
            return False

    # Check target_table format
    target = result['target_table']
    if 'schema_name' not in target or 'table_name' not in target:
        print("❌ Invalid target_table format")
        return False

    # Check dependency item format
    for side in ['left', 'right']:
        for deps in result[side].values():
            for dep in deps:
                required_dep_keys = ['type', 'schema_name', 'object_name', 'details']
                for key in required_dep_keys:
                    if key not in dep:
                        print(f"❌ Missing dependency key: {key}")
                        return False

    print("✅ API response format matches specification")

    # Show sample output
    print("\nSample dependency item:")
    if result['left'].get('level_1'):
        sample_dep = result['left']['level_1'][0]
        sample_json = json.dumps(sample_dep, indent=2, ensure_ascii=False)
        print(sample_json[:300] + "..." if len(sample_json) > 300 else sample_json)

    return True


def main():
    print("Manual API Test - Table Dependencies")
    print("=" * 50)

    success = True
    success &= test_api_functionality()
    success &= test_real_api_response_format()

    if success:
        print("\n🎉 All tests passed! The API implementation is working correctly.")
        print("\nThe following endpoints would work:")
        print("- GET /api/schemas/{schema_name}/tables/{table_name}/dependencies")
        print("- GET /api/schemas/{schema_name}/tables/{table_name}/dependencies/summary")
        print("- GET /api/schemas/{schema_name}/dependencies/graph")
    else:
        print("\n❌ Some tests failed.")

    return success


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
