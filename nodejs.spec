%global with_debug 1

# bundle dependencies that are not available as Fedora modules
# %%{!?_with_bootstrap: %%global bootstrap 1}
# use bcond for building modules
%bcond_with bootstrap

%{?!_pkgdocdir:%global _pkgdocdir %{_docdir}/%{name}-%{version}}

# == Node.js Version ==
# Note: Fedora should only ship LTS versions of Node.js (currently expected
# to be major versions with even numbers). The odd-numbered versions are new
# feature releases that are only supported for nine months, which is shorter
# than a Fedora release lifecycle.
%global nodejs_epoch 1
%global nodejs_major 8
%global nodejs_minor 11
%global nodejs_patch 2
%global nodejs_abi %{nodejs_major}.%{nodejs_minor}
%global nodejs_version %{nodejs_major}.%{nodejs_minor}.%{nodejs_patch}
%global nodejs_release 1

# == Bundled Dependency Versions ==
# v8 - from deps/v8/include/v8-version.h
%global v8_major 6
%global v8_minor 2
%global v8_build 414
%global v8_patch 54
# V8 presently breaks ABI at least every x.y release while never bumping SONAME
%global v8_abi %{v8_major}.%{v8_minor}
%global v8_version %{v8_major}.%{v8_minor}.%{v8_build}.%{v8_patch}

# c-ares - from deps/cares/include/ares_version.h
# https://github.com/nodejs/node/pull/9332
%global c_ares_major 1
%global c_ares_minor 10
%global c_ares_patch 1
%global c_ares_version %{c_ares_major}.%{c_ares_minor}.%{c_ares_patch}

# http-parser - from deps/http_parser/http_parser.h
%global http_parser_major 2
%global http_parser_minor 8
%global http_parser_patch 0
%global http_parser_version %{http_parser_major}.%{http_parser_minor}.%{http_parser_patch}

# libuv - from deps/uv/include/uv-version.h
%global libuv_major 1
%global libuv_minor 19
%global libuv_patch 1
%global libuv_version %{libuv_major}.%{libuv_minor}.%{libuv_patch}

# ICU - from configure in the configure_intl() function
%global libicu_major 60
%global libicu_minor 1
%global libicu_version %{libicu_major}.%{libicu_minor}

# nghttp2 - from deps/nghttp2/lib/includes/nghttp2/nghttp2ver.h
%global nghttp2_major 1
%global nghttp2_minor 29
%global nghttp2_patch 0
%global nghttp2_version %{nghttp2_major}.%{nghttp2_minor}.%{nghttp2_patch}

# punycode - from lib/punycode.js
# Note: this was merged into the mainline since 0.6.x
# Note: this will be unmerged in an upcoming major release
%global punycode_major 2
%global punycode_minor 0
%global punycode_patch 0
%global punycode_version %{punycode_major}.%{punycode_minor}.%{punycode_patch}

# npm - from deps/npm/package.json
%global npm_epoch 1
%global npm_major 5
%global npm_minor 6
%global npm_patch 0
%global npm_version %{npm_major}.%{npm_minor}.%{npm_patch}

# In order to avoid needing to keep incrementing the release version for the
# main package forever, we will just construct one for npm that is guaranteed
# to increment safely. Changing this can only be done during an update when the
# base npm version number is increasing.
%global npm_release %{nodejs_epoch}.%{nodejs_major}.%{nodejs_minor}.%{nodejs_patch}.%{nodejs_release}

# Filter out the NPM bundled dependencies so we aren't providing them
%global __provides_exclude_from ^%{_prefix}/lib/node_modules/npm/.*$
%global __requires_exclude_from ^%{_prefix}/lib/node_modules/npm/.*$


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
Source100: %{name}-tarball.sh

# The native module Requires generator remains in the nodejs SRPM, so it knows
# the nodejs and v8 versions.  The remainder has migrated to the
# nodejs-packaging SRPM.
Source7: nodejs_native.attr

# Disable running gyp on bundled deps we don't use
Patch1: 0001-Disable-running-gyp-on-shared-deps.patch

# Being fixed upstream.
# Follow https://bugs.chromium.org/p/v8/issues/detail?id=6939
Patch2: 0002-Fix-aarch64-debug.patch

# Suppress the message from npm to run `npm -g update npm`
# This does bad things on an RPM-managed npm.
Patch3: 0003-Suppress-message-to-update-npm.patch

# Fix nghttp2 debug builds
# https://github.com/nodejs/node/pull/20815
Patch4: 0004-http2-pass-session-to-DEBUG_HTTP2SESSION2.patch

BuildRequires: python2-devel
BuildRequires: libicu-devel
BuildRequires: zlib-devel
BuildRequires: gcc >= 4.9.4
BuildRequires: gcc-c++ >= 4.9.4

#%if ! 0%%{?bootstrap}
%if %{with bootstrap}
Provides: bundled(http-parser) = %{http_parser_version}
Provides: bundled(libuv) = %{libuv_version}
Provides: bundled(nghttp2) = %{nghttp2_version}
%else
BuildRequires: systemtap-sdt-devel
BuildRequires: http-parser-devel >= 2.7.0
Requires: http-parser >= 2.7.0
BuildRequires: libuv-devel >= 1:1.19.1
Requires: libuv >= 1:1.19.1
BuildRequires: libnghttp2-devel >= 1.25.0
Requires: libnghttp2 >= 1.25.0
%endif

BuildRequires: (openssl-devel <= 1:1.1.0 or compat-openssl10-devel)

# we need the system certificate store when Patch2 is applied
Requires: ca-certificates

#we need ABI virtual provides where SONAMEs aren't enough/not present so deps
#break when binary compatibility is broken
Provides: nodejs(abi) = %{nodejs_abi}
Provides: nodejs(abi%{nodejs_major}) = %{nodejs_abi}
Provides: nodejs(v8-abi) = %{v8_abi}
Provides: nodejs(v8-abi%{v8_major}) = %{v8_abi}

#this corresponds to the "engine" requirement in package.json
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

%if 0%{?fedora} && 0%{?fedora < 28}
# Node.js requires up-to-date ICU
%global config_intl --with-intl=small-icu
Provides: bundled(icu) = %{libicu_version}
%else
%global config_intl --with-intl=system-icu
%endif

# Make sure we keep NPM up to date when we update Node.js
%if 0%{?rhel}
# EPEL doesn't support Recommends, so make it strict
Requires: npm = %{npm_epoch}:%{npm_version}-%{npm_release}%{?dist}
%else
Recommends: npm = %{npm_epoch}:%{npm_version}-%{npm_release}%{?dist}
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
Requires: nodejs-packaging

#%if ! 0%%{?bootstrap}
%if %{with bootstrap}
# deps are bundled
%else
Requires: http-parser-devel%{?_isa}
Requires: libuv-devel%{?_isa}
%endif

%description devel
Development headers for the Node.js JavaScript runtime.

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
Requires: nodejs = %{epoch}:%{nodejs_version}-%{nodejs_release}%{?dist}

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
Conflicts: %{name} > %{epoch}:%{nodejs_version}-%{nodejs_release}%{?dist}
Conflicts: %{name} < %{epoch}:%{nodejs_version}-%{nodejs_release}%{?dist}

%description docs
The API documentation for the Node.js JavaScript runtime.


%prep
%setup -q -n node-v%{nodejs_version}

# remove bundled dependencies that we aren't building
%patch1 -p1

%if 0%{?fedora} && 0%{?fedora < 28}
rm -rf deps/zlib
%else
rm -rf deps/icu-small \
       deps/zlib
%endif

%patch2 -p1

%patch3 -p1

%patch4 -p1

%build
# build with debugging symbols and add defines from libuv (#892601)
# Node's v8 breaks with GCC 6 because of incorrect usage of methods on
# NULL objects. We need to pass -fno-delete-null-pointer-checks
export CFLAGS='%{optflags} -g \
               -D_LARGEFILE_SOURCE \
               -D_FILE_OFFSET_BITS=64 \
               -DZLIB_CONST \
               -fno-delete-null-pointer-checks'
export CXXFLAGS='%{optflags} -g \
                 -D_LARGEFILE_SOURCE \
                 -D_FILE_OFFSET_BITS=64 \
                 -DZLIB_CONST \
                 -fno-delete-null-pointer-checks'

# Explicit new lines in C(XX)FLAGS can break naive build scripts
export CFLAGS="$(echo ${CFLAGS} | tr '\n\\' '  ')"
export CXXFLAGS="$(echo ${CXXFLAGS} | tr '\n\\' '  ')"

export LDFLAGS="%{build_ldflags}"

# Work around Fedora 28 issue:
# https://fedoraproject.org/wiki/Changes/Avoid_usr_bin_python_in_RPM_Build#Quick_Opt-Out
# Tracking BZ: https://bugzilla.redhat.com/show_bug.cgi?id=1550564
export PYTHON_DISALLOW_AMBIGUOUS_VERSION=0

#%if ! 0%%{?bootstrap}
%if %{with bootstrap}
./configure --prefix=%{_prefix} \
           --shared-openssl \
           --shared-zlib \
           --without-dtrace \
           %{config_intl} \
           --debug-http2 \
           --debug-nghttp2 \
           --openssl-use-def-ca-store
%else
./configure --prefix=%{_prefix} \
           --shared-openssl \
           --shared-zlib \
           --shared-libuv \
           --shared-http-parser \
           --shared-nghttp2 \
           --with-dtrace \
           %{config_intl} \
           --debug-http2 \
           --debug-nghttp2 \
           --openssl-use-def-ca-store
%endif

%if %{?with_debug} == 1
# Setting BUILDTYPE=Debug builds both release and debug binaries
make BUILDTYPE=Debug %{?_smp_mflags}
%else
make BUILDTYPE=Release %{?_smp_mflags}
%endif


%install
# Work around Fedora 28 build issue:
# https://fedoraproject.org/wiki/Changes/Avoid_usr_bin_python_in_RPM_Build#Quick_Opt-Out
# Tracking BZ: https://bugzilla.redhat.com/show_bug.cgi?id=1550564
export PYTHON_DISALLOW_AMBIGUOUS_VERSION=0

rm -rf %{buildroot}

./tools/install.py install %{buildroot} %{_prefix}

# Set the binary permissions properly
chmod 0755 %{buildroot}/%{_bindir}/node

%if %{?with_debug} == 1
# Install the debug binary and set its permissions
install -Dpm0755 out/Debug/node %{buildroot}/%{_bindir}/node_g
%endif

# own the sitelib directory
mkdir -p %{buildroot}%{_prefix}/lib/node_modules

# ensure Requires are added to every native module that match the Provides from
# the nodejs build in the buildroot
install -Dpm0644 %{SOURCE7} %{buildroot}%{_rpmconfigdir}/fileattrs/nodejs_native.attr
cat << EOF > %{buildroot}%{_rpmconfigdir}/nodejs_native.req
#!/bin/sh
echo 'nodejs(abi%{nodejs_major}) >= %nodejs_abi'
echo 'nodejs(v8-abi%{v8_major}) >= %v8_abi'
EOF
chmod 0755 %{buildroot}%{_rpmconfigdir}/nodejs_native.req

#install documentation
mkdir -p %{buildroot}%{_pkgdocdir}/html
cp -pr doc/* %{buildroot}%{_pkgdocdir}/html
rm -f %{buildroot}%{_pkgdocdir}/html/nodejs.1

#node-gyp needs common.gypi too
mkdir -p %{buildroot}%{_datadir}/node
cp -p common.gypi %{buildroot}%{_datadir}/node

# Install the GDB init tool into the documentation directory
mv %{buildroot}/%{_datadir}/doc/node/gdbinit %{buildroot}/%{_pkgdocdir}/gdbinit

# Since the old version of NPM was unbundled, there are a lot of symlinks in
# it's node_modules directory. We need to keep these as symlinks to ensure we
# can backtrack on this if we decide to.

# Rename the npm node_modules directory to node_modules.bundled
mv %{buildroot}/%{_prefix}/lib/node_modules/npm/node_modules \
   %{buildroot}/%{_prefix}/lib/node_modules/npm/node_modules.bundled

# Recreate all the symlinks
mkdir -p %{buildroot}/%{_prefix}/lib/node_modules/npm/node_modules
FILES=%{buildroot}/%{_prefix}/lib/node_modules/npm/node_modules.bundled/*
for f in $FILES
do
  module=`basename $f`
  ln -s ../node_modules.bundled/$module %{buildroot}%{_prefix}/lib/node_modules/npm/node_modules/$module
done

# install NPM docs to mandir
mkdir -p %{buildroot}%{_mandir} \
         %{buildroot}%{_pkgdocdir}/npm

cp -pr deps/npm/man/* %{buildroot}%{_mandir}/
rm -rf %{buildroot}%{_prefix}/lib/node_modules/npm/man
ln -sf %{_mandir}  %{buildroot}%{_prefix}/lib/node_modules/npm/man

# Install Markdown and HTML documentation to %{_pkgdocdir}
cp -pr deps/npm/html deps/npm/doc %{buildroot}%{_pkgdocdir}/npm/
rm -rf %{buildroot}%{_prefix}/lib/node_modules/npm/html \
       %{buildroot}%{_prefix}/lib/node_modules/npm/doc

ln -sf %{_pkgdocdir} %{buildroot}%{_prefix}/lib/node_modules/npm/html
ln -sf %{_pkgdocdir}/npm/html %{buildroot}%{_prefix}/lib/node_modules/npm/doc


# Node tries to install some python files into a documentation directory
# (and not the proper one). Remove them for now until we figure out what to
# do with them.
rm -f %{buildroot}/%{_defaultdocdir}/node/lldb_commands.py \
      %{buildroot}/%{_defaultdocdir}/node/lldbinit

%check
# Fail the build if the versions don't match
%{buildroot}/%{_bindir}/node -e "require('assert').equal(process.versions.node, '%{nodejs_version}')"
%{buildroot}/%{_bindir}/node -e "require('assert').equal(process.versions.v8.replace(/-node\.\d+$/, ''), '%{v8_version}')"
%{buildroot}/%{_bindir}/node -e "require('assert').equal(process.versions.ares.replace(/-DEV$/, ''), '%{c_ares_version}')"

# Ensure we have punycode and that the version matches
%{buildroot}/%{_bindir}/node -e "require(\"assert\").equal(require(\"punycode\").version, '%{punycode_version}')"

# Ensure we have npm and that the version matches
NODE_PATH=%{buildroot}%{_prefix}/lib/node_modules %{buildroot}/%{_bindir}/node -e "require(\"assert\").equal(require(\"npm\").version, '%{npm_version}')"

%files
%{_bindir}/node
%dir %{_prefix}/lib/node_modules
%dir %{_datadir}/node
%dir %{_datadir}/systemtap
%dir %{_datadir}/systemtap/tapset
%{_datadir}/systemtap/tapset/node.stp

#%if ! 0%%{?bootstrap}
%if %{with bootstrap}
# no dtrace
%else
%dir %{_usr}/lib/dtrace
%{_usr}/lib/dtrace/node.d
%endif

%{_rpmconfigdir}/fileattrs/nodejs_native.attr
%{_rpmconfigdir}/nodejs_native.req
%license LICENSE
%doc AUTHORS CHANGELOG.md COLLABORATOR_GUIDE.md GOVERNANCE.md README.md
%doc %{_mandir}/man1/node.1*


%files devel
%if %{?with_debug} == 1
%{_bindir}/node_g
%endif
%{_includedir}/node
%{_datadir}/node/common.gypi
%{_pkgdocdir}/gdbinit


%files -n npm
%{_bindir}/npm
%{_bindir}/npx
%{_prefix}/lib/node_modules/npm
%ghost %{_sysconfdir}/npmrc
%ghost %{_sysconfdir}/npmignore
%doc %{_mandir}/man*/npm*
%doc %{_mandir}/man*/npx*
%doc %{_mandir}/man5/package.json.5*
%doc %{_mandir}/man5/package-lock.json.5*
%doc %{_mandir}/man7/removing-npm.7*
%doc %{_mandir}/man7/semver.7*


%files docs
%dir %{_pkgdocdir}
%{_pkgdocdir}/html
%{_pkgdocdir}/npm*
%{_pkgdocdir}/npm/html
%{_pkgdocdir}/npm/doc

%changelog
* Thu May 17 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:8.11.2-1
- Update to 8.11.2
- https://nodejs.org/en/blog/release/v8.11.2/

* Fri Apr 13 2018 Rafael dos Santos <rdossant@redhat.com> - 1:8.11.0-2
- Use standard Fedora linker flags (bug #1543859)

* Wed Mar 28 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:8.11.0-1
- Update to 8.11.0
- https://nodejs.org/en/blog/release/v8.11.0/

* Thu Mar 08 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:8.10.0-1
- Update to 8.10.0
- https://nodejs.org/en/blog/release/v8.10.0/

* Thu Mar 01 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:8.9.4-3
- Work around build issue on F28

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:8.9.4-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jan 11 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:8.9.4-2
- Fix incorrect Requires:

* Thu Jan 11 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:8.9.4-1
- Update to 8.9.4
- https://nodejs.org/en/blog/release/v8.9.4/
- Switch to system copy of nghttp2

* Fri Dec 08 2017 Stephen Gallagher <sgallagh@redhat.com> - 1:8.9.3-2
- Update to 8.9.3
- https://nodejs.org/en/blog/release/v8.9.3/
- https://nodejs.org/en/blog/release/v8.9.2/

* Thu Nov 30 2017 Pete Walter <pwalter@fedoraproject.org> - 1:8.9.1-2
- Rebuild for ICU 60.1

* Thu Nov 09 2017 Zuzana Svetlikova <zsvetlik@redhat.com> - 1:8.9.1-1
- Update to 8.9.1

* Tue Oct 31 2017 Stephen Gallagher <sgallagh@redhat.com> - 1:8.9.0-1
- Update to 8.9.0
- Drop upstreamed patch

* Thu Oct 26 2017 Stephen Gallagher <sgallagh@redhat.com> - 1:8.8.1-1
- Update to 8.8.1 to fix a regression

* Wed Oct 25 2017 Zuzana Svetlikova <zsvetlik@redhat.com> - 1:8.8.0-1
- Security update to 8.8.0
- https://nodejs.org/en/blog/release/v8.8.0/

* Sun Oct 15 2017 Zuzana Svetlikova <zsvetlik@redhat.com> - 1:8.7.0-1
- Update to 8.7.0
- https://nodejs.org/en/blog/release/v8.7.0/

* Fri Oct 06 2017 Zuzana Svetlikova <zsvetlik@redhat.com> - 1:8.6.0-2
- Use bcond macro instead of bootstrap conditional

* Wed Sep 27 2017 Zuzana Svetlikova <zsvetlik@redhat.com> - 1:8.6.0-1
- Fix nghttp2 version
- Update to 8.6.0
- https://nodejs.org/en/blog/release/v8.6.0/

* Wed Sep 20 2017 Zuzana Svetlikova <zsvetlik@redhat.com> - 1:8.5.0-3
- Build with bootstrap + bundle libuv for modularity
- backport patch for aarch64 debug build

* Wed Sep 13 2017 Stephen Gallagher <sgallagh@redhat.com> - 1:8.5.0-2
- Disable debug builds on aarch64 due to https://github.com/nodejs/node/issues/15395

* Tue Sep 12 2017 Stephen Gallagher <sgallagh@redhat.com> - 1:8.5.0-1
- Update to v8.5.0
- https://nodejs.org/en/blog/release/v8.5.0/

* Thu Sep 07 2017 Zuzana Svetlikova <zsvetlik@redhat.com> - 1:8.4.0-2
- Refactor openssl BR

* Wed Aug 16 2017 Zuzana Svetlikova <zsvetlik@redhat.com> - 1:8.4.0-1
- Update to v8.4.0
- https://nodejs.org/en/blog/release/v8.4.0/
- http2 is now supported, add bundled nghttp2
- remove openssl 1.0.1 patches, we won't be using them in fedora

* Thu Aug 10 2017 Zuzana Svetlikova <zsvetlik@redhat.com> - 1:8.3.0-1
- Update to v8.3.0
- https://nodejs.org/en/blog/release/v8.3.0/
- update V8 to 6.0
- update minimal gcc and g++ requirements to 4.9.4

* Wed Aug 09 2017 Tom Hughes <tom@compton.nu> - 1:8.2.1-2
- Bump release to fix broken dependencies

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:8.2.1-1.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:8.2.1-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jul 21 2017 Stephen Gallagher <sgallagh@redhat.com> - 1:8.2.1-1
- Update to v8.2.1
- https://nodejs.org/en/blog/release/v8.2.1/

* Thu Jul 20 2017 Stephen Gallagher <sgallagh@redhat.com> - 1:8.2.0-1
- Update to v8.2.0
- https://nodejs.org/en/blog/release/v8.2.0/
- Update npm to 5.3.0
- Adds npx command

* Tue Jul 18 2017 Igor Gnatenko <ignatenko@redhat.com> - 1:8.1.4-3
- s/BuildRequires/Requires/ for http-parser-devel%%{?_isa}

* Mon Jul 17 2017 Zuzana Svetlikova <zsvetlik@redhat.com> - 1:8.1.4-2
- Rename python-devel to python2-devel
- own %%{_pkgdocdir}/npm

* Tue Jul 11 2017 Stephen Gallagher <sgallagh@redhat.com> - 1:8.1.4-1
- Update to v8.1.4
- https://nodejs.org/en/blog/release/v8.1.4/
- Drop upstreamed c-ares patch

* Thu Jun 29 2017 Zuzana Svetlikova <zsvetlik@redhat.com> - 1:8.1.3-1
- Update to v8.1.3
- https://nodejs.org/en/blog/release/v8.1.3/ 

* Wed Jun 28 2017 Zuzana Svetlikova <zsvetlik@redhat.com> - 1:8.1.2-1
- Update to v8.1.2
- remove GCC 7 patch, as it is now fixed in node >= 6.12

