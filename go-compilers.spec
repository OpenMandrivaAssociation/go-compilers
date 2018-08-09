%global debug_package   %{nil}

%global commit          aecba475bf76f5269c11367da0a190419cd9a133
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

%global m_commit        4d469a3d37c21353fbd6bb306ce707dc4151fd1e
%global m_shortcommit   %(c=%{m_commit}; echo ${c:0:7})

Name:           go-compilers
Version:        1
Release:        30%{?dist}
Summary:        Go language compilers for various architectures
Group:          Development/Tools
License:        GPLv3+
Source0:        https://github.com/gofed/symbols-extractor/archive/%{commit}/symbols-extractor-%{shortcommit}.tar.gz
Source1:        https://github.com/gofed/go-macros/archive/%{m_commit}/go-macros-%{m_shortcommit}.tar.gz
Patch0:         build-with-go-1.10.rc2.patch

ExclusiveArch:  %{go_arches}

# for install, cut and rm commands
BuildRequires:  coreutils
# for go specific macros
BuildRequires:  go-srpm-macros

%description
The package provides correct golang language compiler
base on an architectures.

%ifarch %{golang_arches}
%package golang-compiler
Summary:       compiler for golang

BuildRequires: golang

Requires:      golang

Provides:      compiler(go-compiler) = 2
Provides:      compiler(golang)

%description golang-compiler
Compiler for golang.
%endif

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
%if 0%{?fedora} > 27
%patch0 -p1
%endif
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

%install
%ifarch %{golang_arches}
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
%endif

%ifarch %{gccgo_arches}
install -m 644 -D rpm/macros.d/macros.go-compilers-gcc %{buildroot}%{_rpmconfigdir}/macros.d/macros.go-compilers-gcc
%endif

%ifarch %{golang_arches}
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
%endif

%ifarch %{gccgo_arches}
%files gcc-go-compiler
%{_rpmconfigdir}/macros.d/macros.go-compilers-gcc
%endif

%changelog
* Mon May 28 2018 Jan Chaloupka <jchaloup@redhat.com> - 1-30
- Bump to 4d469a3d37c21353fbd6bb306ce707dc4151fd1e
  Extend .goipath with commit
  Nits and improvements

* Tue Mar 20 2018 Jan Chaloupka <jchaloup@redhat.com> - 1-29
- Bump to c259c4ed880d10667974c460e5259605e32330f0
  Fix order of flags for gochecks and goinstall macros where -i and any of -d, -t, -r, -e are specified

* Fri Mar 16 2018 Jan Chaloupka <jchaloup@redhat.com> - 1-28
- Bump to 6f0cadc4c48f93f02eb573649e2a94eeef12f15c

* Fri Mar 09 2018 Jan Chaloupka <jchaloup@redhat.com> - 1-27
- allow supplying additional -tags arguments to %gobuild (via $BUILDTAGS)
  Upstream: https://github.com/gofed/go-macros/issues/22

* Wed Mar 07 2018 Jan Chaloupka <jchaloup@redhat.com> - 1-26
- Ignore testdata and all files/dirs that begin with . or _
  Upstream: https://github.com/gofed/go-macros/issues/21

* Sun Mar 04 2018 Jan Chaloupka <jchaloup@redhat.com> - 1-25
- Re-implement bash part of the macros

* Thu Mar 01 2018 Jan Chaloupka <jchaloup@redhat.com> - 1-24
- https://github.com/gofed/go-macros/issues/6: golist --provided should accept attribute decorators
- https://github.com/gofed/go-macros/issues/5: The Go utilities used by the macros should accept arbitrary numbers of flags

* Wed Feb 28 2018 Jan Chaloupka <jchaloup@redhat.com> - 1-23
- Copy hidden files as well

* Mon Feb 26 2018 Jan Chaloupka <jchaloup@redhat.com> - 1-22
- Fix the golist --to-install to count Cgo files as well

* Sat Feb 24 2018 Jan Chaloupka <jchaloup@redhat.com> - 1-21
- Allow to ignore root directory

* Fri Feb 23 2018 Jan Chaloupka <jchaloup@redhat.com> - 1-20
- Set _dwz_low_mem_die_limit only when a go binary is built

* Sun Feb 18 2018 Jan Chaloupka <jchaloup@redhat.com> - 1-19
- New macros: __go_ignore_dirs, __go_ignore_trees, __go_ignore_regex

* Sun Feb 18 2018 Jan Chaloupka <jchaloup@redhat.com> - 1-18
- Move all macros under github.com/gofed/go-macros repository
- Provide new macros autogenerating parts of Go spec files (int testing phase)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Jan 16 2018 Jakub Čajka <jcajka@redhat.com> - 1-16
- use build mode pie also for testing(we are getting pie ld flag from hardening), this resolves linker issues on ppc64le

* Thu Nov 30 2017 Jakub Čajka <jcajka@redhat.com> - 1-15
- allow to specify __golang_extldflags macro to specify extldflags with go* macros
- Resolves: rhbz#1502305

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jul 14 2017 Jakub Čajka <jcajka@redhat.com> - 1-12
- rebuild for ppc64 drop

* Wed Feb 15 2017 Jakub Čajka <jcajka@redhat.com> - 1-11
- pie is not supported on ppc64

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Jan 27 2017 Jakub Čajka <jcajka@redhat.com> - 1-9
- Add crash traceback level to golang as default
- Switch to PIE and push distribution ld flags
- Resolves BZ#1413529
- Related BZ#1411242

* Wed Jul 20 2016 Jakub Čajka <jcajka@redhat.com> - 1-8
- Build for s390x switch to golang
- Related: bz1357394

* Wed Apr 13 2016 Dan Horák <dan[at]danny.cz> - 1-7
- fix bug in gcc-go version of gotest macro

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 28 2016 Jakub Čajka <jcajka@redhat.com> - 1-5
- Build for {power64} switch to golang

* Fri Jan 22 2016 Jakub Čajka <jcajka@redhat.com> - 1-4
- version provides to make seamless transition between compilers possible
- Resolves: bz#1300717

* Thu Nov 12 2015 Jakub Čajka <jcajka@redhat.com> - 1-3
- remove version requirement from gcc-go subpackage to avoid cyclic
  dependency due to macro declaration in subpackage

* Thu Sep 10 2015 jchaloup <jchaloup@redhat.com> - 1-2
- go_compiler macro must be in go-srpm-macros package as it is used
  to pick compiler(go-compiler) which would provide go_compiler

* Tue Jul 07 2015 Jan Chaloupka <jchaloup@redhat.com> - 1-1
- Initial commit
  resolves: #1258182
