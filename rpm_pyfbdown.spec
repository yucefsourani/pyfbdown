Name:           pyfbdown
Version:        1.0
Release:        2%{?dist}
Summary:        Facebook Videos Downloader
License:        GPLv3     
URL:            https://github.com/yucefsourani/pyfbdown
Source0:        https://github.com/yucefsourani/pyfbdown/archive/main.zip
BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires: gettext
Requires:       python3-gobject
Requires:       gtk3
Requires:       gettext


%description
Facebook Videos Downloader.


%prep
%autosetup -n pyfbdown-main

%build


%install
rm -rf $RPM_BUILD_ROOT
%make_install

%find_lang %{name}

%files -f %{name}.lang
%doc README.md LICENSE
%{python3_sitelib}/*
%{_bindir}/pyfbdown.py
%{_datadir}/applications/*
%{_datadir}/pyfbdown-data/*
%{_datadir}/pyfbdown-data/images/*
%{_datadir}/pixmaps/*
%{_datadir}/icons/hicolor/*/apps/*


%changelog
* Mon Dec 7 2020 yucuf sourani <youssef.m.sourani@gmail.com> 1.0-2
- Release 2

* Mon Dec 7 2020 yucuf sourani <youssef.m.sourani@gmail.com> 1.0-1
- Initial For Fedora 

