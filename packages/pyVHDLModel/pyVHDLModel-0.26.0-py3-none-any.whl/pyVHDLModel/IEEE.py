# ==================================================================================================================== #
#             __     ___   _ ____  _     __  __           _      _                                                     #
#   _ __  _   \ \   / / | | |  _ \| |   |  \/  | ___   __| | ___| |                                                    #
#  | '_ \| | | \ \ / /| |_| | | | | |   | |\/| |/ _ \ / _` |/ _ \ |                                                    #
#  | |_) | |_| |\ V / |  _  | |_| | |___| |  | | (_) | (_| |  __/ |                                                    #
#  | .__/ \__, | \_/  |_| |_|____/|_____|_|  |_|\___/ \__,_|\___|_|                                                    #
#  |_|    |___/                                                                                                        #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2023 Patrick Lehmann - Boetzingen, Germany                                                            #
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany                                                               #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""This module contains library and package declarations for VHDL library ``IEEE``."""
from pyTooling.Decorators import export

from pyVHDLModel.STD import PredefinedLibrary, PredefinedPackage, PredefinedPackageBody


@export
class Ieee(PredefinedLibrary):
	def __init__(self):
		super().__init__(PACKAGES)

	def LoadSynopsysPackages(self):
		self.AddPackages(PACKAGES_SYNOPSYS)



@export
class Math_Real(PredefinedPackage):
	pass


class Math_Real_Body(PredefinedPackageBody):
	pass


class Math_Complex(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("work.math_real.all",))


class Math_Complex_Body(PredefinedPackageBody):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("work.math_real.all",))


class Std_logic_1164(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))


class Std_logic_1164_Body(PredefinedPackageBody):
	pass


class std_logic_textio(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


class Std_logic_misc(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


class Std_logic_misc_Body(PredefinedPackageBody):
	pass


class Numeric_Bit(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))


class Numeric_Bit_Body(PredefinedPackageBody):
	pass


class Numeric_Bit_Unsigned(PredefinedPackage):
	pass


class Numeric_Bit_Unsigned_Body(PredefinedPackageBody):
	def __init__(self):
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.numeric_bit.all", ))


class Numeric_Std(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


class Numeric_Std_Body(PredefinedPackageBody):
	pass

class Numeric_Std_Unsigned(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


class Numeric_Std_Unsigned_Body(PredefinedPackageBody):
	def __init__(self):
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.numeric_std.all", ))


class Fixed_Float_Types(PredefinedPackage):
	pass


class Fixed_Generic_Pkg(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.NUMERIC_STD.all", ))
		self._AddPackageClause(("IEEE.fixed_float_types.all", ))


class Fixed_Generic_Pkg_Body(PredefinedPackageBody):
	def __init__(self):
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.MATH_REAL.all", ))


class Fixed_Pkg(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddLibraryClause(("IEEE", ))


class Float_Generic_Pkg(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.NUMERIC_STD.all", ))
		self._AddPackageClause(("IEEE.fixed_float_types.all", ))


class Float_Generic_Pkg_Body(PredefinedPackageBody):
	pass


class Float_Pkg(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddLibraryClause(("IEEE", ))


PACKAGES = (
	(Math_Real, Math_Real_Body),
	(Math_Complex, Math_Complex_Body),
	(Std_logic_1164, Std_logic_1164_Body),
	(std_logic_textio, None),
	(Numeric_Bit, Numeric_Bit_Body),
	(Numeric_Bit_Unsigned, Numeric_Bit_Unsigned_Body),
	(Numeric_Std, Numeric_Std_Body),
	(Numeric_Std_Unsigned, Numeric_Std_Unsigned_Body),
	(Fixed_Float_Types, None),
	(Fixed_Generic_Pkg, Fixed_Generic_Pkg_Body),
	(Fixed_Pkg, None),
	(Float_Generic_Pkg, Float_Generic_Pkg_Body),
	(Float_Pkg, None),
)

PACKAGES_SYNOPSYS = (
	(Std_logic_misc, Std_logic_misc_Body),
)
