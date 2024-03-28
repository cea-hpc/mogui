%global srcname modules-gui
Name:           mogui
Version:        0.2
Release:        1%{?dist}
Summary:        Graphical User Interface for Environment Modules

License:        GPL-2.0-or-later
URL:            https://github.com/cea-hpc/mogui
Source:         %{pypi_source}

BuildArch:      noarch
BuildRequires:  python3-devel
Requires:       python3
Requires:       python3-qt5
Requires:       environment-modules
Provides:       environment-modules-gui = %{version}

%description
MoGui is a Graphical User Interface (GUI) for Environment Modules. It helps
users selecting modules to load and save module collections.

%prep
%autosetup -p1 -n %{srcname}-%{version}

%generate_buildrequires
%pyproject_buildrequires -t

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{name}

install -d %{buildroot}%{_datadir}/pixmaps
install -p -m 0644 mogui/icons/mogui-light/symbolic/apps/environment-modules.svg %{buildroot}%{_datadir}/pixmaps/%{name}.svg

install -d %{buildroot}%{_datadir}/applications
install -p -m 0644 share/%{name}.desktop %{buildroot}%{_datadir}/applications/

install -d %{buildroot}%{_sysconfdir}/profile.d
install -d %{buildroot}%{_datadir}/fish/vendor_conf.d
install -p -m 0644 share/setup-env.sh %{buildroot}%{_sysconfdir}/profile.d/%{name}.sh
install -p -m 0644 share/setup-env.csh %{buildroot}%{_sysconfdir}/profile.d/%{name}.csh
install -p -m 0644 share/setup-env.fish %{buildroot}%{_datadir}/fish/vendor_conf.d/%{name}.fish

# "mogui" bin is not needed, as mogui shell function is defined at shell session start
# and desktop file relies on the "mogui-cmd" bin
rm %{buildroot}%{_bindir}/%{name}

%check
%pyproject_check_import

%files
%license COPYING.GPLv2
%doc ChangeLog README.md TODO.md
%{python3_sitelib}/%{name}/
%{python3_sitelib}/modules_gui-%{version}.dist-info/
%{_bindir}/%{name}-cmd
%{_bindir}/%{name}-setup-env
%{_sysconfdir}/profile.d/%{name}.csh
%{_sysconfdir}/profile.d/%{name}.sh
%{_datadir}/fish/vendor_conf.d/%{name}.fish
%{_datadir}/applications/%{name}.desktop
%{_datadir}/pixmaps/%{name}.svg

%changelog
* Wed Mar 27 2024 Xavier Delaruelle <xavier.delaruelle@cea.fr> - 0.2-1
- Initial package
