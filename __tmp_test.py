from pathlib import Path
import tempfile
from src.parser import parse_file, parse_inline
from src.validator import validate


def write_md(content):
    p = Path(tempfile.mkdtemp()) / "t.md"
    p.write_text(content, encoding="utf-8")
    return p


# Test 1: missing name -> error
bad = write_md('''---
{
	"title": "Only Title"
}
---

# Section

Content here.
''')
doc = parse_file(bad)
errs, warns = validate(doc)
print("Test1 missing name -> errors:", errs)
assert any("name" in e for e in errs), "missing name should error"

# Test 2: invalid color -> error
bad2 = write_md('''---
{
	"name": "N", "title": "T", "primary_color": "not-a-color"
}
---

# Section

Content.
''')
doc2 = parse_file(bad2)
errs2, warns2 = validate(doc2)
print("Test2 invalid color -> errors:", errs2)
assert any("color" in e for e in errs2), "invalid color should error"

# Test 3: missing contact fields -> warnings only
bad3 = write_md('''---
{
	"name": "N", "title": "T"
}
---

# Section

Content.
''')
doc3 = parse_file(bad3)
errs3, warns3 = validate(doc3)
print("Test3 missing contact -> errors:", errs3, "warnings:", warns3)
assert errs3 == [], "should have no errors"
assert any("Email" in w for w in warns3), "should warn missing email"

# Test 4: valid full doc -> clean
good = write_md('''---
{
	"name": "N", "title": "T", "email": "a@b.com", "phone": "123", "location": "Loc",
	"github": "https://g.com", "linkedin": "https://l.com", "portfolio": "https://p.com"
}
---

# Section

## Subsection

Para with **bold** and *italic* and `code` and [link](https://x.com).

- item one
- item two
''')
doc4 = parse_file(good)
errs4, warns4 = validate(doc4)
print("Test4 valid -> errors:", errs4, "warnings:", warns4)
assert errs4 == [] and warns4 == [], "valid doc should be clean"

# Test 5: inline parsing
spans = parse_inline('**b** *i* `c` [l](http://x.com) plain')
print("Test5 spans:", [(s.text, s.bold, s.italic, s.code, s.url) for s in spans])
assert any(s.bold and s.text == "b" for s in spans)
assert any(s.italic and s.text == "i" for s in spans)
assert any(s.code and s.text == "c" for s in spans)
link = [s for s in spans if s.url]
assert link and link[0].url == "http://x.com" and link[0].text == "l"

# Test 6: invalid JSON metadata -> exception
bad6 = write_md('''---
{ not valid json }
---
# Section

Content.
''')
try:
    parse_file(bad6)
    print("Test6 FAILED: no exception raised")
    assert False
except ValueError as e:
    print("Test6 invalid JSON -> ValueError:", e)

print("ALL TESTS PASSED")
