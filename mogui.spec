%global srcname modules-gui
Name:           mogui
Version:        0.2.2
Release:        1%{?dist}
Summary:        Graphical User Interface for Environment Modules

# icon files are licensed under CC-BY-SA-3.0 terms
License:        GPL-2.0-or-later AND CC-BY-SA-3.0
URL:            https://github.com/cea-hpc/mogui
Source:         %{pypi_source}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
Requires:       environment-modules

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

install -d %{buildroot}%{_metainfodir}
install -p -m 0644 share/%{name}.metainfo.xml %{buildroot}%{_metainfodir}/

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
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{name}.metainfo.xml

%files
%license COPYING.GPLv2 COPYING-ICONS.CCBYSA3
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
%{_metainfodir}/%{name}.metainfo.xml

%changelog
* Sun Mar 31 2024 Xavier Delaruelle <xavier.delaruelle@cea.fr> - 0.2.2-1
- Update to 0.2.2
- Test desktop file
- Add AppData file and test it
- Remove environment-modules-gui provides
- Clarify license used for icon files (CC-BY-SA-3.0)

* Fri Mar 29 2024 Xavier Delaruelle <xavier.delaruelle@cea.fr> - 0.2.1-2
- Fix python-leftover-require issue

* Thu Mar 28 2024 Xavier Delaruelle <xavier.delaruelle@cea.fr> - 0.2.1-1
- Update to 0.2.1
- Clarify package summary
- Add ChangeLog file to documentation
- Add mogui desktop file
- Remove "mogui" bin (as "mogui" shell function is defined in environment
  and desktop file relies on "mogui-cmd")
- Use "global" directive instead of "define"

* Wed Mar 27 2024 Xavier Delaruelle <xavier.delaruelle@cea.fr> - 0.2-1
- Initial package
