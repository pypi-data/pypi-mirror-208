import sys

from reloadium.corium.lll111l11l11lll1Il1l1.l11lll11l1ll1ll1Il1l1 import ll11l1lll111l1l1Il1l1

__RELOADIUM__ = True

ll11l1lll111l1l1Il1l1()


try:
    import _pytest.assertion.rewrite
except ImportError:
    class lll11l1l111lll1lIl1l1:
        pass

    _pytest = lambda :None  # type: ignore
    sys.modules['_pytest'] = _pytest

    _pytest.assertion = lambda :None  # type: ignore
    sys.modules['_pytest.assertion'] = _pytest.assertion

    _pytest.assertion.rewrite = lambda :None  # type: ignore
    _pytest.assertion.rewrite.AssertionRewritingHook = lll11l1l111lll1lIl1l1  # type: ignore
    sys.modules['_pytest.assertion.rewrite'] = _pytest.assertion.rewrite
