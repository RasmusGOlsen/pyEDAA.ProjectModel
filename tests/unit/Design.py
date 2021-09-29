# =============================================================================
#               _____ ____    _        _
#   _ __  _   _| ____|  _ \  / \      / \
#  | '_ \| | | |  _| | | | |/ _ \    / _ \
#  | |_) | |_| | |___| |_| / ___ \  / ___ \
#  | .__/ \__, |_____|____/_/   \_\/_/   \_\
#  |_|    |___/
# ==============================================================================
# Authors:            Patrick Lehmann
#
# Python unittest:    Instantiation tests for the project model.
#
# License:
# ==============================================================================
# Copyright 2021-2021 Patrick Lehmann - Boetzingen, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ==============================================================================
#
from pathlib import Path
from unittest import TestCase

from pySystemVerilogModel import VerilogVersion, SystemVerilogVersion
from pyVHDLModel import VHDLVersion

from pyEDAA.ProjectModel import Design, File, Project


if __name__ == "__main__":
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Instantiate(TestCase):
	def test_Design(self):
		design = Design("design")

		self.assertIsNotNone(design)
		self.assertEqual(design.Name, "design")
		self.assertEqual(Path("."), design.Directory)
		self.assertIsNotNone(design.DefaultFileSet)
		self.assertEqual(1, len(design.FileSets))
		self.assertIsNotNone(design.FileSets["default"])
		self.assertIs(design.FileSets[design.DefaultFileSet.Name], design.DefaultFileSet)
		self.assertEqual(0, len(design.VHDLLibraries))

	def test_DesignWithProject(self):
		project = Project("project")
		design = Design("design", project=project)

		self.assertIs(project, design.Project)

	def test_DesignWithVersions(self):
		vhdlVersion = VHDLVersion.VHDL2019
		verilogVersion = VerilogVersion.Verilog2005
		svVersion = SystemVerilogVersion.SystemVerilog2017

		design = Design("design", vhdlVersion=vhdlVersion, verilogVersion=verilogVersion, svVersion=svVersion)

		self.assertEqual(vhdlVersion, design.VHDLVersion)
		self.assertEqual(verilogVersion, design.VerilogVersion)
		self.assertEqual(svVersion, design.SVVersion)

	def test_DesignSetProjectLater(self):
		project = Project("project")
		design = Design("design")

		design.Project = project

		self.assertIs(project, design.Project)
		
	def test_DesignSetVersionsLater(self):
		design = Design("design")

		vhdlVersion = VHDLVersion.VHDL2019
		verilogVersion = VerilogVersion.Verilog2005
		svVersion = SystemVerilogVersion.SystemVerilog2017

		design.VHDLVersion = vhdlVersion
		design.VerilogVersion = verilogVersion
		design.SVVersion = svVersion

		self.assertEqual(vhdlVersion, design.VHDLVersion)
		self.assertEqual(verilogVersion, design.VerilogVersion)
		self.assertEqual(svVersion, design.SVVersion)

# todo: test composing path

	def test_Files(self):
		project = Design("project")

		file = File(Path("example.vhdl"))
		project.AddFile(file)

		self.assertListEqual([file], [f for f in project.Files()])
