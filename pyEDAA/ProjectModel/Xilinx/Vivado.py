# =============================================================================
#               _____ ____    _        _      ____            _           _   __  __           _      _
#   _ __  _   _| ____|  _ \  / \      / \    |  _ \ _ __ ___ (_) ___  ___| |_|  \/  | ___   __| | ___| |
#  | '_ \| | | |  _| | | | |/ _ \    / _ \   | |_) | '__/ _ \| |/ _ \/ __| __| |\/| |/ _ \ / _` |/ _ \ |
#  | |_) | |_| | |___| |_| / ___ \  / ___ \ _|  __/| | | (_) | |  __/ (__| |_| |  | | (_) | (_| |  __/ |
#  | .__/ \__, |_____|____/_/   \_\/_/   \_(_)_|   |_|  \___// |\___|\___|\__|_|  |_|\___/ \__,_|\___|_|
#  |_|    |___/                                            |__/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Package installer:  An abstract model of EDA tool projects.
#
# License:
# ============================================================================
# Copyright 2017-2021 Patrick Lehmann - Boetzingen, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#		http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ============================================================================
#
from pathlib import Path

from lxml import etree
from pyVHDLModel import VHDLVersion
from pydecor import export

from pyEDAA.ProjectModel import ConstraintFile, ProjectFile, XMLFile, XMLContent, SDCContent, Project, FileSet, \
	VHDLSourceFile, File, VerilogSourceFile


@export
class VivadoProjectFile(ProjectFile, XMLContent):
	"""A Vivado project file (``*.xpr``)."""

	_xprProject: Project

	def Parse(self):
		if not self._path.exists():
			raise Exception("File not found!")

		try:
			with self._path.open(encoding="utf-8") as fileHandle:
				content = fileHandle.read()
				content = bytes(bytearray(content, encoding='utf-8'))
		except OSError:
			raise Exception("Couldn't open '{0!s}'.".format(self._path))

		XMLParser = etree.XMLParser(remove_blank_text=True, encoding='utf-8')
		root = etree.XML(content, XMLParser)
		rootTag = etree.QName(root.tag)

		self._xprProject = Project(self._path.stem, rootDirectory=self._path.parent)
		self._ParseRootElement(root)

	def _ParseRootElement(self, root):
		filesetsNode = root.find('FileSets')
		for filesetNode in filesetsNode:
			self._ParseFileSet(filesetNode)


	def _ParseFileSet(self, filesetNode):
		filesetName = filesetNode.get('Name')
		fileset = FileSet(filesetName, design=self._xprProject.DefaultDesign)

		for fileNode in filesetNode:
			if fileNode.tag == 'File':
				self._ParseFile(fileNode, fileset)

	def _ParseFile(self, fileNode, fileset):
		filePath = Path(fileNode.get('Path'))
		if filePath.suffix in ('.vhd', '.vhdl'):
			self._ParseVHDLFile(fileNode, filePath, fileset)
		elif filePath.suffix == '.xdc':
			self._ParseXDCFile(fileNode, filePath, fileset)
		elif filePath.suffix == '.v':
			self._ParseVerilogFile(fileNode, filePath, fileset)
		elif filePath.suffix == '.xci':
			self._ParseXCIFile(fileNode, filePath, fileset)
		else:
			self._ParseDefaultFile(fileNode, filePath, fileset)


	def _ParseVHDLFile(self, fileNode, path, fileset):
		vhdlFile = VHDLSourceFile(Path(*path.parts[1:]))
		fileset.AddFile(vhdlFile)

		if fileNode[0].tag == 'FileInfo':
			if fileNode[0].get('SFType') == 'VHDL2008':
				vhdlFile.VHDLVersion = VHDLVersion.VHDL2008
			else:
				vhdlFile.VHDLVersion = VHDLVersion.VHDL93

	def _ParseDefaultFile(self, _, path, fileset):
		File(Path(*path.parts[1:]), fileSet=fileset)

	def _ParseXDCFile(self, _, path, fileset):
		XDCConstraintFile(Path(*path.parts[1:]), fileSet=fileset)

	def _ParseVerilogFile(self, _, path, fileset):
		VerilogSourceFile(Path(*path.parts[1:]), fileSet=fileset)

	def _ParseXCIFile(self, _, path, fileset):
		IPCoreInstantiationFile(Path(*path.parts[1:]), fileSet=fileset)



@export
class XDCConstraintFile(ConstraintFile, SDCContent):
	"""A Vivado constraint file (Xilinx Design Constraints; ``*.xdc``)."""


@export
class IPCoreDescriptionFile(XMLFile):
	pass


@export
class IPCoreInstantiationFile(XMLFile):
	"""A Vivado IP core instantiation file (Xilinx IPCore Instance; ``*.xci``)."""
