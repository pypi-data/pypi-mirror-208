# pylint: disable=W0622
"""cubicweb_web application packaging information"""


modname = "web"
distname = "cubicweb-web"

numversion = (1, 0, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "Legacy component for web application"
web = "https://forge.extranet.logilab.fr/cubicweb/cubes/web"

__depends__ = {"cubicweb": ">= 4.0.0,<5.0.0", "yams": ">= 0.48"}
__recommends__ = {}

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python :: 3",
    "Programming Language :: JavaScript",
]
