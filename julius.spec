%define packagePatch 1
%global debug_package %{nil}

Name:    julius 
Version: 1.8.0
Release: %{packagePatch}%{?dist}
Summary: An open source re-implementation of Caesar III 

Group:   Games
License: AGPLv3
URL:     https://github.com/bvschaik/julius 
Source:  https://github.com/bvschaik/julius/releases/download/v%{version}/julius-%{version}-source.tar.gz 
Source1: https://github.com/dudekaa/julius-spec/archive/refs/tags/v%{version}-%{packagePatch}.zip

BuildRequires: gcc
BuildRequires: cmake
BuildRequires: SDL2-devel
BuildRequires: SDL2_mixer-devel
BuildRequires: libpng-devel
BuildRequires: desktop-file-utils
Requires: SDL2
Requires: SDL2_mixer
Requires: libpng 

%description
Julius is a fully working open-source version of Caesar 3, with the same logic as the original, but with some UI enhancements, that can be played on multiple platforms.

Julius will not run without the original Caesar 3 files. You can buy a digital copy from GOG or Steam, or you can use an original CD-ROM version.

The goal of the project is to have exactly the same game logic as Caesar 3, with the same look and feel. This means that the saved games are 100% compatible with Caesar 3, and any gameplay bugs present in the original Caesar 3 game will also be present in Julius.

Enhancements for Julius include:

  * Support for widescreen resolutions
  * Windowed mode support for 32-bit desktops
  * A lot of small in-game quality of life improvements
  * Support for the high-quality MP3 files once provided on the Sierra website


%prep
%setup
%setup -T -D -a 1


%build
#configure
mkdir build && cd build
%cmake -DIS_RELEASE_VERSION=1 ..
%cmake_build
%ctest


%install
install -pDm0755 %_builddir/%{name}-%{version}/build/redhat-linux-build/%{name} %{buildroot}%{_bindir}/%{name}

# menu item
install -pDm0644 %_builddir/%{name}-%{version}/%{name}-spec-%{version}-%{packagePatch}/%{name}.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop
desktop-file-validate $RPM_BUILD_ROOT%{_datadir}/applications/%{name}.desktop


%files
/usr/bin/%{name}
%{_datadir}/applications/%{name}.desktop


%changelog
* Wed Sep 03 2025 Arnošt Dudek <arnost@arnostdudek.cz> - 1.8.0-1
- Initial build
