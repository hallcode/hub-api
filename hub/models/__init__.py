
import os
from importlib import import_module


def import_all_models():
    """Import all modules inside 'models' folder."""
    path = __path__
    modules = []

    for root, dirs, files in os.walk(path[0]):
        if os.path.basename(root) == 'models':
            for name in files:
                if name.endswith('.py') and name != '__init__.py' and not name.endswith('_test.py'):
                    modules += ['{}.{}'.format(__name__, name[:-3])]

    for module in modules:
        import_module(module)