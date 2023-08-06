# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.policy.registry import register_propagation_nodes


path_propagators = [
    {
        # os.path is just an alias for posixpath
        "module": "posixpath",
        "method_name": "basename",
        "source": "ARG_0,KWARG:p",
        "target": "RETURN",
        "action": "REMOVE",
        "tags": ["SAFE_PATH"],
    },
    {
        "module": "posixpath",
        "method_name": "normpath",
        "source": "ARG_0,KWARG:path",
        "target": "RETURN",
        "action": "REMOVE",
    },
    {
        "module": "posix",
        "method_name": "readlink",
        "source": "ARG_0,KWARG:path",
        "target": "RETURN",
        "action": "SPLAT",
    },
    {
        "module": "urllib.parse",
        "method_name": ["quote", "quote_plus"],
        "source": "ARG_0,KWARG:string",
        "target": "RETURN",
        "action": "SPLAT",
        "tags": ["URL_ENCODED"],
    },
    {
        "module": "urllib.parse",
        "method_name": ["unquote", "unquote_plus"],
        "source": "ARG_0,KWARG:string",
        "target": "RETURN",
        "action": "SPLAT",
        "untags": ["URL_ENCODED"],
    },
]


register_propagation_nodes(path_propagators)
