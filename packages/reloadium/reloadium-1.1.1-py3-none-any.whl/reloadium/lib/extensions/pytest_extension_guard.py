import sys

from reloadium.corium.utils.comp import fix_sep

__RELOADIUM__ = True

fix_sep()


try:
    import _pytest.assertion.rewrite
except ImportError:
    class AssertionRewritingHook:
        pass

    _pytest = lambda: None  # type: ignore
    sys.modules["_pytest"] = _pytest

    _pytest.assertion = lambda: None  # type: ignore
    sys.modules["_pytest.assertion"] = _pytest.assertion

    _pytest.assertion.rewrite = lambda: None  # type: ignore
    _pytest.assertion.rewrite.AssertionRewritingHook = AssertionRewritingHook  # type: ignore
    sys.modules["_pytest.assertion.rewrite"] = _pytest.assertion.rewrite
