%define debug_package %{nil}

%define _git_url https://github.com/percona/mysqld_exporter
%define _git_slug src/github.com/percona/mysqld_exporter

Name:    mysqld_exporter
Version: 0.10.0+percona.4
Release: 2.vortex%{?dist}
Summary: Prometheus exporter for MySQL
License: MIT
Vendor:  Vortex RPM
URL:     https://github.com/percona/mysqld_exporter

Source1: %{name}.service
Source2: %{name}.default
Source3: %{name}.init

%{?el6:Requires(post): chkconfig}
%{?el6:Requires(preun): chkconfig, initscripts}
Requires(pre): shadow-utils
%{?el6:Requires: daemonize}
%{?el7:%{?systemd_requires}}
BuildRequires: golang, git

%description
Prometheus exporter for MySQL.

%prep
mkdir _build
export GOPATH=$(pwd)/_build
git clone %{_git_url} $GOPATH/%{_git_slug}
cd $GOPATH/%{_git_slug}
git checkout v%{version}

%build
export GOPATH=$(pwd)/_build
cd $GOPATH/%{_git_slug}
make format
make build
strip %{name}

%install
export GOPATH=$(pwd)/_build
mkdir -vp %{buildroot}/var/lib/prometheus
%{?el6:mkdir -vp %{buildroot}/usr/sbin}
%{?el7:mkdir -vp %{buildroot}/usr/bin}
%{?el6:mkdir -vp %{buildroot}%{_initddir}}
%{?el7:mkdir -vp %{buildroot}/usr/lib/systemd/system}
mkdir -vp %{buildroot}/etc/default
%{?el6:install -m 755 $GOPATH/%{_git_slug}/%{name} %{buildroot}/usr/sbin/%{name}}
%{?el7:install -m 755 $GOPATH/%{_git_slug}/%{name} %{buildroot}/usr/bin/%{name}}
%{?el6:install -m 755 %{SOURCE3} %{buildroot}%{_initddir}/%{name}}
%{?el7:install -m 644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/%{name}.service}
install -m 644 %{SOURCE2} %{buildroot}/etc/default/%{name}

%pre
getent group prometheus >/dev/null || groupadd -r prometheus
getent passwd prometheus >/dev/null || \
  useradd -r -g prometheus -d /var/lib/prometheus -s /sbin/nologin \
          -c "Prometheus services" prometheus
exit 0

%post
%{?el6:/sbin/chkconfig --add %{name}}
%{?el7:%systemd_post %{name}.service}

%preun
%{?el6:
if [ $1 -eq 0 ] ; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi
}
%{?el7:%systemd_preun %{name}.service}

%postun
%{?el6:
if [ "$1" -ge "1" ] ; then
    /sbin/service %{name} restart >/dev/null 2>&1
fi
}
%{?el7:%systemd_postun %{name}.service}

%files
%defattr(-,root,root,-)
%{?el6:/usr/sbin/%{name}}
%{?el7:/usr/bin/%{name}}
%{?el6:%{_initddir}/%{name}}
%{?el7:/usr/lib/systemd/system/%{name}.service}
%config(noreplace) /etc/default/%{name}
%attr(755, prometheus, prometheus)/var/lib/prometheus
%doc _build/%{_git_slug}/LICENSE _build/%{_git_slug}/README.md

%changelog
* Thu Jan 18 2018 Ilya Otyutskiy <ilya.otyutskiy@icloud.com> - 0.10.0+percona.4-2.vortex
- Update

* Thu Jan 18 2018 Ilya Otyutskiy <ilya.otyutskiy@icloud.com> - 0.10.0+percona.4-1.vortex
- Initial packaging
