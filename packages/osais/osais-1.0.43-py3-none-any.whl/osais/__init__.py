"""
A package for OSAIS virtual AI.
"""
__version__="1.0.43"
__author__ = "incubiq"
__email__ = "eric@incubiq.com"

from .osais import osais_isDebug
from .osais import osais_isDocker
from .osais import osais_isLocal
from .osais import osais_isVirtualAI
from .osais import osais_loadConfig
from .osais import osais_getEnv
from .osais import osais_getHarwareInfo
from .osais import osais_getDirectoryListing
from .osais import osais_downloadImage
from .osais import osais_uploadeFileToS3
from .osais import osais_getInfo
from .osais import osais_getClientID
from .osais import osais_resetGateway
from .osais import osais_authenticateAI
from .osais import osais_authenticateClient
from .osais import osais_postRequest
from .osais import osais_initParser
from .osais import osais_runAI
from .osais import osais_notify
from .osais import osais_onNotifyFileCreated
from .osais import osais_resetOSAIS
from .osais import osais_initializeAI
