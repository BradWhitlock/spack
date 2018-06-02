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
import os

class Macsio(CMakePackage):
    """A Multi-purpose, Application-Centric, Scalable I/O Proxy Application
    """
    tags = ['proxy-app', 'ecp-proxy-app']

    homepage = "http://llnl.github.io/MACSio"
    url = "https://github.com/LLNL/MACSio/archive/1.0.tar.gz"

    version('1.0', '90e8e00ea84af2a47bee387ad331dbde')
    version('develop', git='https://github.com/LLNL/MACSio.git',
            branch='master')
    ## FOR NOW:
    version('brad', git='https://github.com/BradWhitlock/MACSio.git',
            branch='master')

    variant('mpi', default=True, description="Build MPI plugin")
    variant('silo', default=True, description="Build with SILO plugin")
    # TODO: multi-level variants for hdf5
    variant('hdf5', default=False, description="Build HDF5 plugin")
    variant('zfp', default=False, description="Build HDF5 with ZFP compression")
    variant('szip', default=False, description="Build HDF5 with SZIP compression")
    variant('zlib', default=False, description="Build HDF5 with ZLIB compression")
    variant('pdb', default=False, description="Build PDB plugin")
    variant('exodus', default=False, description="Build EXODUS plugin")
    variant('scr', default=False, description="Build with SCR support")
    variant('typhonio', default=False, description="Build TYPHONIO plugin")
    variant('conduit', default=False, description="Build CONDUIT plugin")

    depends_on('json-cwx')
    depends_on('mpi', when="+mpi")

    # Build hdf5, selecting for mpi.
    # * Do we need to cross with szip and zlib too?
    # * Had to add hl for adios.
    depends_on('hdf5+hl+mpi~shared', when="+hdf5+mpi")
    depends_on('hdf5+hl~mpi~shared', when="+hdf5~mpi")

    # Silo always wants to be built with HDF5 under spack. Select for mpi.
    depends_on('silo~fortran+mpi~shared', when="+silo+mpi")
    depends_on('silo~fortran~mpi~shared', when="+silo~mpi")
    # pdb is packaged with silo so do the same thing as for Silo
    depends_on('silo~fortran+mpi~shared', when="+pdb+mpi")
    depends_on('silo~fortran~mpi~shared', when="+pdb~mpi")

    depends_on('exodusii', when="+exodus")
    depends_on('typhonio', when="+typhonio")
    depends_on('scr', when="+scr")
    depends_on('szip', when="+szip")
    depends_on('zlib', when="+zlib")

    # Build conduit.
    # * I don't care if conduit has Python except that it won't build on Mac
    #   due to NumPy/OpenBLAS fortran compiler requirements.
    # * It seems that I'm somewhat overspecifying in order to get some
    #   multilevel variants to play together. I have to force adios to get it.
#    depends_on('conduit', when="+conduit")
    depends_on('conduit@brad~python+mpi+hdf5+silo+adios~shared', when="+conduit+mpi+hdf5+silo")
    depends_on('conduit@brad~python+mpi+hdf5~silo+adios~shared', when="+conduit+mpi+hdf5~silo")
    depends_on('conduit@brad~python+mpi~hdf5+silo+adios~shared', when="+conduit+mpi~hdf5+silo")
    depends_on('conduit@brad~python+mpi~hdf5~silo+adios~shared', when="+conduit+mpi~hdf5~silo")
    depends_on('conduit@brad~python~mpi+hdf5+silo+adios~shared', when="+conduit~mpi+hdf5+silo")
    depends_on('conduit@brad~python~mpi+hdf5~silo+adios~shared', when="+conduit~mpi+hdf5~silo")
    depends_on('conduit@brad~python~mpi~hdf5+silo+adios~shared', when="+conduit~mpi~hdf5+silo")
    depends_on('conduit@brad~python~mpi~hdf5~silo+adios~shared', when="+conduit~mpi~hdf5~silo")
    # ADIOS forces this. This seems to resolve it.
    depends_on('libtool@:2.4.2', type='build')

    def cmake_args(self):
        spec = self.spec
        cmake_args = []

        if "~mpi" in spec:
            cmake_args.append("-DENABLE_MPI=OFF")

        if "~silo" in spec:
            cmake_args.append("-DENABLE_SILO_PLUGIN=OFF")

        if "+silo" in spec:
            cmake_args.append("-DWITH_SILO_PREFIX={0}"
                              .format(spec['silo'].prefix))

        if "+pdb" in spec:
            # pdb is a part of silo
            cmake_args.append("-DENABLE_PDB_PLUGIN=ON")
            cmake_args.append("-DWITH_SILO_PREFIX={0}"
                              .format(spec['silo'].prefix))
        if "+hdf5" in spec:
            cmake_args.append("-DENABLE_HDF5_PLUGIN=ON")
            cmake_args.append("-DWITH_HDF5_PREFIX={0}"
                              .format(spec['hdf5'].prefix))
            # TODO: Multi-level variants
            # ZFP not in hdf5 spack package??
            # if "+zfp" in spec:
            #     cmake_args.append("-DENABLE_HDF5_ZFP")
            #     cmake_args.append("-DWITH_ZFP_PREFIX={0}"
            #         .format(spec['silo'].prefix))
        # SZIP is an hdf5 spack variant
        if "+szip" in spec:
            cmake_args.append("-DENABLE_HDF5_SZIP=ON")
            cmake_args.append("-DWITH_SZIP_PREFIX={0}"
                 .format(spec['szip'].prefix))

        # ZLIB is on by default, @1.1.2
        if "+zlib" in spec:
            cmake_args.append("-DENABLE_HDF5_ZLIB=ON")
            cmake_args.append("-DWITH_ZLIB_PREFIX={0}"
                 .format(spec['zlib'].prefix))

        if "+typhonio" in spec:
            cmake_args.append("-DENABLE_TYPHONIO_PLUGIN=ON")
            cmake_args.append("-DWITH_TYPHONIO_PREFIX={0}"
                              .format(spec['typhonio'].prefix))

        if "+exodus" in spec:
            cmake_args.append("-DENABLE_EXODUS_PLUGIN=ON")
            cmake_args.append("-DWITH_EXODUS_PREFIX={0}"
                              .format(spec['exodusii'].prefix))
            # exodus requires netcdf
            cmake_args.append("-DWITH_NETCDF_PREFIX={0}"
                              .format(spec['netcdf'].prefix))

        if "+conduit" in spec:
            cmake_args.append("-DENABLE_CONDUIT_PLUGIN=ON")
            cmake_args.append("-DWITH_CONDUIT_PREFIX={0}"
                              .format(spec['conduit'].prefix))

        #print(os.listdir("."))
        cmake_args.append(os.path.abspath(os.curdir))

        return cmake_args
