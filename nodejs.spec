# bundle dependencies that are not available as Fedora modules
%bcond_with bootstrap

%if 0%{?rhel} && 0%{?rhel} < 9
%bcond_without python3_fixup
%else
%bcond_with python3_fixup
%endif

# LTO is currently broken on Node.js builds
%define _lto_cflags %{nil}

# Heavy-handed approach to avoiding issues with python
# bytecompiling files in the node_modules/ directory
%global __python %{__python3}

# == Master Relase ==
# This is used by both the nodejs package and the npm subpackage that
# has a separate version - the name is special so that rpmdev-bumpspec
# will bump this rather than adding .1 to the end.
%global baserelease 2

%{?!_pkgdocdir:%global _pkgdocdir %{_docdir}/%{name}-%{version}}

# == Node.js Version ==
# Note: Fedora should only ship LTS versions of Node.js (currently expected
# to be major versions with even numbers). The odd-numbered versions are new
# feature releases that are only supported for nine months, which is shorter
# than a Fedora release lifecycle.
%global nodejs_epoch 1
%global nodejs_major 16
%global nodejs_minor 13
%global nodejs_patch 2
%global nodejs_abi %{nodejs_major}.%{nodejs_minor}
# nodejs_soversion - from NODE_MODULE_VERSION in src/node_version.h
%global nodejs_soversion 93
%global nodejs_version %{nodejs_major}.%{nodejs_minor}.%{nodejs_patch}
%global nodejs_release %{baserelease}

%global nodejs_datadir %{_datarootdir}/nodejs

# == Bundled Dependency Versions ==
# v8 - from deps/v8/include/v8-version.h
# Epoch is set to ensure clean upgrades from the old v8 package
%global v8_epoch 2
%global v8_major 9
%global v8_minor 4
%global v8_build 146
%global v8_patch 24
%global v8_version %{v8_major}.%{v8_minor}.%{v8_build}.%{v8_patch}
%global v8_release %{nodejs_epoch}.%{nodejs_major}.%{nodejs_minor}.%{nodejs_patch}.%{nodejs_release}

# c-ares - from deps/cares/include/ares_version.h
# https://github.com/nodejs/node/pull/9332
%global c_ares_major 1
%global c_ares_minor 18
%global c_ares_patch 1
%global c_ares_version %{c_ares_major}.%{c_ares_minor}.%{c_ares_patch}

# llhttp - from deps/llhttp/include/llhttp.h
%global llhttp_major 6
%global llhttp_minor 0
%global llhttp_patch 4
%global llhttp_version %{llhttp_major}.%{llhttp_minor}.%{llhttp_patch}

# libuv - from deps/uv/include/uv/version.h
%global libuv_major 1
%global libuv_minor 42
%global libuv_patch 0
%global libuv_version %{libuv_major}.%{libuv_minor}.%{libuv_patch}

# nghttp2 - from deps/nghttp2/lib/includes/nghttp2/nghttp2ver.h
%global nghttp2_major 1
%global nghttp2_minor 45
%global nghttp2_patch 1
%global nghttp2_version %{nghttp2_major}.%{nghttp2_minor}.%{nghttp2_patch}

# ICU - from tools/icu/current_ver.dep
%global icu_major 69
%global icu_minor 1
%global icu_version %{icu_major}.%{icu_minor}

%global icudatadir %{nodejs_datadir}/icudata
%{!?little_endian: %global little_endian %(%{__python3} -c "import sys;print (0 if sys.byteorder=='big' else 1)")}
# " this line just fixes syntax highlighting for vim that is confused by the above and continues literal


# OpenSSL minimum version
%global openssl_minimum 1:1.1.1

# punycode - from lib/punycode.js
# Note: this was merged into the mainline since 0.6.x
# Note: this will be unmerged in an upcoming major release
%global punycode_major 2
%global punycode_minor 1
%global punycode_patch 0
%global punycode_version %{punycode_major}.%{punycode_minor}.%{punycode_patch}

# npm - from deps/npm/package.json
%global npm_epoch 1
%global npm_major 8
%global npm_minor 1
%global npm_patch 2
%global npm_version %{npm_major}.%{npm_minor}.%{npm_patch}

# In order to avoid needing to keep incrementing the release version for the
# main package forever, we will just construct one for npm that is guaranteed
# to increment safely. Changing this can only be done during an update when the
# base npm version number is increasing.
%global npm_release %{nodejs_epoch}.%{nodejs_major}.%{nodejs_minor}.%{nodejs_patch}.%{nodejs_release}

# uvwasi - from deps/uvwasi/include/uvwasi.h
%global uvwasi_major 0
%global uvwasi_minor 0
%global uvwasi_patch 11
%global uvwasi_version %{uvwasi_major}.%{uvwasi_minor}.%{uvwasi_patch}

# histogram_c - assumed from timestamps
%global histogram_major 0
%global histogram_minor 9
%global histogram_patch 7
%global histogram_version %{histogram_major}.%{histogram_minor}.%{histogram_patch}

# Node.js 16.9.1 and later comes with an experimental package management tool
%global corepack_version 0.10.0

Name: nodejs
Epoch: %{nodejs_epoch}
Version: %{nodejs_version}
Release: %{nodejs_release}%{?dist}
Summary: JavaScript runtime
License: MIT and ASL 2.0 and ISC and BSD
Group: Development/Languages
URL: http://nodejs.org/

ExclusiveArch: %{nodejs_arches}

# nodejs bundles openssl, but we use the system version in Fedora
# because openssl contains prohibited code, we remove openssl completely from
# the tarball, using the script in Source100
Source0: node-v%{nodejs_version}-stripped.tar.gz
Source1: npmrc
Source2: btest402.js
Source3: https://github.com/unicode-org/icu/releases/download/release-%{icu_major}-%{icu_minor}/icu4c-%{icu_major}_%{icu_minor}-src.tgz
Source100: %{name}-tarball.sh

# The native module Requires generator remains in the nodejs SRPM, so it knows
# the nodejs and v8 versions.  The remainder has migrated to the
# nodejs-packaging SRPM.
Source7: nodejs_native.attr

# Disable running gyp on bundled deps we don't use
Patch1: 0001-Disable-running-gyp-on-shared-deps.patch

# Patch to install both node and libnode.so, using the correct libdir
Patch2: 0002-Install-both-binaries-and-use-libdir.patch

BuildRequires: make
BuildRequires: python%{python3_pkgversion}-devel
BuildRequires: python%{python3_pkgversion}-setuptools
BuildRequires: python%{python3_pkgversion}-jinja2
%if !%{with python3_fixup}
BuildRequires: python-unversioned-command
%endif
BuildRequires: zlib-devel
BuildRequires: brotli-devel
%if 0%{?rhel} && 0%{?rhel} < 8
BuildRequires: devtoolset-11-gcc
BuildRequires: devtoolset-11-gcc-c++
%else
BuildRequires: gcc >= 8.3.0
BuildRequires: gcc-c++ >= 8.3.0
%endif

BuildRequires: jq
# needed to generate bundled provides for npm dependencies
# https://src.fedoraproject.org/rpms/nodejs/pull-request/2
# https://pagure.io/nodejs-packaging/pull-request/10
BuildRequires: nodejs-packaging
BuildRequires: chrpath
BuildRequires: libatomic
BuildRequires: systemtap-sdt-devel

%if %{with bootstrap}
Provides: bundled(libuv) = %{libuv_version}
Provides: bundled(nghttp2) = %{nghttp2_version}
%else
BuildRequires: libuv-devel >= 1:%{libuv_version}
Requires: libuv >= 1:%{libuv_version}
%if 0%{?fedora} || 0%{?rhel} >= 9
BuildRequires: libnghttp2-devel >= %{nghttp2_version}
Requires: libnghttp2 >= %{nghttp2_version}
%define nghttp2_configure --shared-nghttp2
%else
%define nghttp2_configure %{nil}
Provides: bundled(nghttp2) = %{nghttp2_version}
%endif
%endif

# Temporarily bundle llhttp because the upstream doesn't
# provide releases for it.
Provides: bundled(llhttp) = %{llhttp_version}

%if 0%{?rhel} && 0%{?rhel} < 8
BuildRequires: openssl11-devel >= %{openssl_minimum}
Requires: openssl11 >= %{openssl_minimum}
%global ssl_configure --shared-openssl --shared-openssl-includes=%{_includedir}/openssl11 --shared-openssl-libpath=%{_libdir}/openssl11
%else
BuildRequires: openssl-devel >= %{openssl_minimum}
Requires: openssl >= %{openssl_minimum}
%global ssl_configure --shared-openssl
%endif

# we need the system certificate store
Requires: ca-certificates

Requires: nodejs-libs%{?_isa} = %{nodejs_epoch}:%{version}-%{release}

# Pull in the full-icu data by default
%if 0%{?rhel} && 0%{?rhel} < 8
Requires: nodejs-full-i18n%{?_isa} = %{nodejs_epoch}:%{version}-%{release}
%else
Recommends: nodejs-full-i18n%{?_isa} = %{nodejs_epoch}:%{version}-%{release}
%endif

# we need ABI virtual provides where SONAMEs aren't enough/not present so deps
# break when binary compatibility is broken
Provides: nodejs(abi) = %{nodejs_abi}
Provides: nodejs(abi%{nodejs_major}) = %{nodejs_abi}

# this corresponds to the "engine" requirement in package.json
Provides: nodejs(engine) = %{nodejs_version}

# Node.js currently has a conflict with the 'node' package in Fedora
# The ham-radio group has agreed to rename their binary for us, but
# in the meantime, we're setting an explicit Conflicts: here
Conflicts: node <= 0.3.2-12

# The punycode module was absorbed into the standard library in v0.6.
# It still exists as a seperate package for the benefit of users of older
# versions.  Since we've never shipped anything older than v0.10 in Fedora,
# we don't need the seperate nodejs-punycode package, so we Provide it here so
# dependent packages don't need to override the dependency generator.
# See also: RHBZ#11511811
# UPDATE: punycode will be deprecated and so we should unbundle it in Node v8
# and use upstream module instead
# https://github.com/nodejs/node/commit/29e49fc286080215031a81effbd59eac092fff2f
Provides: nodejs-punycode = %{punycode_version}
Provides: npm(punycode) = %{punycode_version}

# Node.js has forked c-ares from upstream in an incompatible way, so we need
# to carry the bundled version internally.
# See https://github.com/nodejs/node/commit/766d063e0578c0f7758c3a965c971763f43fec85
Provides: bundled(c-ares) = %{c_ares_version}

# Node.js is closely tied to the version of v8 that is used with it. It makes
# sense to use the bundled version because upstream consistently breaks ABI
# even in point releases. Node.js upstream has now removed the ability to build
# against a shared system version entirely.
# See https://github.com/nodejs/node/commit/d726a177ed59c37cf5306983ed00ecd858cfbbef
Provides: bundled(v8) = %{v8_version}

# Node.js is bound to a specific version of ICU which may not match the OS
# We cannot pin the OS to this version of ICU because every update includes
# an ABI-break, so we'll use the bundled copy.
Provides: bundled(icu) = %{icu_version}

# Upstream added new dependencies, but so far they are not available in Fedora
# or there's no option to built it as a shared dependency, so we bundle them
Provides: bundled(uvwasi) = %{uvwasi_version}
Provides: bundled(histogram) = %{histogram_version}
Provides: bundled(corepack) = %{corepack_version}

%if 0%{?fedora}
# Make sure to pull in the appropriate packaging macros when building RPMs
Requires: (nodejs-packaging if rpm-build)
%endif

# Make sure we keep NPM up to date when we update Node.js
%if 0%{?rhel} && 0%{?rhel} < 8
Requires: npm >= %{npm_epoch}:%{npm_version}-%{npm_release}%{?dist}
%else
Recommends: npm >= %{npm_epoch}:%{npm_version}-%{npm_release}%{?dist}
%endif


%description
Node.js is a platform built on Chrome's JavaScript runtime
for easily building fast, scalable network applications.
Node.js uses an event-driven, non-blocking I/O model that
makes it lightweight and efficient, perfect for data-intensive
real-time applications that run across distributed devices.


%package devel
Summary: JavaScript runtime - development headers
Group: Development/Languages
Requires: %{name}%{?_isa} = %{epoch}:%{nodejs_version}-%{nodejs_release}%{?dist}
Requires: openssl-devel%{?_isa}
Requires: zlib-devel%{?_isa}
Requires: brotli-devel%{?_isa}
Requires: nodejs-packaging

%if %{with bootstrap}
# deps are bundled
%else
Requires: libuv-devel%{?_isa}
%endif

%description devel
Development headers for the Node.js JavaScript runtime.


%package libs
Summary: Node.js and v8 libraries

# Compatibility for obsolete v8 package
%if 0%{?__isa_bits} == 64
Provides: libv8.so.%{v8_major}()(64bit)
Provides: libv8_libbase.so.%{v8_major}()(64bit)
Provides: libv8_libplatform.so.%{v8_major}()(64bit)
%else
# 32-bits
Provides: libv8.so.%{v8_major}
Provides: libv8_libbase.so.%{v8_major}
Provides: libv8_libplatform.so.%{v8_major}
%endif

Provides: v8 = %{v8_epoch}:%{v8_version}-%{nodejs_release}%{?dist}
Provides: v8%{?_isa} = %{v8_epoch}:%{v8_version}-%{nodejs_release}%{?dist}
Obsoletes: v8 < 1:6.7.17-10

%description libs
Libraries to support Node.js and provide stable v8 interfaces.


%package full-i18n
Summary: Non-English locale data for Node.js
Requires: %{name}%{?_isa} = %{nodejs_epoch}:%{nodejs_version}-%{nodejs_release}%{?dist}

%description full-i18n
Optional data files to provide full-icu support for Node.js. Remove this
package to save space if non-English locales are not needed.


%package -n v8-devel
Summary: v8 - development headers
Epoch: %{v8_epoch}
Version: %{v8_version}
Release: %{v8_release}%{?dist}
Requires: %{name}-devel%{?_isa} = %{nodejs_epoch}:%{nodejs_version}-%{nodejs_release}%{?dist}

%description -n v8-devel
Development headers for the v8 runtime.


%package -n npm
Summary: Node.js Package Manager
Epoch: %{npm_epoch}
Version: %{npm_version}
Release: %{npm_release}%{?dist}

# We used to ship npm separately, but it is so tightly integrated with Node.js
# (and expected to be present on all Node.js systems) that we ship it bundled
# now.
Obsoletes: npm < 0:3.5.4-6
Provides: npm = %{npm_epoch}:%{npm_version}
Requires: nodejs = %{nodejs_epoch}:%{nodejs_version}-%{nodejs_release}%{?dist}
%if 0%{?rhel} && 0%{?rhel} < 8
Requires: nodejs-docs = %{nodejs_epoch}:%{nodejs_version}-%{nodejs_release}%{?dist}
%else
Recommends: nodejs-docs = %{nodejs_epoch}:%{nodejs_version}-%{nodejs_release}%{?dist}
%endif

# Do not add epoch to the virtual NPM provides or it will break
# the automatic dependency-generation script.
Provides: npm(npm) = %{npm_version}

%description -n npm
npm is a package manager for node.js. You can use it to install and publish
your node programs. It manages dependencies and does other cool stuff.


%package docs
Summary: Node.js API documentation
Group: Documentation
BuildArch: noarch

# We don't require that the main package be installed to
# use the docs, but if it is installed, make sure the
# version always matches
Conflicts: %{name} > %{nodejs_epoch}:%{nodejs_version}-%{nodejs_release}%{?dist}
Conflicts: %{name} < %{nodejs_epoch}:%{nodejs_version}-%{nodejs_release}%{?dist}

%description docs
The API documentation for the Node.js JavaScript runtime.


%prep
%autosetup -p1 -n node-v%{nodejs_version}

# remove bundled dependencies that we aren't building
rm -rf deps/zlib
rm -rf deps/brotli
rm -rf deps/v8/third_party/jinja2
rm -rf tools/inspector_protocol/jinja2

# Replace any instances of unversioned python' with python3
%if %{with python3_fixup}
pathfix.py -i %{__python3} -pn $(find -type f ! -name "*.js")
find . -type f -exec sed -i "s~/usr\/bin\/env python~/usr/bin/python3~" {} \;
find . -type f -exec sed -i "s~/usr\/bin\/python\W~/usr/bin/python3~" {} \;
sed -i "s~usr\/bin\/python2~usr\/bin\/python3~" ./deps/v8/tools/gen-inlining-tests.py
sed -i "s~usr\/bin\/python.*$~usr\/bin\/python3~" ./deps/v8/tools/mb/mb_unittest.py
find . -type f -exec sed -i "s~python -c~python3 -c~" {} \;
%endif


%build

# Activate DevToolset 11 on EPEL 7
%if 0%{?rhel} && 0%{?rhel} < 8
. /opt/rh/devtoolset-11/enable
%endif

# When compiled on armv7hl this package generates an out of range
# reference to the literal pool.  This is most likely a GCC issue.
%ifarch armv7hl
%define _lto_cflags %{nil}
%endif

%ifarch s390 s390x %{arm} %ix86
# Decrease debuginfo verbosity to reduce memory consumption during final
# library linking
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

export CC='%{__cc}'
export CXX='%{__cxx}'
%if %{with python3_fixup}
export NODE_GYP_FORCE_PYTHON=%{__python3}
%endif

# build with debugging symbols and add defines from libuv (#892601)
# Node's v8 breaks with GCC 6 because of incorrect usage of methods on
# NULL objects. We need to pass -fno-delete-null-pointer-checks
export CFLAGS='%{optflags} \
               -D_LARGEFILE_SOURCE \
               -D_FILE_OFFSET_BITS=64 \
               -DZLIB_CONST \
               -fno-delete-null-pointer-checks'
export CXXFLAGS='%{optflags} \
                 -D_LARGEFILE_SOURCE \
                 -D_FILE_OFFSET_BITS=64 \
                 -DZLIB_CONST \
                 -fno-delete-null-pointer-checks'

# Explicit new lines in C(XX)FLAGS can break naive build scripts
export CFLAGS="$(echo ${CFLAGS} | tr '\n\\' '  ')"
export CXXFLAGS="$(echo ${CXXFLAGS} | tr '\n\\' '  ')"

export LDFLAGS="%{build_ldflags}"

%if %{with bootstrap}
%{__python3} configure.py --prefix=%{_prefix} \
           --shared \
           --libdir=%{_lib} \
           %{ssl_configure} \
           --shared-zlib \
           --shared-brotli \
           --without-dtrace \
           --with-intl=small-icu \
           --openssl-use-def-ca-store
%else
%{__python3} configure.py --prefix=%{_prefix} \
           --shared \
           --libdir=%{_lib} \
           %{ssl_configure} \
           --shared-zlib \
           --shared-brotli \
           --shared-libuv \
           %{nghttp2_configure} \
           --with-dtrace \
           --with-intl=small-icu \
           --with-icu-default-data-dir=%{icudatadir} \
           --openssl-use-def-ca-store
%endif

%make_build BUILDTYPE=Release

# Extract the ICU data and convert it to the appropriate endianness
pushd deps/
tar xfz %SOURCE3

pushd icu/source

mkdir -p converted
%if 0%{?little_endian}
# The little endian data file is included in the ICU sources
install -Dpm0644 data/in/icudt%{icu_major}l.dat converted/

%else
# For the time being, we need to build ICU and use the included `icupkg` tool
# to convert the little endian data file into a big-endian one.
# At some point in the future, ICU releases will start including both data
# files and we should switch to those.
mkdir -p data/out/tmp

%configure
%make_build

icu_root=$(pwd)
LD_LIBRARY_PATH=./lib ./bin/icupkg -tb data/in/icudt%{icu_major}l.dat \
                                       converted/icudt%{icu_major}b.dat
%endif

popd # icu/source
popd # deps


%install
rm -rf %{buildroot}

./tools/install.py install %{buildroot} %{_prefix}

# Set the binary permissions properly
chmod 0755 %{buildroot}/%{_bindir}/node
chrpath --delete %{buildroot}%{_bindir}/node

# Install library symlink
ln -s libnode.so.%{nodejs_soversion} %{buildroot}%{_libdir}/libnode.so

# Install v8 compatibility symlinks
for header in %{buildroot}%{_includedir}/node/libplatform %{buildroot}%{_includedir}/node/v8*.h; do
    header=$(basename ${header})
    ln -s ./node/${header} %{buildroot}%{_includedir}/${header}
done
ln -s ./node/cppgc %{buildroot}%{_includedir}/cppgc
for soname in libv8 libv8_libbase libv8_libplatform; do
    ln -s libnode.so.%{nodejs_soversion} %{buildroot}%{_libdir}/${soname}.so
    ln -s libnode.so.%{nodejs_soversion} %{buildroot}%{_libdir}/${soname}.so.%{v8_major}
done

# own the sitelib directory
mkdir -p %{buildroot}%{_prefix}/lib/node_modules

# ensure Requires are added to every native module that match the Provides from
# the nodejs build in the buildroot
install -Dpm0644 %{SOURCE7} %{buildroot}%{_rpmconfigdir}/fileattrs/nodejs_native.attr
cat << EOF > %{buildroot}%{_rpmconfigdir}/nodejs_native.req
#!/bin/sh
echo 'nodejs(abi%{nodejs_major}) >= %nodejs_abi'
EOF
chmod 0755 %{buildroot}%{_rpmconfigdir}/nodejs_native.req

# install documentation
mkdir -p %{buildroot}%{_pkgdocdir}/html
cp -pr doc/* %{buildroot}%{_pkgdocdir}/html
rm -f %{buildroot}%{_pkgdocdir}/html/nodejs.1

# node-gyp needs common.gypi too
mkdir -p %{buildroot}%{_datadir}/node
cp -p common.gypi %{buildroot}%{_datadir}/node

# Install the GDB init tool into the documentation directory
mv %{buildroot}/%{_datadir}/doc/node/gdbinit %{buildroot}/%{_pkgdocdir}/gdbinit

# install NPM docs to mandir
mkdir -p %{buildroot}%{_mandir} \
         %{buildroot}%{_pkgdocdir}/npm

cp -pr deps/npm/man/* %{buildroot}%{_mandir}/
rm -rf %{buildroot}%{_prefix}/lib/node_modules/npm/man
ln -sf %{_mandir}  %{buildroot}%{_prefix}/lib/node_modules/npm/man

# Install Gatsby HTML documentation to %{_pkgdocdir}
cp -pr deps/npm/docs %{buildroot}%{_pkgdocdir}/npm/
rm -rf %{buildroot}%{_prefix}/lib/node_modules/npm/docs

ln -sf %{_pkgdocdir}/npm %{buildroot}%{_prefix}/lib/node_modules/npm/docs

# Node tries to install some python files into a documentation directory
# (and not the proper one). Remove them for now until we figure out what to
# do with them.
rm -f %{buildroot}/%{_defaultdocdir}/node/lldb_commands.py \
      %{buildroot}/%{_defaultdocdir}/node/lldbinit

# Some NPM bundled deps are executable but should not be. This causes
# unnecessary automatic dependencies to be added. Make them not executable.
# Skip the npm bin directory or the npm binary will not work.
find %{buildroot}%{_prefix}/lib/node_modules/npm \
    -not -path "%{buildroot}%{_prefix}/lib/node_modules/npm/bin/*" \
    -executable -type f \
    -exec chmod -x {} \;

# The above command is a little overzealous. Add a few permissions back.
chmod 0755 %{buildroot}%{_prefix}/lib/node_modules/npm/node_modules/@npmcli/run-script/lib/node-gyp-bin/node-gyp
chmod 0755 %{buildroot}%{_prefix}/lib/node_modules/npm/node_modules/node-gyp/bin/node-gyp.js

# Corepack contains a number of executable"shims", including some for Windows
# PowerShell. Drop the executable bit for those so we don't pick up an
# automatic dependency on /usr/bin/pwsh that we cannot satisfy.
chmod -x %{buildroot}%{_prefix}/lib/node_modules/corepack/shims/*.ps1

# Drop the NPM default configuration in place
mkdir -p %{buildroot}%{_sysconfdir}
cp %{SOURCE1} %{buildroot}%{_sysconfdir}/npmrc

# NPM upstream expects it to be in /usr/etc/npmrc, so we'll put a symlink here
# This is done in the interests of keeping /usr read-only.
mkdir -p %{buildroot}%{_prefix}/etc
ln -s %{_sysconfdir}/npmrc %{buildroot}%{_prefix}/etc/npmrc

# Install the full-icu data files
mkdir -p %{buildroot}%{icudatadir}
install -Dpm0644 -t %{buildroot}%{icudatadir} deps/icu/source/converted/*


%check
# Fail the build if the versions don't match
LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}/%{_bindir}/node -e "require('assert').equal(process.versions.node, '%{nodejs_version}')"
LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}/%{_bindir}/node -e "require('assert').equal(process.versions.v8.replace(/-node\.\d+$/, ''), '%{v8_version}')"
LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}/%{_bindir}/node -e "require('assert').equal(process.versions.ares.replace(/-DEV$/, ''), '%{c_ares_version}')"

# Ensure we have punycode and that the version matches
LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}/%{_bindir}/node -e "require(\"assert\").equal(require(\"punycode\").version, '%{punycode_version}')"

# Ensure we have npm and that the version matches
LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}%{_bindir}/node %{buildroot}%{_bindir}/npm version --json |jq '. | select(.npm | contains("7.24.0"))'

# Make sure i18n support is working
NODE_PATH=%{buildroot}%{_prefix}/lib/node_modules:%{buildroot}%{_prefix}/lib/node_modules/npm/node_modules LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}/%{_bindir}/node --icu-data-dir=%{buildroot}%{icudatadir} %{SOURCE2}


%files
%{_bindir}/node
%dir %{_prefix}/lib/node_modules
%dir %{_datadir}/node
%dir %{_datadir}/systemtap
%dir %{_datadir}/systemtap/tapset
%{_datadir}/systemtap/tapset/node.stp

# corepack
%{_bindir}/corepack
%{_prefix}/lib/node_modules/corepack

%if %{with bootstrap}
# no dtrace
%else
%dir %{_usr}/lib/dtrace
%{_usr}/lib/dtrace/node.d
%endif

%{_rpmconfigdir}/fileattrs/nodejs_native.attr
%{_rpmconfigdir}/nodejs_native.req
%doc AUTHORS CHANGELOG.md onboarding.md GOVERNANCE.md README.md
%doc %{_mandir}/man1/node.1*


%files devel
%{_includedir}/node
%{_libdir}/libnode.so
%{_datadir}/node/common.gypi
%{_pkgdocdir}/gdbinit


%files full-i18n
%dir %{icudatadir}
%{icudatadir}/icudt%{icu_major}*.dat


%files libs
%license LICENSE
%{_libdir}/libnode.so.%{nodejs_soversion}
%{_libdir}/libv8.so.%{v8_major}
%{_libdir}/libv8_libbase.so.%{v8_major}
%{_libdir}/libv8_libplatform.so.%{v8_major}
%dir %{nodejs_datadir}/


%files -n v8-devel
%{_includedir}/libplatform
%{_includedir}/v8*.h
%{_includedir}/cppgc
%{_libdir}/libv8.so
%{_libdir}/libv8_libbase.so
%{_libdir}/libv8_libplatform.so


%files -n npm
%{_bindir}/npm
%{_bindir}/npx
%{_prefix}/lib/node_modules/npm
%config(noreplace) %{_sysconfdir}/npmrc
%{_prefix}/etc/npmrc
%ghost %{_sysconfdir}/npmignore
%doc %{_mandir}/man1/npm*.1*
%doc %{_mandir}/man1/npx.1*
%doc %{_mandir}/man5/folders.5*
%doc %{_mandir}/man5/install.5*
%doc %{_mandir}/man5/npmrc.5*
%doc %{_mandir}/man5/npm-shrinkwrap-json.5*
%doc %{_mandir}/man5/package-json.5*
%doc %{_mandir}/man5/package-lock-json.5*
%doc %{_mandir}/man7/config.7*
%doc %{_mandir}/man7/developers.7*
%doc %{_mandir}/man7/orgs.7*
%doc %{_mandir}/man7/registry.7*
%doc %{_mandir}/man7/removal.7*
%doc %{_mandir}/man7/scope.7*
%doc %{_mandir}/man7/scripts.7*
%doc %{_mandir}/man7/workspaces.7*


%files docs
%doc doc
%dir %{_pkgdocdir}
%{_pkgdocdir}/html
%{_pkgdocdir}/npm/docs


%changelog
* Mon Jan 17 2022 Stephen Gallagher <sgallagh@redhat.com> - 1:16.13.2-2
- Add support for building on EPEL 7

* Tue Jan 11 2022 Stephen Gallagher <sgallagh@redhat.com> - 1:16.13.2-1
- Improper handling of URI Subject Alternative Names (Medium)(CVE-2021-44531)
- Certificate Verification Bypass via String Injection (Medium)(CVE-2021-44532)
- Incorrect handling of certificate subject and issuer fields (Medium)(CVE-2021-44533)
- Prototype pollution via `console.table` properties (Low)(CVE-2022-21824)

* Thu Dec 02 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.13.1-2
- Enable building for EPEL 8 modules

* Thu Dec 02 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.13.1-1
- Update to 16.13.1
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.13.1

* Thu Nov 25 2021 Honza Horak <hhorak@redhat.com> - 1:16.13.0-3
- Make sure binary node-gyp is executable
  Resolves: #2026615

* Mon Nov 01 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.13.0-1
- Update to 16.13.0
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.13.0
- Add support for epel8

* Mon Oct 25 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.12.0-1
- Update to 16.12.0
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.12.0

* Wed Oct 13 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.11.1-1
- Update to 16.11.1
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.11.0
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.11.1

* Thu Sep 23 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.10.0-1
- Update to 16.10.0
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.10.0

* Tue Sep 14 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.9.1-4
- Correct the bad merge of corepack fix

* Tue Sep 14 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.9.1-3
- Drop auto-dependency on PowerShell introduced by corepack

* Tue Sep 14 2021 Sahana Prasad <sahana@redhat.com> - 1:16.9.1-2
- Rebuilt with OpenSSL 3.0.0

* Mon Sep 13 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.9.1-1
- Update to 16.9.1
- Add experimental 'corepack' tool
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.9.0
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.9.1

* Tue Aug 31 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.8.0-1
- Update to 16.8.0
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.8.0
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.7.0

* Wed Aug 11 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.6.2-1
- Update to 16.6.2
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.6.2

* Tue Aug 03 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.6.1-1
- Update to 16.6.1
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.6.1
- Fixes v8 regression introduced in 16.6.0

* Mon Aug 02 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.6.0-1
- Update to 16.6.0
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.6.0

* Thu Jul 22 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1:16.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Tue Jul 20 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.5.0-1
- Update to 16.5.0
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.5.0

* Fri Jul 02 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.4.1-2
- Re-add support for v8 development headers

* Thu Jul 01 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.4.1-1
- Update to 16.4.1
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.4.1

* Wed Jun 23 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.4.0-1
- Update to 16.4.0
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.4.0

* Fri Jun 04 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.3.0-1
- Update to 16.3.0
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.3.0


* Wed May 19 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.2.0-1
- Update to 16.2.0
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.2.0
- Fix changelog version numbers

* Tue May 04 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.1.0-1
- Update to 16.1.0
- https://github.com/nodejs/node/blob/master/doc/changelogs/CHANGELOG_V16.md#16.1.0
- Drop upstreamed patch

* Thu Apr 29 2021 Stephen Gallagher <sgallagh@redhat.com> - 1:16.0.0-1
- First release of Node.js 16.x

