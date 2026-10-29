"""Phase 18 的前端静态契约；真实浏览器点击另行验收。"""

from app.main import home


def test_web_ui_is_responsive_and_has_visible_status():
    html = home()
    assert "@media(max-width:700px)" in html
    assert "role='status'" in html
    assert "Please enter English text before redacting." in html
    assert "console.log" not in html


def test_javascript_calls_backend_instead_of_matching_names():
    html = home()
    assert "fetch('/api/redact'" in html
    assert "keyword" not in html.lower()
