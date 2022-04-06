#
# Conditional build:
%bcond_without	apidocs		# gtk-doc based API documentation
%bcond_without	sane		# SANE support
%bcond_without	vala		# Vala API
%bcond_without	systemd		# systemd

Summary:	Color daemon - system daemon for managing color devices
Summary(pl.UTF-8):	Demon colord - usługa systemowa do zarządzania urządzeniami obsługującymi kolory
Name:		colord
Version:	1.4.5
Release:	4
License:	GPL v2+ and LGPL v2+
Group:		Daemons
Source0:	https://www.freedesktop.org/software/colord/releases/%{name}-%{version}.tar.xz
# Source0-md5:	adc4501b54fb8667ee99f64cff87e12d
URL:		https://www.freedesktop.org/software/colord/
# for colprof,spotread programs detection
BuildRequires:	argyllcms
BuildRequires:	bash-completion-devel >= 2.0
BuildRequires:	dbus-devel
BuildRequires:	docbook-style-xsl-ns
BuildRequires:	gcc >= 5:3.2
BuildRequires:	gettext-tools >= 0.17
BuildRequires:	glib2-devel >= 1:2.46.0
BuildRequires:	gobject-introspection-devel >= 0.9.8
BuildRequires:	gtk-doc >= 1.9
BuildRequires:	lcms2-devel >= 2.6
BuildRequires:	libgusb-devel >= 0.2.7
BuildRequires:	libxslt-progs
BuildRequires:	meson >= 0.52.0
BuildRequires:	ninja
BuildRequires:	pkgconfig
BuildRequires:	polkit-devel >= 0.103
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 1.736
%{?with_sane:BuildRequires:	sane-backends-devel}
BuildRequires:	sqlite3-devel >= 3
%{?with_systemd:BuildRequires:	systemd-devel >= 44}
BuildRequires:	tar >= 1:1.22
BuildRequires:	udev-devel
BuildRequires:	udev-glib-devel
%{?with_vala:BuildRequires:	vala}
BuildRequires:	xz
Requires(post,preun,postun):	systemd-units >= 44
Requires:	%{name}-libs = %{version}-%{release}
Requires:	polkit >= 0.103
Requires:	systemd-units >= 44
# /usr/bin/spotread called by argyll sensor driver
Suggests:	argyllcms
Suggests:	shared-color-profiles
Provides:	group(colord)
Provides:	user(colord)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
colord is a low level system activated daemon that maps color devices
to color profiles in the system context.

%description -l pl.UTF-8
colord to niskopoziomowa usługa systemowa odwzorowująca urządzenia
obsługujące kolory na profile kolorów w kontekście systemu.

%package libs
Summary:	colord library
Summary(pl.UTF-8):	Biblioteka colord
Group:		Libraries
Requires:	glib2 >= 1:2.46.0
Requires:	lcms2 >= 2.6
# for libcolorhug only
Requires:	libgusb >= 0.2.7
Suggests:	%{name} = %{version}-%{release}
Obsoletes:	colorhug-client-libs < 0.1.14
Conflicts:	colord < 0.1.12-4

%description libs
colord library.

%description libs -l pl.UTF-8
Biblioteka colord.

%package devel
Summary:	Header files for colord library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki colord
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	dbus-devel
Requires:	glib2-devel >= 1:2.46.0
Requires:	lcms2-devel >= 2.6
Requires:	libgusb-devel >= 0.2.7
Obsoletes:	colord-static < 1.4.0
Obsoletes:	colorhug-client-devel < 0.1.14
Obsoletes:	colorhug-client-static < 0.1.14

%description devel
Header files for colord library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki colord.

%package apidocs
Summary:	colord API documentation
Summary(pl.UTF-8):	Dokumentacja API colord
Group:		Documentation
Requires:	gtk-doc-common
BuildArch:	noarch

%description apidocs
colord API documentation.

%description apidocs -l pl.UTF-8
Dokumentacja API colord.

%package -n vala-colord
Summary:	colord API for Vala language
Summary(pl.UTF-8):	API colord dla języka Vala
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}
BuildArch:	noarch

%description -n vala-colord
colord API for Vala language.

%description -n vala-colord -l pl.UTF-8
API colord dla języka Vala.

%package -n bash-completion-colord
Summary:	bash-completion for colormgr console commands
Summary(pl.UTF-8):	Bashowe uzupełnianie poleceń terminalowych colormgr
Group:		Applications/Shells
Requires:	bash-completion >= 2.0
BuildArch:	noarch

%description -n bash-completion-colord
bash-completion for colormgr console commands.

%description -n bash-completion-colord -l pl.UTF-8
Bashowe uzupełnianie poleceń terminalowych colormgr.

%prep
%setup -q

%build
%meson build \
	%{!?with_apidocs:-Ddocs=false} \
	-Dlibcolordcompat=true \
	%{?with_sane:-Dsane=true} \
	%{!?with_systemd:-Dsystemd=false} \
	%{?with_vala:-Dvapi=true} \
	-Ddaemon_user=colord

%ninja_build -C build

%install
rm -rf $RPM_BUILD_ROOT

%ninja_install -C build

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 331 colord
%useradd -u 331 -d /var/lib/colord -g colord -c "colord daemon user" colord

%post
%glib_compile_schemas

%postun
%systemd_reload
if [ "$1" = "0" ]; then
	%glib_compile_schemas
	%userremove colord
	%groupremove colord
fi

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc AUTHORS NEWS README.md
%attr(755,root,root) %{_bindir}/cd-create-profile
%attr(755,root,root) %{_bindir}/cd-fix-profile
%attr(755,root,root) %{_bindir}/cd-iccdump
%attr(755,root,root) %{_bindir}/cd-it8
%attr(755,root,root) %{_bindir}/colormgr
%attr(755,root,root) %{_libexecdir}/colord
%{?with_sane:%attr(755,root,root) %{_libexecdir}/colord-sane}
%attr(755,root,root) %{_libexecdir}/colord-session
%dir %{_libdir}/colord-plugins
%attr(755,root,root) %{_libdir}/colord-plugins/libcolord_sensor_camera.so
%{?with_sane:%attr(755,root,root) %{_libdir}/colord-plugins/libcolord_sensor_sane.so}
%attr(755,root,root) %{_libdir}/colord-plugins/libcolord_sensor_scanner.so
%dir %{_libdir}/colord-sensors
%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_argyll.so
%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_colorhug.so
%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_dtp94.so
%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_dummy.so
%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_huey.so
# disabled for now
#%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_munki.so
%{_datadir}/colord
%{_datadir}/color/icc/colord
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorHelper.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager.Device.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager.Profile.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager.Sensor.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager.xml
%{_datadir}/dbus-1/services/org.freedesktop.ColorHelper.service
%{_datadir}/dbus-1/system-services/org.freedesktop.ColorManager.service
%{_datadir}/dbus-1/system.d/org.freedesktop.ColorManager.conf
%{_datadir}/glib-2.0/schemas/org.freedesktop.ColorHelper.gschema.xml
%{_datadir}/polkit-1/actions/org.freedesktop.color.policy
%{_mandir}/man1/cd-create-profile.1*
%{_mandir}/man1/cd-fix-profile.1*
%{_mandir}/man1/cd-it8.1*
%{_mandir}/man1/colormgr.1*
%if %{with systemd}
%{systemdunitdir}/colord.service
%{systemduserunitdir}/colord-session.service
%{systemdtmpfilesdir}/colord.conf
%endif
/lib/udev/rules.d/69-cd-sensors.rules
/lib/udev/rules.d/95-cd-devices.rules
%attr(755,colord,colord) %dir /var/lib/colord
%attr(755,colord,colord) %dir /var/lib/colord/icc

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcolord.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcolord.so.2
%attr(755,root,root) %{_libdir}/libcolordcompat.so
%attr(755,root,root) %{_libdir}/libcolordprivate.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcolordprivate.so.2
%attr(755,root,root) %{_libdir}/libcolorhug.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcolorhug.so.2
%{_libdir}/girepository-1.0/Colord-1.0.typelib
%{_libdir}/girepository-1.0/Colorhug-1.0.typelib

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcolord.so
%attr(755,root,root) %{_libdir}/libcolordprivate.so
%attr(755,root,root) %{_libdir}/libcolorhug.so
%{_includedir}/colord-1
%{_pkgconfigdir}/colord.pc
%{_pkgconfigdir}/colorhug.pc
%{_datadir}/gir-1.0/Colord-1.0.gir
%{_datadir}/gir-1.0/Colorhug-1.0.gir

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%{_gtkdocdir}/colord
%endif

%if %{with vala}
%files -n vala-colord
%defattr(644,root,root,755)
%{_datadir}/vala/vapi/colord.deps
%{_datadir}/vala/vapi/colord.vapi
%endif

%files -n bash-completion-colord
%defattr(644,root,root,755)
%{bash_compdir}/colormgr
