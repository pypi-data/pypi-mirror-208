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

from dataclasses import dataclass, field

from . import http1, http2, http3
from ._factories import HTTPOverQUICClientFactory, HTTPOverTCPFactory


@dataclass
class ProtocolRegistry:
    """
    Registry of protocol implementations
    """

    #: HTTP/1 client implementations
    http1_clients: dict[str, HTTPOverTCPFactory] = field(default_factory=dict)

    #: HTTP/2 client implementations
    http2_clients: dict[str, HTTPOverTCPFactory] = field(default_factory=dict)

    #: HTTP/3 client implementations
    http3_clients: dict[str, HTTPOverQUICClientFactory] = field(default_factory=dict)

    def load(self) -> None:
        """
        Load known implementations.
        """
        self.http1_clients["default"] = http1.HTTP1ClientFactory()
        self.http2_clients["default"] = http2.HTTP2ClientFactory()
        self.http3_clients["default"] = http3.HTTP3ClientFactory()
