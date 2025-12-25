import re

# Test URL Pattern
# r'^categories/(?P<category_id>[^/]+)/posts/?$'
url_pattern = r'^categories/(?P<category_id>[^/]+)/posts/?$'
test_url_1 = "categories/1748720433271/posts/"
test_url_2 = "categories/1748720433271/posts"

print(f"Testing URL Pattern: {url_pattern}")
print(f"Match 1 (with slash): {bool(re.search(url_pattern, test_url_1))}")
print(f"Match 2 (no slash): {bool(re.search(url_pattern, test_url_2))}")

# Test WebSocket Pattern
# r'ws/community/(?P<room_name>[^/]+)/?$'
ws_pattern = r'ws/community/(?P<room_name>[^/]+)/?$'
test_ws_1 = "ws/community/category_1748720433271/"
test_ws_2 = "ws/community/category_1748720433271"

print(f"\nTesting WebSocket Pattern: {ws_pattern}")
print(f"Match 1 (with slash): {bool(re.search(ws_pattern, test_ws_1))}")
print(f"Match 2 (no slash): {bool(re.search(ws_pattern, test_ws_2))}")
