#!/bin/sh
# Uses Argbash to generate command argument parsing. To update
# arguments, make sure to call
# `argbash nodejs-tarball.sh -o nodejs-tarball.sh`

# ARG_POSITIONAL_SINGLE([version],[Node.js release version],[""])
# ARG_DEFAULTS_POS([])
# ARG_HELP([Tool to aid in Node.js packaging of new releases])
# ARGBASH_GO()
# needed because of Argbash --> m4_ignore([
### START OF CODE GENERATED BY Argbash v2.8.1 one line above ###
# Argbash is a bash code generator used to get arguments parsing right.
# Argbash is FREE SOFTWARE, see https://argbash.io for more info


die()
{
	local _ret=$2
	test -n "$_ret" || _ret=1
	test "$_PRINT_HELP" = yes && print_help >&2
	echo "$1" >&2
	exit ${_ret}
}


begins_with_short_option()
{
	local first_option all_short_options='h'
	first_option="${1:0:1}"
	test "$all_short_options" = "${all_short_options/$first_option/}" && return 1 || return 0
}

# THE DEFAULTS INITIALIZATION - POSITIONALS
_positionals=()
_arg_version=""
# THE DEFAULTS INITIALIZATION - OPTIONALS


print_help()
{
	printf '%s\n' "Tool to aid in Node.js packaging of new releases"
	printf 'Usage: %s [-h|--help] [<version>]\n' "$0"
	printf '\t%s\n' "<version>: Node.js release version (default: '""')"
	printf '\t%s\n' "-h, --help: Prints help"
}


parse_commandline()
{
	_positionals_count=0
	while test $# -gt 0
	do
		_key="$1"
		case "$_key" in
			-h|--help)
				print_help
				exit 0
				;;
			-h*)
				print_help
				exit 0
				;;
			*)
				_last_positional="$1"
				_positionals+=("$_last_positional")
				_positionals_count=$((_positionals_count + 1))
				;;
		esac
		shift
	done
}


handle_passed_args_count()
{
	test "${_positionals_count}" -le 1 || _PRINT_HELP=yes die "FATAL ERROR: There were spurious positional arguments --- we expect between 0 and 1, but got ${_positionals_count} (the last one was: '${_last_positional}')." 1
}


assign_positional_args()
{
	local _positional_name _shift_for=$1
	_positional_names="_arg_version "

	shift "$_shift_for"
	for _positional_name in ${_positional_names}
	do
		test $# -gt 0 || break
		eval "$_positional_name=\${1}" || die "Error during argument parsing, possibly an Argbash bug." 1
		shift
	done
}

parse_commandline "$@"
handle_passed_args_count
assign_positional_args 1 "${_positionals[@]}"

# OTHER STUFF GENERATED BY Argbash

### END OF CODE GENERATED BY Argbash (sortof) ### ])
# [ <-- needed because of Argbash


set -e

echo $_arg_version

if [ x$_arg_version != x ]; then
    version=$_arg_version
else
    version=$(rpm -q --specfile --qf='%{version}\n' nodejs.spec | head -n1)
fi

rm -rf node-v${version}.tar.gz \
       node-v${version}-stripped.tar.gz \
       node-v${version}/ \
       SHASUMS256.txt
wget http://nodejs.org/dist/v${version}/node-v${version}.tar.gz \
     http://nodejs.org/dist/v${version}/SHASUMS256.txt
sha256sum -c SHASUMS256.txt --ignore-missing
tar -zxf node-v${version}.tar.gz
rm -rf node-v${version}/deps/openssl
tar -zcf node-v${version}-stripped.tar.gz node-v${version}

# Download the matching version of ICU
rm -f icu4c*-src.tgz icu.md5
ICUMD5=$(cat node-v${version}/tools/icu/current_ver.dep |jq -r '.[0].md5')
wget $(cat node-v${version}/tools/icu/current_ver.dep |jq -r '.[0].url')
ICUTARBALL=$(ls -1 icu4c*-src.tgz)
echo "$ICUMD5  $ICUTARBALL" > icu.md5
md5sum -c icu.md5
rm -f icu.md5 SHASUMS256.txt

fedpkg new-sources node-v${version}-stripped.tar.gz icu4c*-src.tgz

rm -f node-v${version}.tar.gz

set +e

# Determine the bundled versions of the various packages
echo "Bundled software versions"
echo "-------------------------"
echo
echo "libnode shared object version"
echo "========================="
grep "define NODE_MODULE_VERSION" node-v${version}/src/node_version.h
echo
echo "V8"
echo "========================="
grep "define V8_MAJOR_VERSION" node-v${version}/deps/v8/include/v8-version.h
grep "define V8_MINOR_VERSION" node-v${version}/deps/v8/include/v8-version.h
grep "define V8_BUILD_NUMBER" node-v${version}/deps/v8/include/v8-version.h
grep "define V8_PATCH_LEVEL" node-v${version}/deps/v8/include/v8-version.h
echo
echo "c-ares"
echo "========================="
grep "define ARES_VERSION_MAJOR" node-v${version}/deps/cares/include/ares_version.h
grep "define ARES_VERSION_MINOR" node-v${version}/deps/cares/include/ares_version.h
grep "define ARES_VERSION_PATCH" node-v${version}/deps/cares/include/ares_version.h
echo
echo "llhttp"
echo "========================="
grep "define LLHTTP_VERSION_MAJOR" node-v${version}/deps/llhttp/include/llhttp.h
grep "define LLHTTP_VERSION_MINOR" node-v${version}/deps/llhttp/include/llhttp.h
grep "define LLHTTP_VERSION_PATCH" node-v${version}/deps/llhttp/include/llhttp.h
echo
echo "libuv"
echo "========================="
grep "define UV_VERSION_MAJOR" node-v${version}/deps/uv/include/uv/version.h
grep "define UV_VERSION_MINOR" node-v${version}/deps/uv/include/uv/version.h
grep "define UV_VERSION_PATCH" node-v${version}/deps/uv/include/uv/version.h
echo
echo "nghttp2"
echo "========================="
grep "define NGHTTP2_VERSION " node-v${version}/deps/nghttp2/lib/includes/nghttp2/nghttp2ver.h
echo
echo "ICU"
echo "========================="
grep "url" node-v${version}/tools/icu/current_ver.dep
echo
echo "punycode"
echo "========================="
grep "'version'" node-v${version}/lib/punycode.js
echo
echo "uvwasi"
echo "========================="
grep "define UVWASI_VERSION_MAJOR" node-v${version}/deps/uvwasi/include/uvwasi.h
grep "define UVWASI_VERSION_MINOR" node-v${version}/deps/uvwasi/include/uvwasi.h
grep "define UVWASI_VERSION_PATCH" node-v${version}/deps/uvwasi/include/uvwasi.h
echo
echo "npm"
echo "========================="
grep "\"version\":" node-v${version}/deps/npm/package.json
echo
echo "zlib"
echo "========================="
grep "define ZLIB_VERSION" node-v${version}/deps/zlib/zlib.h
echo
echo "Make sure these versions match what is in the RPM spec file"

rm -rf node-v${version}
# ] <-- needed because of Argbash
