import sys
import pytest

from pymetabiosis.import_hook import install
from pymetabiosis.wrapper import applevel


def inject_spam():
    # Creates a spam module in CPython.
    applevel('''
import sys, types
m = types.ModuleType('spam')
m.x = 1
sys.modules['spam'] = m
''', noconvert=False)

@pytest.fixture(scope="function")
def import_hook(request):
    inject_spam()
    uninstall = install()
    request.addfinalizer(uninstall)

def test_pypy_cannot_import_spam():
    # Without the import hook, this should raise an ImportError.
    with pytest.raises(ImportError):
        import spam    
     
def test_import_hook_imports_cpython_spam(import_hook):
    import spam
    assert spam.__name__ == 'spam'
    assert spam.x == 1

    with pytest.raises(ImportError):
        # Should not import.
        import eggs_and_ham
    # Cleanup.
    del sys.modules['spam']

def test_import_hook_is_correctly_uninstalled():
    # Given
    inject_spam()
    uninstall = install()
    
    # When.
    uninstall()

    with pytest.raises(ImportError):
        import spam
