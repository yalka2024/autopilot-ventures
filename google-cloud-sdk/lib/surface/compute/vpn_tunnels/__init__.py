# -*- coding: utf-8 -*- #
# Copyright 2014 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Commands for reading and manipulating VPN Gateways."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base


@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
class VpnTunnels(base.Group):
  """Read and manipulate Compute Engine VPN tunnels."""

  # Placeholder to indicate that a detailed_help field exists and should
  # be set outside the class definition.
  detailed_help = None


VpnTunnels.category = base.NETWORKING_CATEGORY

VpnTunnels.detailed_help = {
    'DESCRIPTION': """
        Read and manipulate Cloud VPN tunnels.

        For more information about Cloud VPN tunnels, see the
        [Cloud VPN tunnels documentation](https://cloud.google.com//network-connectivity/docs/vpn/concepts/overview).

        See also: [VPN tunnels API](https://cloud.google.com/compute/docs/reference/rest/v1/vpnTunnels).
    """,
}
