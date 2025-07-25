# -*- coding: utf-8 -*- #
# Copyright 2024 Google LLC. All Rights Reserved.
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
"""Flags and helpers for the compute reservation block commands."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals


def AddDescribeFlags(parser):
  """Adds flags to the parser for the describe command."""
  parser.add_argument(
      '--block-name',
      metavar='BLOCK_NAME',
      type=str,
      required=True,
      help='The name of the reservation block.')


def AddFullViewFlag(parser):
  help_text = """\
  The view type for the reservation block.
  """
  parser.add_argument(
      '--full-view',
      metavar='FULL_VIEW',
      choices={
          'BLOCK_VIEW_FULL': 'Full detailed view of the reservation block.',
          'BLOCK_VIEW_BASIC': 'Basic default view of the reservation block.',
      },
      default='BLOCK_VIEW_UNSPECIFIED',
      help=help_text,
      required=False,
  )


def AddScopeFlags(parser):
  """Adds scope flag to the parser."""
  parser.add_argument(
      '--scope',
      metavar='SCOPE',
      type=lambda x: x.lower(),
      choices={
          'all': 'Perform maintenance on all hosts in the reservation block.',
          'running': (
              'Perform maintenance only on the hosts in the reservation block'
              ' that have running VMs.'
          ),
          'unused': (
              'Perform maintenance only on the hosts in the reservation block'
              " that don't have running VMs."
          ),
      },
      help='The maintenance scope to set for the reservation block.',
  )
