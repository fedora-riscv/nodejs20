#!/bin/sh
# Uses Argbash to generate command argument parsing. To update
# arguments, make sure to call
# `argbash nodejs-tarball.sh -o nodejs-tarball.sh`

# ARG_POSITIONAL_SINGLE([version],[Node.js release version])
# ARG_OPTIONAL_BOOLEAN([push],[],[Whether to upload to the lookaside cache],[on])
# ARG_DEFAULTS_POS([])
# ARG_HELP([Tool to aid in Node.js packaging of new releases])
# ARGBASH_GO()
# needed because of Argbash --> m4_ignore([
### START OF CODE GENERATED BY Argbash v2.10.0 one line above ###
# Argbash is a bash code generator used to get arguments parsing right.
# Argbash is FREE SOFTWARE, see https://argbash.io for more info


die()
{
	local _ret="${2:-1}"
	test "${_PRINT_HELP:-no}" = yes && print_help >&2
	echo "$1" >&2
	exit "${_ret}"
}


begins_with_short_option()
{
	local first_option all_short_options='h'
	first_option="${1:0:1}"
	test "$all_short_options" = "${all_short_options/$first_option/}" && return 1 || return 0
}

# THE DEFAULTS INITIALIZATION - POSITIONALS
_positionals=()
_arg_version=
# THE DEFAULTS INITIALIZATION - OPTIONALS
_arg_push="on"


print_help()
{
	printf '%s\n' "Tool to aid in Node.js packaging of new releases"
	printf 'Usage: %s [--(no-)push] [-h|--help] <version>\n' "$0"
	printf '\t%s\n' "<version>: Node.js release version"
	printf '\t%s\n' "--push, --no-push: Whether to upload to the lookaside cache (on by default)"
	printf '\t%s\n' "-h, --help: Prints help"
}


parse_commandline()
{
	_positionals_count=0
	while test $# -gt 0
	do
		_key="$1"
		case "$_key" in
			--no-push|--push)
				_arg_push="on"
				test "${1:0:5}" = "--no-" && _arg_push="off"
				;;
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
	local _required_args_string="'version'"
	test "${_positionals_count}" -ge 1 || _PRINT_HELP=yes die "FATAL ERROR: Not enough positional arguments - we require exactly 1 (namely: $_required_args_string), but got only ${_positionals_count}." 1
	test "${_positionals_count}" -le 1 || _PRINT_HELP=yes die "FATAL ERROR: There were spurious positional arguments --- we expect exactly 1 (namely: $_required_args_string), but got ${_positionals_count} (the last one was: '${_last_positional}')." 1
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

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

alias wget='wget --quiet'

packages=("jq" "wget" "tar" "fedpkg" "grep" "sed")

rpm -q ${packages[@]} >/dev/null
if [ $? -ne 0 ]; then
  sudo dnf -y install ${packages[@]}
fi

set -e

version=$_arg_version

NODE_MAJOR=$(echo $version | cut -d. -f1)
NODE_MINOR=$(echo $version | cut -d. -f2)
NODE_PATCH=$(echo $version | cut -d. -f3)

# Treat odd-numbered major releases as pre-releases for the
# next LTS release.
if [[ $((NODE_MAJOR % 2)) -eq 0 ]];
  then NODE_PKG_MAJOR=${NODE_MAJOR};
  else NODE_PKG_MAJOR=$((NODE_MAJOR + 1));
fi

FEDORA_DEFAULT_RELEASE_LOW=$((NODE_PKG_MAJOR + 19))
FEDORA_DEFAULT_RELEASE_HIGH=$((NODE_PKG_MAJOR + 20))

if [[ $((NODE_PKG_MAJOR)) -eq 20 ]]
  then RHEL_DEFAULT_RELEASE=" | 0%{?rhel} == 10"
fi

rm -rf node-v${version}.tar.gz \
       node-v${version}-stripped.tar.gz \
       node-v${version}/ \
       wasi-sdk-* \
       cjs-module-lexer* \
       undici* \
       SHASUMS256.txt
echo Downloading node-v${version}.tar.gz
wget http://nodejs.org/dist/v${version}/node-v${version}.tar.gz \
     http://nodejs.org/dist/v${version}/SHASUMS256.txt
echo Validating sha256sum
sha256sum -c SHASUMS256.txt --ignore-missing
rm -f SHASUMS256.txt
tar -zxf node-v${version}.tar.gz

# Remove bundled OpenSSL
# We will link to the system version
rm -rf node-v${version}/deps/openssl
tar -zcf node-v${version}-stripped.tar.gz node-v${version}

# Download the cjs-module-lexer sources
LEXER_VERSION=$(jq -r '.version' node-v${version}/deps/cjs-module-lexer/package.json)
wget https://github.com/nodejs/cjs-module-lexer/archive/refs/tags/${LEXER_VERSION}.tar.gz
tar -zxf ${LEXER_VERSION}.tar.gz
rm -f cjs-module-lexer-${LEXER_VERSION}/lib/lexer.wasm
tar -zcf cjs-module-lexer-${LEXER_VERSION}-stripped.tar.gz cjs-module-lexer-${LEXER_VERSION}/
rm -f ${LEXER_VERSION}.tar.gz

# Download the WASI compiler used to build cjs-module-lexer
LEXER_WASI_MAJOR=$(grep -oP '(?<=^\W../wasi-sdk-)\d+\.\d+' cjs-module-lexer-${LEXER_VERSION}/Makefile | cut -d'.'  -f1)
LEXER_WASI_MINOR=$(grep -oP '(?<=^\W../wasi-sdk-)\d+\.\d+' cjs-module-lexer-${LEXER_VERSION}/Makefile | cut -d'.'  -f2)
wget https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-${LEXER_WASI_MAJOR}/wasi-sdk-${LEXER_WASI_MAJOR}.${LEXER_WASI_MINOR}-linux.tar.gz
rm -rf cjs-module-lexer-${LEXER_VERSION}/

# Download the undici sources
UNDICI_VERSION=$(jq -r '.version' node-v${version}/deps/undici/src/package.json)
wget https://github.com/nodejs/undici/archive/refs/tags/v${UNDICI_VERSION}.tar.gz
tar -zxf v${UNDICI_VERSION}.tar.gz
rm -f undici-${UNDICI_VERSION}/lib/llhttp/llhttp*.wasm*
tar -zcf undici-${UNDICI_VERSION}-stripped.tar.gz undici-${UNDICI_VERSION}/
rm -f v${UNDICI_VERSION}.tar.gz

# Download the WASI compiler used to build undici
UNDICI_WASI_MAJOR=$(grep -oP '(?<=WASI_SDK_VERSION_MAJOR=).*' undici-${UNDICI_VERSION}/build/Dockerfile)
UNDICI_WASI_MINOR=$(grep -oP '(?<=WASI_SDK_VERSION_MINOR=).*' undici-${UNDICI_VERSION}/build/Dockerfile)
wget https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-${UNDICI_WASI_MAJOR}/wasi-sdk-${UNDICI_WASI_MAJOR}.${UNDICI_WASI_MINOR}-linux.tar.gz
rm -rf undici-${UNDICI_VERSION}/

ICU_MAJOR=$(jq -r '.[0].url' node-v${version}/tools/icu/current_ver.dep | sed --expression='s/.*release-\([[:digit:]]\+\)-\([[:digit:]]\+\).*/\1/g')
ICU_MINOR=$(jq -r '.[0].url' node-v${version}/tools/icu/current_ver.dep | sed --expression='s/.*release-\([[:digit:]]\+\)-\([[:digit:]]\+\).*/\2/g')

# Download the ICU binary data files
rm -Rf icu4c-${ICU_MAJOR}_${ICU_MINOR}-data-bin-*.zip
wget $(grep Source3 packaging/nodejs.spec.j2 | sed --expression="s/.*http/http/g" --expression="s/\(\%{icu_major}\)/${ICU_MAJOR}/g" --expression="s/\(\%{icu_minor}\)/${ICU_MINOR}/g")
wget $(grep Source4 packaging/nodejs.spec.j2 | sed --expression="s/.*http/http/g" --expression="s/\(\%{icu_major}\)/${ICU_MAJOR}/g" --expression="s/\(\%{icu_minor}\)/${ICU_MINOR}/g")

rm -f node-v${version}.tar.gz

set +e

# Determine the bundled versions of the various packages
echo "Included software versions"
echo "-------------------------"
echo
echo "Node.js version"
echo "========================="
echo "${version}"
echo
echo "libnode shared object version"
echo "========================="
NODE_SOVERSION=$(grep -oP '(?<=#define NODE_MODULE_VERSION )\d+' node-v${version}/src/node_version.h)
echo "${NODE_SOVERSION}"
echo
echo "V8"
echo "========================="
V8_MAJOR=$(grep -oP '(?<=#define V8_MAJOR_VERSION )\d+' node-v${version}/deps/v8/include/v8-version.h)
V8_MINOR=$(grep -oP '(?<=#define V8_MINOR_VERSION )\d+' node-v${version}/deps/v8/include/v8-version.h)
V8_BUILD=$(grep -oP '(?<=#define V8_BUILD_NUMBER )\d+' node-v${version}/deps/v8/include/v8-version.h)
V8_PATCH=$(grep -oP '(?<=#define V8_PATCH_LEVEL )\d+' node-v${version}/deps/v8/include/v8-version.h)
echo "${V8_MAJOR}.${V8_MINOR}.${V8_BUILD}.${V8_PATCH}"
echo
echo "c-ares"
echo "========================="
C_ARES_VERSION=$(grep -oP '(?<=#define ARES_VERSION_STR ).*\"' node-v${version}/deps/cares/include/ares_version.h |sed -e 's/^"//' -e 's/"$//')
echo $C_ARES_VERSION
echo
echo "llhttp"
echo "========================="
LLHTTP_MAJOR=$(grep -oP '(?<=#define LLHTTP_VERSION_MAJOR )\d+' node-v${version}/deps/llhttp/include/llhttp.h)
LLHTTP_MINOR=$(grep -oP '(?<=#define LLHTTP_VERSION_MINOR )\d+' node-v${version}/deps/llhttp/include/llhttp.h)
LLHTTP_PATCH=$(grep -oP '(?<=#define LLHTTP_VERSION_PATCH )\d+' node-v${version}/deps/llhttp/include/llhttp.h)
LLHTTP_VERSION="${LLHTTP_MAJOR}.${LLHTTP_MINOR}.${LLHTTP_PATCH}"
echo $LLHTTP_VERSION
echo
echo "libuv"
echo "========================="
UV_MAJOR=$(grep -oP '(?<=#define UV_VERSION_MAJOR )\d+' node-v${version}/deps/uv/include/uv/version.h)
UV_MINOR=$(grep -oP '(?<=#define UV_VERSION_MINOR )\d+' node-v${version}/deps/uv/include/uv/version.h)
UV_PATCH=$(grep -oP '(?<=#define UV_VERSION_PATCH )\d+' node-v${version}/deps/uv/include/uv/version.h)
LIBUV_VERSION="${UV_MAJOR}.${UV_MINOR}.${UV_PATCH}"
echo $UV_VERSION
echo
echo "nghttp2"
echo "========================="
NGHTTP2_VERSION=$(grep -oP '(?<=#define NGHTTP2_VERSION ).*\"' node-v${version}/deps/nghttp2/lib/includes/nghttp2/nghttp2ver.h |sed -e 's/^"//' -e 's/"$//')
echo $NGHTTP2_VERSION
echo
echo "ICU"
echo "========================="
echo "${ICU_MAJOR}.${ICU_MINOR}"
echo
echo "punycode"
echo "========================="
PUNYCODE_VERSION=$(/usr/bin/node -e "console.log(require('punycode').version)")
echo $PUNYCODE_VERSION
echo
echo "uvwasi"
echo "========================="
UVWASI_MAJOR=$(grep -oP '(?<=#define UVWASI_VERSION_MAJOR )\d+' node-v${version}/deps/uvwasi/include/uvwasi.h)
UVWASI_MINOR=$(grep -oP '(?<=#define UVWASI_VERSION_MINOR )\d+' node-v${version}/deps/uvwasi/include/uvwasi.h)
UVWASI_PATCH=$(grep -oP '(?<=#define UVWASI_VERSION_PATCH )\d+' node-v${version}/deps/uvwasi/include/uvwasi.h)
UVWASI_VERSION="${UVWASI_MAJOR}.${UVWASI_MINOR}.${UVWASI_PATCH}"
echo $UVWASI_VERSION
echo
echo "npm"
echo "========================="
NPM_VERSION=$(jq -r .version ./node-v${version}/deps/npm/package.json)
echo $NPM_VERSION
echo
echo "zlib"
echo "========================="
ZLIB_VERSION=$(grep -oP '(?<=#define ZLIB_VERSION ).*\"' node-v${version}/deps/zlib/zlib.h |sed -e 's/^"//' -e 's/"$//')
echo $ZLIB_VERSION
echo
echo "cjs-module-lexer"
echo "========================="
echo "${LEXER_VERSION}"
echo "WASI-SDK: ${LEXER_WASI_MAJOR}.${LEXER_WASI_MINOR}"
echo
echo "undici"
echo "========================="
echo "${UNDICI_VERSION}"
echo "WASI-SDK: ${UNDICI_WASI_MAJOR}.${UNDICI_WASI_MINOR}"
echo
echo "ada"
echo "========================="
ADA_VERSION=$(grep -osP '(?<=#define ADA_VERSION ).*\"' node-v${version}/deps/ada/ada.h |sed -e 's/^"//' -e 's/"$//')
ADA_VERSION=${ADA_VERSION:-0}
echo "${ADA_VERSION}"
echo
echo "Applying versions to spec template"

# Get the list of patches we need to add to the specfile
readarray -t patchlist < <(git ls-files |grep '^[0-9]\{4\}-.*\.patch')
json_patchlist=$(jq --compact-output --null-input '$ARGS.positional' --args -- "${patchlist[@]}")

IFS='' read -r -d '' template_json <<EOF
{
    "NODE_PKG_MAJOR": $NODE_PKG_MAJOR,
    "NODE_MAJOR": $NODE_MAJOR,
    "NODE_MINOR": $NODE_MINOR,
    "NODE_PATCH": $NODE_PATCH,
    "FEDORA_DEFAULT_RELEASE_LOW": $FEDORA_DEFAULT_RELEASE_LOW,
    "FEDORA_DEFAULT_RELEASE_HIGH": $FEDORA_DEFAULT_RELEASE_HIGH,
	"RHEL_DEFAULT_RELEASE": "$RHEL_DEFAULT_RELEASE",
    "NODE_SOVERSION": $NODE_SOVERSION,
    "V8_MAJOR": $V8_MAJOR,
    "V8_MINOR": $V8_MINOR,
    "V8_BUILD": $V8_BUILD,
    "V8_PATCH": $V8_PATCH,
    "C_ARES_VERSION": $C_ARES_VERSION,
    "LLHTTP_VERSION": $LLHTTP_VERSION,
    "LIBUV_VERSION": $LIBUV_VERSION,
    "NGHTTP2_VERSION": $NGHTTP2_VERSION,
    "ICU_MAJOR": $ICU_MAJOR,
    "ICU_MINOR": $ICU_MINOR,
    "PUNYCODE_VERSION": $PUNYCODE_VERSION,
    "UVWASI_VERSION": $UVWASI_VERSION,
    "NPM_VERSION": $NPM_VERSION,
    "ZLIB_VERSION": $ZLIB_VERSION,
    "LEXER_VERSION": $LEXER_VERSION,
    "LEXER_WASI_MAJOR": $LEXER_WASI_MAJOR,
    "LEXER_WASI_MINOR": $LEXER_WASI_MINOR,
    "UNDICI_VERSION": $UNDICI_VERSION,
    "UNDICI_WASI_MAJOR": $UNDICI_WASI_MAJOR,
    "UNDICI_WASI_MINOR": $UNDICI_WASI_MINOR,
    "ADA_VERSION": $ADA_VERSION,
	"PATCHES": $json_patchlist
}
EOF

echo ${template_json} | jinja2 ${SCRIPT_DIR}/packaging/nodejs.spec.j2 \
    > ${SCRIPT_DIR}/nodejs${NODE_PKG_MAJOR}.spec

if [ $_arg_push = 'on' ]; then
  fedpkg new-sources node-v${version}-stripped.tar.gz \
                     icu4c-${ICU_MAJOR}_${ICU_MINOR}-data-bin-*.zip \
                     cjs-module-lexer-${LEXER_VERSION}-stripped.tar.gz \
                     wasi-sdk-${LEXER_WASI_MAJOR}.${LEXER_WASI_MINOR}-linux.tar.gz \
                     undici-${UNDICI_VERSION}-stripped.tar.gz \
                     wasi-sdk-${UNDICI_WASI_MAJOR}.${UNDICI_WASI_MINOR}-linux.tar.gz
fi

rm -rf node-v${version}
# ] <-- needed because of Argbash
