Name:    julius
Version: 1.8.0
Release: 5%{?dist}
Summary: An open source re-implementation of Caesar III 

Group:   Games
License: AGPLv3
URL:     https://github.com/bvschaik/julius
# e.g. https://github.com/bvschaik/julius/archive/refs/tags/v1.8.0.tar.gz
Source:  %{url}/archive/refs/tags/v%{version}.tar.gz
Source1: %{name}.desktop

Patch1: 01-cmake-min-version.patch

BuildRequires: gcc
BuildRequires: cmake
BuildRequires: pkgconfig(sdl2)
BuildRequires: pkgconfig(SDL2_mixer)
BuildRequires: pkgconfig(libpng)
BuildRequires: desktop-file-utils

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
%autosetup -n %{name}-%{version}


%build
# CMake build flags:
# -DCMAKE_BUILD_TYPE=RelWithDebInfo: Build with optimizations enabled and debug symbols included - Fedora recommendation
# -DIS_RELEASE_VERSION=1: Mark this as an official release version (not a development build) - we build directly from tags
# -DSYSTEM_LIBS=ON: Use system-provided libraries (SDL2, SDL2_mixer, libpng) instead of bundled versions
%cmake \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DIS_RELEASE_VERSION=1 \
    -DSYSTEM_LIBS=ON
%cmake_build


%check
%ctest


%install
install -pDm0755 %{_vpath_builddir}/%{name} %{buildroot}%{_bindir}/%{name}

# menu item
install -pDm0644 %{SOURCE1} %{buildroot}%{_datadir}/applications/%{name}.desktop
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop


%files
/usr/bin/%{name}
%{_datadir}/applications/%{name}.desktop


%changelog
* Sat May 02 2026 Jenkins <jenkins@nostovo> - 1.8.0-5
- Automated update to upstream version

* Fri Feb 20 2026 Jenkins <jenkins@nostovo> - 1.8.0-4
- Minor spec file updates

* Fri Feb 20 2026 Jenkins <jenkins@nostovo> - 1.8.0-3
- Minor spec file updates

* Thu Feb 19 2026 Arnošt Dudek <arnost@arnostdudek.cz> - 1.8.0-2
- rework dependencies
- enable debug packages

* Wed Sep 03 2025 Arnošt Dudek <arnost@arnostdudek.cz> - 1.8.0-1
- Initial build
