#
# Conditional build:
%bcond_without	apidocs		# do not build and package API docs
%bcond_without	static_libs	# don't build static libraries
%bcond_without	vala		# don't build Vala API
#
Summary:	Color daemon - system daemon for managing color devices
Summary(pl.UTF-8):	Demon colord - usługa systemowa do zarządzania urządzeniami obsługującymi kolory
Name:		colord
Version:	0.1.16
Release:	2
License:	GPL v2+ and LGPL v2+
Group:		Daemons
Source0:	http://www.freedesktop.org/software/colord/releases/%{name}-%{version}.tar.xz
# Source0-md5:	cb73ffdcebe4c06852c48355e83a4bc4
URL:		http://www.freedesktop.org/software/colord/
BuildRequires:	autoconf >= 2.63
BuildRequires:	automake >= 1:1.9
BuildRequires:	dbus-devel
BuildRequires:	gettext-devel >= 0.17
BuildRequires:	glib2-devel >= 1:2.28.0
BuildRequires:	gobject-introspection-devel >= 0.9.8
BuildRequires:	gtk-doc >= 1.9
BuildRequires:	intltool >= 0.40.0
BuildRequires:	lcms2-devel >= 2.2
BuildRequires:	libgusb-devel >= 0.1.1
BuildRequires:	libtool
BuildRequires:	libusb-devel >= 1.0.0
BuildRequires:	pkgconfig
BuildRequires:	polkit-devel >= 0.103
BuildRequires:	rpmbuild(macros) >= 1.644
BuildRequires:	sane-backends-devel >= 1.0.20-3
BuildRequires:	sqlite3-devel
BuildRequires:	udev-glib-devel
%{?with_vala:BuildRequires:	vala}
Requires:	%{name}-libs = %{version}-%{release}
Requires:	polkit-libs >= 0.103
Requires:	systemd-units >= 38
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
Requires:	glib2 >= 1:2.28.0
Suggests:	%{name} = %{version}-%{release}
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
Requires:	glib2-devel >= 1:2.28.0

%description devel
Header files for colord library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki colord.

%package static
Summary:	Static colord library
Summary(pl.UTF-8):	Statyczna biblioteka colord
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

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

%prep
%setup -q

%build
%{__intltoolize}
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-silent-rules \
	%{__enable_disable apidocs gtk-doc} \
	%{__enable_disable static_libs static} \
	--with-html-dir=%{_gtkdocdir} \
	--with-systemdsystemunitdir=%{systemdunitdir}
# doc build is broken with -j
%{__make} -j1

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.la
%{__rm} $RPM_BUILD_ROOT%{_libdir}/colord-sensors/*.a
%{__rm} $RPM_BUILD_ROOT%{_libdir}/colord-sensors/*.la

# the same as it locale
%{__rm} -r $RPM_BUILD_ROOT%{_datadir}/locale/it_IT

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post colord.service

%preun
%systemd_preun colord.service

%postun
%systemd_reload

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README TODO
%attr(755,root,root) %{_bindir}/cd-create-profile
%attr(755,root,root) %{_bindir}/cd-fix-profile
%attr(755,root,root) %{_bindir}/colormgr
%attr(755,root,root) %{_libexecdir}/colord
%dir %{_libdir}/colord-sensors
%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_colorhug.so
%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_dummy.so
%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_huey.so
# disabled for now
#%attr(755,root,root) %{_libdir}/colord-sensors/libcolord_sensor_munki.so
%dir %{_datadir}/color/icc/colord
%{_datadir}/color/icc/colord/*.icc
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager.Device.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager.Profile.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager.Sensor.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager.xml
%{_datadir}/dbus-1/system-services/org.freedesktop.ColorManager.service
%{_datadir}/polkit-1/actions/org.freedesktop.color.policy
%{_mandir}/man1/cd-create-profile.1*
%{_mandir}/man1/cd-fix-profile.1*
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
%{_libdir}/girepository-1.0/Colord-1.0.typelib

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcolord.so
%{_includedir}/colord-1
%{_pkgconfigdir}/colord.pc
%{_datadir}/gir-1.0/Colord-1.0.gir

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libcolord.a
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
