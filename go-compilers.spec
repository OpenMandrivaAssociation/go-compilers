%global debug_package %{nil}

%global commit		4d469a3d37c21353fbd6bb306ce707dc4151fd1e
%global shortcommit	%(c=%{m_commit}; echo ${c:0:7})

# actually gcc-go is not packaged
%bcond_with gcc

Summary:	Go language compilers for various architectures
Name:		go-compilers
Version:	1
License:	GPLv3+
Group:		Development/Tools
Release:	41
URL:		https://github.com/gofed/go-macros
Source0:	https://github.com/gofed/go-macros/archive/%{commit}/go-macros-%{commit}.tar.gz
Patch0:		go-srpm-macros-2-dont_download_missing_modules.patch
Patch1:		go-srpm-macros-2-provides.patch
# for install, cut and rm commands
BuildRequires:	coreutils
# for go specific macros
BuildRequires:	go-srpm-macros

%description
The package provides correct golang language compiler
base on an architectures.

#-----------------------------------------------------------------------

%package golang-compiler
Summary:		compiler for golang
BuildRequires:	golang
Requires:		golang
Requires:		golist
Provides:		compiler(go-compiler) = 2
Provides:		compiler(golang)

%description golang-compiler
Compiler for golang.

%files golang-compiler
%{_bindir}/go-rpm-integration
%{_rpmconfigdir}/macros.d/macros.go-compilers-golang
%{_rpmconfigdir}/macros.d/macros.go-rpm
%{_rpmconfigdir}/gobundled.prov
%{_rpmconfigdir}/gosymlink.deps
%{_rpmconfigdir}/fileattrs/go.attr
%{_rpmconfigdir}/fileattrs/gobundled.attr
%{_rpmconfigdir}/fileattrs/gosymlink.attr

#-----------------------------------------------------------------------

%if %{with gcc}
%package gcc-go-compiler
Summary:	compiler for gcc-go
Requires:	gcc-go
Provides:	compiler(go-compiler) = 1
Provides:	compiler(gcc-go)

%description gcc-go-compiler
Compiler for gcc-go.

%files gcc-go-compiler
%{_rpmconfigdir}/macros.d/macros.go-compilers-gcc
%endif

#-----------------------------------------------------------------------

%prep
%autosetup -p1 -n go-macros-%{commit}

# remove pre-build binaries
# golist is now provided by a separate package
rm -fr bin/golist

%build

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

%if %{with gcc}
install -m 644 -D rpm/macros.d/macros.go-compilers-gcc %{buildroot}%{_rpmconfigdir}/macros.d/macros.go-compilers-gcc
sed -i 's!%__global_ldflags!%%{ldflags}!g' %{buildroot}%{_rpmconfigdir}/macros.d/macros.go-compilers-gcc
%endif

sed -i 's!%__global_ldflags!%%{ldflags}!g' %{buildroot}%{_rpmconfigdir}/macros.d/macros.go-compilers-golang

