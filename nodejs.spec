%global with_debug 1

# PowerPC and s390x segfault during Debug builds
# https://github.com/nodejs/node/issues/20642
%ifarch %{power64} s390x
%global with_debug 0
%endif

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
%global nodejs_major 10
%global nodejs_minor 7
%global nodejs_patch 0
%global nodejs_abi %{nodejs_major}.%{nodejs_minor}
%global nodejs_version %{nodejs_major}.%{nodejs_minor}.%{nodejs_patch}
%global nodejs_release 4

# == Bundled Dependency Versions ==
# v8 - from deps/v8/include/v8-version.h
%global v8_major 6
%global v8_minor 7
%global v8_build 288
%global v8_patch 49
# V8 presently breaks ABI at least every x.y release while never bumping SONAME
%global v8_abi %{v8_major}.%{v8_minor}
%global v8_version %{v8_major}.%{v8_minor}.%{v8_build}.%{v8_patch}

# c-ares - from deps/cares/include/ares_version.h
# https://github.com/nodejs/node/pull/9332
%global c_ares_major 1
%global c_ares_minor 14
%global c_ares_patch 0
%global c_ares_version %{c_ares_major}.%{c_ares_minor}.%{c_ares_patch}

# http-parser - from deps/http_parser/http_parser.h
%global http_parser_major 2
%global http_parser_minor 8
%global http_parser_patch 0
%global http_parser_version %{http_parser_major}.%{http_parser_minor}.%{http_parser_patch}

# libuv - from deps/uv/include/uv/version.h
%global libuv_major 1
%global libuv_minor 22
%global libuv_patch 0
%global libuv_version %{libuv_major}.%{libuv_minor}.%{libuv_patch}

# nghttp2 - from deps/nghttp2/lib/includes/nghttp2/nghttp2ver.h
%global nghttp2_major 1
%global nghttp2_minor 32
%global nghttp2_patch 0
%global nghttp2_version %{nghttp2_major}.%{nghttp2_minor}.%{nghttp2_patch}

# ICU - from configure in the configure_intl() function
%global icu_major 62
%global icu_minor 1
%global icu_version %{icu_major}.%{icu_minor}

%if 0%{?fedora} >= 29
%global icu_flag system-icu
%else
%global icu_flag small-icu
%endif


# punycode - from lib/punycode.js
# Note: this was merged into the mainline since 0.6.x
# Note: this will be unmerged in an upcoming major release
%global punycode_major 2
%global punycode_minor 1
%global punycode_patch 0
%global punycode_version %{punycode_major}.%{punycode_minor}.%{punycode_patch}

# npm - from deps/npm/package.json
%global npm_epoch 1
%global npm_major 6
%global npm_minor 1
%global npm_patch 0
%global npm_version %{npm_major}.%{npm_minor}.%{npm_patch}

# In order to avoid needing to keep incrementing the release version for the
# main package forever, we will just construct one for npm that is guaranteed
# to increment safely. Changing this can only be done during an update when the
# base npm version number is increasing.
%global npm_release %{nodejs_epoch}.%{nodejs_major}.%{nodejs_minor}.%{nodejs_patch}.%{nodejs_release}


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

# Suppress the message from npm to run `npm -g update npm`
# This does bad things on an RPM-managed npm.
Patch2: 0002-Suppress-NPM-message-to-run-global-update.patch

BuildRequires: python2-devel
BuildRequires: python3-devel
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
BuildRequires: libuv-devel >= 1:%{libuv_version}
Requires: libuv >= 1:1.20.2
BuildRequires: libnghttp2-devel >= %{nghttp2_version}
Requires: libnghttp2 >= %{nghttp2_version}
%endif


%if 0%{?fedora} >= 29
BuildRequires: libicu-devel >= 62.1
%endif

BuildRequires: openssl-devel

# we need the system certificate store
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

# Node.js is bound to a specific version of ICU which may not match the OS
# We cannot pin the OS to this version of ICU because every update includes
# an ABI-break, so we'll use the bundled copy.
Provides: bundled(icu) = %{icu_version}

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
rm -rf deps/zlib

%patch2 -p1

# Replace any instances of unversioned python' with python2
pathfix.py -i %{__python2} -pn $(find -type f)
find . -type f -exec sed -i "s~/usr\/bin\/env python~/usr/bin/python2~" {} \;
find . -type f -exec sed -i "s~/usr\/bin\/python\W~/usr/bin/python2~" {} \;
sed -i "s~python~python2~" $(find . -type f | grep "gyp$")
sed -i "s~usr\/bin\/python2~usr\/bin\/python3~" ./deps/v8/tools/gen-inlining-tests.py
sed -i "s~usr\/bin\/python.*$~usr\/bin\/python2~" ./deps/v8/tools/mb/mb_unittest.py
find . -type f -exec sed -i "s~python -c~python2 -c~" {} \;
sed -i "s~which('python')~which('python2')~" configure

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

#%if ! 0%%{?bootstrap}
%if %{with bootstrap}
./configure --prefix=%{_prefix} \
           --shared-openssl \
           --shared-zlib \
           --without-dtrace \
           --with-intl=small-icu \
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
           --with-intl=%{icu_flag} \
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
NODE_PATH=%{buildroot}%{_prefix}/lib/node_modules:%{buildroot}%{_prefix}/lib/node_modules/npm/node_modules %{buildroot}/%{_bindir}/node -e "require(\"assert\").equal(require(\"npm\").version, '%{npm_version}')"


%pretrans -n npm -p <lua>
-- Remove all of the symlinks from the bundled npm node_modules directory
-- This scriptlet can be removed in Fedora 31
base_path = "%{_prefix}/lib/node_modules/npm/node_modules/"
d_st = posix.stat(base_path)
if d_st then
  for f in posix.files(base_path) do
    path = base_path..f
    st = posix.stat(path)
    if st and st.type == "link" then
      os.remove(path)
    end
  end
end

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
%{_pkgdocdir}/npm/html
%{_pkgdocdir}/npm/doc

%changelog
* Fri Jul 20 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.7.0-4
- Fix npm upgrade scriptlet
- Fix unexpected trailing .1 in npm release field

* Fri Jul 20 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.7.0-3
- Restore annotations to binaries
- Fix unexpected trailing .1 in release field

* Thu Jul 19 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.7.0-2
- Update to 10.7.0
- https://nodejs.org/en/blog/release/v10.7.0/
- https://nodejs.org/en/blog/release/v10.6.0/

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:10.5.0-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Jun 21 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.5.0-1
- Update to 10.5.0
- https://nodejs.org/en/blog/release/v10.5.0/

* Thu Jun 14 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.4.1-1
- Update to 10.4.1 to address security issues
- https://nodejs.org/en/blog/release/v10.4.1/
- Resolves: rhbz#1590801
- Resolves: rhbz#1591014
- Resolves: rhbz#1591019

* Thu Jun 07 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.4.0-1
- Update to 10.4.0
- https://nodejs.org/en/blog/release/v10.4.0/

* Wed May 30 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.3.0-1
- Update to 10.3.0
- Update npm to 6.1.0
- https://nodejs.org/en/blog/release/v10.3.0/

* Tue May 29 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.2.1-2
- Fix up bare 'python' to be python2
- Drop redundant entry in docs section

* Fri May 25 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.2.1-1
- Update to 10.2.1
- https://nodejs.org/en/blog/release/v10.2.1/

* Wed May 23 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.2.0-1
- Update to 10.2.0
- https://nodejs.org/en/blog/release/v10.2.0/

* Thu May 10 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.1.0-3
- Fix incorrect rpm macro

* Thu May 10 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.1.0-2
- Include upstream v8 fix for ppc64[le]
- Disable debug build on ppc64[le] and s390x

* Wed May 09 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.1.0-1
- Update to 10.1.0
- https://nodejs.org/en/blog/release/v10.1.0/
- Reenable node_g binary

* Thu Apr 26 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:10.0.0-1
- Update to 10.0.0
- https://nodejs.org/en/blog/release/v10.0.0/
- Drop workaround patch
- Temporarily drop node_g binary due to
  https://gcc.gnu.org/bugzilla/show_bug.cgi?id=85587

* Fri Apr 13 2018 Rafael dos Santos <rdossant@redhat.com> - 1:9.11.1-2
- Use standard Fedora linker flags (bug #1543859)

* Thu Apr 05 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:9.11.1-1
- Update to 9.11.1
- https://nodejs.org/en/blog/release/v9.11.0/
- https://nodejs.org/en/blog/release/v9.11.1/

* Wed Mar 28 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:9.10.0-1
- Update to 9.10.0
- https://nodejs.org/en/blog/release/v9.10.0/

* Wed Mar 21 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:9.9.0-1
- Update to 9.9.0
- https://nodejs.org/en/blog/release/v9.9.0/

* Thu Mar 08 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:9.8.0-1
- Update to 9.8.0
- https://nodejs.org/en/blog/release/v9.8.0/

* Thu Mar 01 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:9.7.0-1
- Update to 9.7.0
- https://nodejs.org/en/blog/release/v9.7.0/
- Work around F28 build issue

* Sun Feb 25 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:9.6.1-1
- Update to 9.6.1
- https://nodejs.org/en/blog/release/v9.6.1/
- https://nodejs.org/en/blog/release/v9.6.0/

* Mon Feb 05 2018 Stephen Gallagher <sgallagh@redhat.com> - 1:9.5.0-1
- Package Node.js 9.5.0

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

