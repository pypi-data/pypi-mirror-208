from .coretex import *

# Internal - not for outside use
from ._logger import _initializeDefaultLogger
from ._configuration import _syncConfigWithEnv


_initializeDefaultLogger()
_syncConfigWithEnv()
