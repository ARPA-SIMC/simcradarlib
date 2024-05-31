%global srcname simcradarlib
%global releaseno 1
# Note: define _srcarchivename in Travis build only.
%{!?srcarchivename: %global srcarchivename %{srcname}-%{version}-%{releaseno}}


Name:           python-simcradarlib
Version:        0.1
Release:        1%{?dist}
Summary:        Libreria Python per applicazioni radar di Arpae-SIMC
License:        GPLv3
URL:            https://github.com/ARPA-SIMC/simcradarlib
Source0:        https://github.com/arpa-simc/%{name}/archive/v%{version}-%{release}.tar.gz#/%{srcarchivename}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-numpy
BuildRequires:  python3-pandas
BuildRequires:  python3-netcdf4
BuildRequires:  python3-pyproj
BuildRequires:  python3-h5py
BuildRequires:  python3-cftime
BuildRequires:  python3-matplotlib
BuildRequires:  python3-gdal

Requires:       python3-netcdf4
Requires:       python3-pyproj
Requires:       python3-h5py
Requires:       python3-cftime
Requires:       python3-matplotlib
Requires:       python3-gdal


%description
Libreria Python per applicazioni radar di Arpae-SIMC

%prep
%autosetup -n %{srcarchivename}

%build
%py3_build

%install
rm -rf $RPM_BUILD_ROOT
%py3_install


%check
%{__python3} setup.py test

%files
%license LICENSE
%doc README.md
# For noarch packages: sitelib
%{python3_sitelib}/%{srcname}/
%{python3_sitelib}/%{srcname}-%{version}-py%{python3_version}.egg-info/


%changelog
* Fri May 31 2024 Emanuele Di Giacomo <edigiacomo@arpae.it> - 0.1-1
- First package
