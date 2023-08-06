# Copyright 2022 Akamai Technologies, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from ._factories import ALPNHTTPFactory, HTTPOverQUICClientFactory, HTTPOverTCPFactory
from ._protocols import (
    HTTP1Protocol,
    HTTP2Protocol,
    HTTP3Protocol,
    HTTPOverQUICProtocol,
    HTTPOverTCPProtocol,
    HTTPProtocol,
)
from ._registry import ProtocolRegistry
from .http1 import HTTP1ClientFactory
from .http2 import HTTP2ClientFactory
from .http3 import HTTP3ClientFactory

#: Global instance of :class:`ProtocolRegistry`
#:
#: Use setuptools entrypoints to register new implementations:
#: See :meth:`.ProtocolRegistry.load_entry_points` how.
#:
#: :type: ProtocolRegistry
protocol_registry = ProtocolRegistry()
protocol_registry.load()

__all__ = (
    "ALPNHTTPFactory",
    "HTTPOverQUICClientFactory",
    "HTTPOverTCPFactory",
    "HTTP1ClientFactory",
    "HTTP2ClientFactory",
    "HTTP2ClientFactory",
    "HTTP3ClientFactory",
    "HTTP1Protocol",
    "HTTP2Protocol",
    "HTTP3Protocol",
    "HTTPOverQUICProtocol",
    "HTTPOverTCPProtocol",
    "HTTPProtocol",
    "ProtocolRegistry",
)
