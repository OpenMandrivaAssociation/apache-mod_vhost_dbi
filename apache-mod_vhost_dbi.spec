#Module-Specific definitions
%define mod_name mod_vhost_dbi
%define mod_conf A80_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Provides database connection pooling services for the apache web server
Name:		apache-%{mod_name}
Version:	0.1.0
Release:	%mkrel 2
Group:		System/Servers
License:	GPL
URL:		http://www.outoforder.cc/projects/apache/mod_vhost_dbi/
Source0:	http://www.outoforder.cc/downloads/mod_vhost_dbi/%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}.bz2
Patch0:		mod_vhost_dbi-0.1.0-module.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
BuildRequires:	libdbi-devel >= 0.8.1
BuildRequires:	apache-mod_dbi_pool-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_vhost_dbi creates virtual hosts for Apache 2.0 completely dynamically,
without the need to edit your configuration file or restart Apache if you
change a Vhost.

%prep

%setup -q -n %{mod_name}-%{version}
%patch0 -p1

# stupid libtool...
perl -pi -e "s|libmod_vhost_dbi|mod_vhost_dbi|g" src/Makefile*

# lib64 fixes
perl -pi -e "s|/lib\b|/%{_lib}|g" *

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

%configure2_5x

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_libdir}/apache-extramodules

install -m0755 src/.libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
 %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
 if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
 fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc TODO
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}


