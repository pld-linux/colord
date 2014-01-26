#
# Conditional build:
%bcond_without	apidocs		# do not build and package API docs
%bcond_without	sane		# SANE support
%bcond_without	static_libs	# don't build static libraries
%bcond_without	vala		# don't build Vala API
#
Summary:	Color daemon - system daemon for managing color devices
Summary(pl.UTF-8):	Demon colord - usługa systemowa do zarządzania urządzeniami obsługującymi kolory
Name:		colord
Version:	1.0.6
Release:	1
License:	GPL v2+ and LGPL v2+
Group:		Daemons
Source0:	http://www.freedesktop.org/software/colord/releases/%{name}-%{version}.tar.xz
# Source0-md5:	9bd8a1f117742c31d195a09092ca3066
Patch0:		%{name}-completions.patch
URL:		http://www.freedesktop.org/software/colord/
BuildRequires:	autoconf >= 2.63
BuildRequires:	automake >= 1:1.9
BuildRequires:	dbus-devel
BuildRequires:	docbook-utils
BuildRequires:	gettext-devel >= 0.17
BuildRequires:	glib2-devel >= 1:2.36
BuildRequires:	gobject-introspection-devel >= 0.9.8
BuildRequires:	gtk-doc >= 1.9
BuildRequires:	intltool >= 0.40.0
BuildRequires:	lcms2-devel >= 2.2
BuildRequires:	libgusb-devel >= 0.1.1
BuildRequires:	libtool >= 2:2.0
BuildRequires:	libusb-devel >= 1.0.0
BuildRequires:	pkgconfig
BuildRequires:	polkit-devel >= 0.103
BuildRequires:	rpmbuild(macros) >= 1.644
%{?with_sane:BuildRequires:	sane-backends-devel}
BuildRequires:	sqlite3-devel
BuildRequires:	systemd-devel >= 44
BuildRequires:	udev-devel
BuildRequires:	udev-glib-devel
%{?with_vala:BuildRequires:	vala}
Requires(post,preun,postun):	systemd-units >= 44
Requires:	%{name}-libs = %{version}-%{release}
Requires:	polkit-libs >= 0.103
Requires:	systemd-units >= 44
Suggests:	shared-color-profiles
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
Requires:	glib2 >= 1:2.36
Requires:	lcms2 >= 2.2
# for libcolorhug only
Requires:	libgusb >= 0.1.1
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
Requires:	glib2-devel >= 1:2.36
Requires:	lcms2-devel >= 2.2
Requires:	libgusb-devel >= 0.1.1
Obsoletes:	colorhug-client-devel < 0.1.14

%description devel
Header files for colord library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki colord.

%package static
Summary:	Static colord library
Summary(pl.UTF-8):	Statyczna biblioteka colord
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}
Obsoletes:	colorhug-client-static < 0.1.14

%description static
Static colord library.

%description static -l pl.UTF-8
Statyczna biblioteka colord.

%package apidocs
Summary:	colord API documentation
Summary(pl.UTF-8):	Dokumentacja API colord
Group:		Documentation
Requires:	gtk-doc-common

%description apidocs
colord API documentation.

%description apidocs -l pl.UTF-8
Dokumentacja API colord.

%package -n vala-colord
Summary:	colord API for Vala language
Summary(pl.UTF-8):	API colord dla języka Vala
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description -n vala-colord
colord API for Vala language.

%description -n vala-colord -l pl.UTF-8
API colord dla języka Vala.

%package -n bash-completion-colord
Summary:	bash-completion for colormgr console commands
Summary(pl.UTF-8):	Bashowe uzupełnianie poleceń terminalowych colormgr
Group:		Applications/Shells
Requires:	bash-completion >= 2.0

%description -n bash-completion-colord
bash-completion for colormgr console commands.

%description -n bash-completion-colord -l pl.UTF-8
Bashowe uzupełnianie poleceń terminalowych colormgr.

%prep
%setup -q
%patch0 -p1

%build
%{__intltoolize}
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-silent-rules \
	--enable-bash-completion=%{_datadir}/bash-completion/completions \
	%{__enable_disable apidocs gtk-doc} \
	%{__enable sane} \
	%{__enable_disable static_libs static} \
	%{__enable_disable vala} \
	--with-html-dir=%{_gtkdocdir} \
	--with-systemdsystemunitdir=%{systemdunitdir}
# doc build is broken with -j
%{__make} -j1

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.la
# loadable modules
%{__rm} $RPM_BUILD_ROOT%{_libdir}/colord-{plugins,sensors}/*.{la,a}

# the same as it locale
%{__rm} -r $RPM_BUILD_ROOT%{_localedir}/it_IT
# empty version of bg locale
%{__rm} -r $RPM_BUILD_ROOT%{_localedir}/bg_BG

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%glib_compile_schemas

%postun
if [ "$1" = "0" ]; then
	%glib_compile_schemas
fi
%systemd_reload

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README TODO
%attr(755,root,root) %{_bindir}/cd-create-profile
%attr(755,root,root) %{_bindir}/cd-fix-profile
%attr(755,root,root) %{_bindir}/cd-iccdump
%attr(755,root,root) %{_bindir}/colormgr
%attr(755,root,root) %{_libexecdir}/colord
%{?with_sane:%attr(755,root,root) %{_libexecdir}/colord-sane}
%attr(755,root,root) %{_libexecdir}/colord-session
%dir %{_libdir}/colord-plugins
%attr(755,root,root) %{_libdir}/colord-plugins/libcd_plugin_camera.so
%{?with_sane:%attr(755,root,root) %{_libdir}/colord-plugins/libcd_plugin_sane.so}
%attr(755,root,root) %{_libdir}/colord-plugins/libcd_plugin_scanner.so
%dir %{_libdir}/colord-sensors
%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_argyll.so
%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_colorhug.so
%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_dtp94.so
%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_dummy.so
%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_huey.so
# disabled for now
#%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_munki.so
%attr(755,root,root) %{_libdir}/colord-sensors/libdtp94-private.so
%attr(755,root,root) %{_libdir}/colord-sensors/libhuey-private.so
%attr(755,root,root) %{_libdir}/colord-sensors/libmunki-private.so
%{_datadir}/colord
%{_datadir}/color/icc/colord
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorHelper.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager.Device.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager.Profile.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager.Sensor.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager.xml
%{_datadir}/dbus-1/services/org.freedesktop.ColorHelper.service
%{_datadir}/dbus-1/system-services/org.freedesktop.ColorManager.service
%{_datadir}/glib-2.0/schemas/org.freedesktop.ColorHelper.gschema.xml
%{_datadir}/polkit-1/actions/org.freedesktop.color.policy
%{_mandir}/man1/cd-create-profile.1*
%{_mandir}/man1/cd-fix-profile.1*
# man5?
%{_mandir}/man1/colord.conf.1*
%{_mandir}/man1/colormgr.1*
%{systemdunitdir}/colord.service
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/colord.conf
/etc/dbus-1/system.d/org.freedesktop.ColorManager.conf
/lib/udev/rules.d/69-cd-sensors.rules
/lib/udev/rules.d/95-cd-devices.rules
%dir /var/lib/colord

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcolord.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcolord.so.1
%attr(755,root,root) %{_libdir}/libcolordprivate.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcolordprivate.so.1
%attr(755,root,root) %{_libdir}/libcolorhug.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcolorhug.so.1
%{_libdir}/girepository-1.0/Colord-1.0.typelib
%{_libdir}/girepository-1.0/ColorHug-1.0.typelib

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcolord.so
%attr(755,root,root) %{_libdir}/libcolordprivate.so
%attr(755,root,root) %{_libdir}/libcolorhug.so
%{_includedir}/colord-1
%{_pkgconfigdir}/colord.pc
%{_pkgconfigdir}/colorhug.pc
%{_datadir}/gir-1.0/Colord-1.0.gir
%{_datadir}/gir-1.0/ColorHug-1.0.gir

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libcolord.a
%{_libdir}/libcolordprivate.a
%{_libdir}/libcolorhug.a
%endif

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%{_gtkdocdir}/colord
%endif

%if %{with vala}
%files -n vala-colord
%defattr(644,root,root,755)
%{_datadir}/vala/vapi/colord.vapi
%endif

%files -n bash-completion-colord
%defattr(644,root,root,755)
%{_datadir}/bash-completion/completions/colormgr
