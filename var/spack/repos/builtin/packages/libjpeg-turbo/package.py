##############################################################################
# Copyright (c) 2013-2018, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/spack/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *


class LibjpegTurbo(Package):
    """libjpeg-turbo is a fork of the original IJG libjpeg which uses SIMD to
       accelerate baseline JPEG compression and decompression. libjpeg is a
       library that implements JPEG image encoding, decoding and
       transcoding."""
    # https://github.com/libjpeg-turbo/libjpeg-turbo/blob/master/BUILDING.md
    homepage = "https://libjpeg-turbo.org/"
    url      = "https://github.com/libjpeg-turbo/libjpeg-turbo/archive/1.5.90.tar.gz"

    version('1.5.90', '85f7f9c377b70cbf48e61726097d4efa')
    version('1.5.3', '7c82f0f6a3130ec06b8a4d0b321cbca3')
    version('1.5.0', '3fc5d9b6a8bce96161659ae7a9939257')
    version('1.3.1', '2c3a68129dac443a72815ff5bb374b05')

    provides('jpeg')

    # Can use either of these. But in the current version of the package
    # only nasm is used. In order to use yasm an environmental variable
    # NASM must be set.
    # TODO: Implement the selection between two supported assemblers.
    # depends_on("yasm", type='build')
    depends_on("nasm", type='build')
    depends_on('cmake', type='build', when="@1.5.90:")

    @when('@:1.5.3')
    def install(self, spec, prefix):
        configure('--prefix=%s' % prefix)
        make()
        make('install')

    @when('@1.5.90:')
    def install(self, spec, prefix):
        cmake_args = ['-GUnix Makefiles']
        cmake_args.extend(std_cmake_args)
        with working_dir('spack-build', create=True):
            cmake('..', *cmake_args)
            make()
            make('install')
