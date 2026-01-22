%global srcname simcradarlib
%global releaseno 2
# Note: define _srcarchivename in Travis build only.
%{!?srcarchivename: %global srcarchivename %{srcname}-%{version}-%{releaseno}}


Name:           python-simcradarlib
Version:        0.9
Release:        %{releaseno}%{?dist}
Summary:        Libreria Python per applicazioni radar di Arpae-SIMC
License:        GPLv3
URL:            https://github.com/ARPA-SIMC/simcradarlib
Source0:        https://github.com/arpa-simc/%{srcname}/archive/v%{version}-%{releaseno}.tar.gz#/%{srcarchivename}.tar.gz

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
BuildRequires:  python3-yaml

%description
Libreria Python per applicazioni radar di Arpae-SIMC

%package -n python3-simcradarlib
Summary:        Libreria Python per applicazioni radar di Arpae-SIMC
Requires:       python3-netcdf4
Requires:       python3-pyproj
Requires:       python3-h5py
Requires:       python3-cftime
Requires:       python3-matplotlib
Requires:       python3-gdal
Requires:       python3-yaml

%description -n python3-simcradarlib
Libreria Python per applicazioni radar di Arpae-SIMC

%prep
%autosetup -n %{srcarchivename}

%build
%py3_build

%install
%py3_install

%check
%{__python3} -m unittest tests/runtests.py

%files -n python3-simcradarlib
%license LICENSE
%doc README.md
# For noarch packages: sitelib
%{python3_sitelib}/%{srcname}/*
%{python3_sitelib}/%{srcname}-%{version}-py%{python3_version}.egg-info/*


%changelog
* Thu Jan 22 2026 Daniele Branchini  <dbranchini@arpae.it> - 0.9-2
- Fixed version in sources

* Thu Jan 22 2026 Daniele Branchini  <dbranchini@arpae.it> - 0.9-1
- Added `odim_operations.py`

* Thu Sep  4 2025 Daniele Branchini <dbranchini@arpae.it> - 0.8-2
- Removed deprecated setup.py test from spec file

* Fri Jun 20 2025 Daniele Branchini <dbranchini@arpae.it> - 0.8-1
- resolved: colorbar->ScalarMappable->setarray

* Fri Jun 20 2025 Emanuele Di Giacomo <edigiacomo@arpae.it> - 0.7-1
- Add YAML file to package

* Wed Sep 25 2024 Daniele Branchini <dbranchini@arpae.it> - 0.6-1
- Introdotta gestione lettura grid per netcdf antecedenti al 2013-04-09
- Aggiunta lettura var_missing e undetectable per netcdf

* Tue Sep 24 2024 Daniele Branchini <dbranchini@arpae.it> - 0.5-1
- Aggiornata documentazione

* Fri Jun 21 2024 Emanuele Di Giacomo <edigiacomo@arpae.it> - 0.3-1
- Risolto problema memoryerror sul dtype
- Corretta documentazione su metodo scrittura netcdf

* Tue Jun  4 2024 Emanuele Di Giacomo <edigiacomo@arpae.it> - 0.2-1
- Fixed subpackages installation

* Fri May 31 2024 Emanuele Di Giacomo <edigiacomo@arpae.it> - 0.1-1
- First package
