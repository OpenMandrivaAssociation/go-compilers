%global debug_package   %{nil}

%global commit          9f4330a0f4437ca61ba92f9f30e34424c6742ad6
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

%global m_commit        4d469a3d37c21353fbd6bb306ce707dc4151fd1e
%global m_shortcommit   %(c=%{m_commit}; echo ${c:0:7})

Name:           go-compilers
Version:        1
Release:        32%{?dist}
Summary:        Go language compilers for various architectures
Group:          Development/Tools
License:        GPLv3+
Source0:        https://github.com/gofed/symbols-extractor/archive/%{commit}/symbols-extractor-%{shortcommit}.tar.gz
Source1:        https://github.com/gofed/go-macros/archive/%{m_commit}/go-macros-%{m_shortcommit}.tar.gz

# for install, cut and rm commands
BuildRequires:  coreutils
# for go specific macros
BuildRequires:  go-srpm-macros

%description
The package provides correct golang language compiler
base on an architectures.

%package golang-compiler
Summary:       compiler for golang

BuildRequires: golang

Requires:      golang

Provides:      compiler(go-compiler) = 2
Provides:      compiler(golang)

%description golang-compiler
Compiler for golang.

%ifarch %{gccgo_arches}
%package gcc-go-compiler
Summary:       compiler for gcc-go

# GCC>=5 holds in Fedora now
Requires:      gcc-go

Provides:      compiler(go-compiler) = 1
Provides:      compiler(gcc-go)

%description gcc-go-compiler
Compiler for gcc-go.
%endif

%prep
%setup -q -n symbols-extractor-%{commit}
%setup -q -n go-macros-%{m_commit} -T -b 1

%build
mkdir -p src/github.com/gofed
pushd ../symbols-extractor-%{commit}
export GOPATH=$(pwd):%{gopath}
# TODO(jchaloup): build it as part of the golang compiler or to-be symbols-extractor package
sed -i "s/.*\/cmd\/extract.*/\t\\\\/" Makefile
sed -i "s/.*\/cmd\/checkapi.*/\t\\\\/" Makefile
make
popd

echo $GOROOT

%install
# executables
install -m 755 -D bin/go-rpm-integration %{buildroot}%{_bindir}/go-rpm-integration
install -m 755 -D rpm/gobundled.prov %{buildroot}%{_rpmconfigdir}/gobundled.prov
install -m 755 -D rpm/gosymlink.deps %{buildroot}%{_rpmconfigdir}/gosymlink.deps
# macros
install -m 644 -D rpm/macros.d/macros.go-compilers-golang %{buildroot}%{_rpmconfigdir}/macros.d/macros.go-compilers-golang
install -m 644 -D rpm/macros.d/macros.go-rpm %{buildroot}%{_rpmconfigdir}/macros.d/macros.go-rpm
# attrs
install -m 644 -D rpm/fileattrs/go.attr %{buildroot}%{_rpmconfigdir}/fileattrs/go.attr
install -m 644 -D rpm/fileattrs/gobundled.attr %{buildroot}%{_rpmconfigdir}/fileattrs/gobundled.attr
install -m 644 -D rpm/fileattrs/gosymlink.attr %{buildroot}%{_rpmconfigdir}/fileattrs/gosymlink.attr

pushd ../symbols-extractor-%{commit}
install -D -p -m 0755 golist %{buildroot}%{_bindir}/golist
popd

%ifarch %{gccgo_arches}
install -m 644 -D rpm/macros.d/macros.go-compilers-gcc %{buildroot}%{_rpmconfigdir}/macros.d/macros.go-compilers-gcc
%endif

%files golang-compiler
%{_rpmconfigdir}/macros.d/macros.go-compilers-golang
%{_rpmconfigdir}/macros.d/macros.go-rpm
%{_rpmconfigdir}/gobundled.prov
%{_rpmconfigdir}/gosymlink.deps
%{_rpmconfigdir}/fileattrs/go.attr
%{_rpmconfigdir}/fileattrs/gobundled.attr
%{_rpmconfigdir}/fileattrs/gosymlink.attr
%{_bindir}/golist
%{_bindir}/go-rpm-integration

%ifarch %{gccgo_arches}
%files gcc-go-compiler
%{_rpmconfigdir}/macros.d/macros.go-compilers-gcc
%endif
