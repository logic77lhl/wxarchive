from wxarchive.article import safe_filename
from wxarchive.render import clean_markdown


def test_clean_markdown_drops_empty_headings():
    assert clean_markdown("正文\n\n###\n\n下一段") == "正文\n\n下一段"


def test_clean_markdown_collapses_nested_numbering():
    assert clean_markdown("2. 1. **小标题**") == "2. **小标题**"


def test_clean_markdown_keeps_list_together():
    text = "- 一\n\n- 二\n\n- 三"
    assert clean_markdown(text) == "- 一\n- 二\n- 三"


def test_clean_markdown_keeps_paragraph_gaps():
    text = "第一段\n\n第二段"
    assert clean_markdown(text) == "第一段\n\n第二段"


def test_safe_filename_strips_illegal_chars():
    assert safe_filename('a/b:c*d?e"f<g>h|i') == "a_b_c_d_e_f_g_h_i"


def test_safe_filename_truncates_and_falls_back():
    assert len(safe_filename("长" * 100, maxlen=20)) == 20
    assert safe_filename("   ") == "untitled"
