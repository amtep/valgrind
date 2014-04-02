#specfile originally created for Fedora, modified for Mer
Summary: Tool for finding memory management bugs in programs
Name: valgrind
Version: 3.9.0
Release: 1
Source0: http://www.valgrind.org/downloads/%{name}-%{version}.tar.bz2
License: GPLv2
URL: http://www.valgrind.org/
Group: Development/Debuggers
ExclusiveArch: %{ix86} %{arm}
BuildRequires: pkgconfig

%ifarch %{ix86}
%define valarch x86
%define valsecarch %{nil}
%endif
%ifarch %{arm}
%define valarch arm
%define valsecarch %{nil}
%endif

%description
Valgrind is a tool to help you find memory-management problems in your
programs. When a program is run under Valgrind\'s supervision, all
reads and writes of memory are checked, and calls to
malloc/new/free/delete are intercepted. As a result, Valgrind can
detect a lot of problems that are otherwise very hard to
find/diagnose.

%package devel
Summary: Development files for valgrind
Group: Development/Debuggers
Requires: valgrind = %{version}-%{release}

%description devel
Header files and libraries for development of valgrind aware programs
or valgrind plugins.

%package doc
Summary: Documentation for valgrind
Group: Development/Debuggers
Requires: valgrind = %{version}-%{release}

%description doc
%{summary}.

# valgrind enforces usage of -Wl,--build-id=none 
# and debug packages requires build-id, so disable them
%define debug_package %{nil}

%prep
%setup -q -n %{name}-%{version}/%{name}

%build

# not a good idea to build valgrind with fortify, as it does not link glibc
RPM_OPT_FLAGS="`echo " %{optflags} " | sed 's/ -m\(64\|3[21]\) / /g;s/ -fexceptions / /g;s/^ //;s/ $//' | \
    sed s/-Wp,-D_FORTIFY_SOURCE=2// | sed s/-D_FORTIFY_SOURCE=2//`"

export CFLAGS="$RPM_OPT_FLAGS -DVSCREENINFO_BORKAGE"
export CXXFLAGS="$RPM_OPT_FLAGS -DVSCREENINFO_BORKAGE"
autoreconf -fi
export GDB=/usr/bin/gdb

%configure CFLAGS="$CFLAGS" CXXFLAGS="$CXXFLAGS"
make %{_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

%makeinstall
mkdir docs.installed
mv $RPM_BUILD_ROOT%{_datadir}/doc/valgrind/* docs.installed/
rm -f docs.installed/*.ps

%if "%{valsecarch}" != ""
pushd $RPM_BUILD_ROOT%{_libdir}/valgrind/
rm -f *-%{valsecarch}-* || :
for i in *-%{valarch}-*; do
  j=`echo $i | sed 's/-%{valarch}-/-%{valsecarch}-/'`
  ln -sf ../../lib/valgrind/$j $j
done
popd
%endif

rm -f $RPM_BUILD_ROOT%{_libdir}/valgrind/*.supp.in

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc COPYING NEWS README_*
%{_bindir}/*
%dir %{_libdir}/valgrind
%{_libdir}/valgrind/*[^ao]
%{_libdir}/valgrind/[^l]*o

%files devel
%defattr(-,root,root)
%{_includedir}/valgrind
%dir %{_libdir}/valgrind
%{_libdir}/valgrind/*.a
%{_libdir}/pkgconfig/*

%files doc
%defattr(-,root,root)
%doc docs.installed/html docs.installed/*.pdf
%{_mandir}/man1/*
