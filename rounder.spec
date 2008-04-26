%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name: rounder
Version: 0.0.1
Release:        1%{?dist}
Summary: An online poker server and clients

Group: Amusements/Games
License: GPL
URL: http://dangerouslyinc.com/rounder
Source0: http://dangerouslyinc.com/files/rounder/rounder-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch: noarch
BuildRequires: python-devel

Requires: python-cerealizer >= 0.6
Requires: python-twisted >= 2.4.0

%description
Rounder is an open source poker suite consisting of an engine, server, and
various client implementations. It allows you to play online with friends
and hopefully one day to build a non-monetary online poker community.
%prep
%setup -q -n rounder-%{version}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{python_sitelib}/*egg-info/requires.txt


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc AUTHORS
%doc LICENSE
%doc README
%{_bindir}/rounder
%{_bindir}/rounder-server
%{_bindir}/rounder-randombot
%dir %{python_sitelib}/rounder
%{python_sitelib}/rounder/*


%changelog
* Sat Apr 26 2008 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.1-1
- Initial packaging.
