Summary:	User Interface Designer for GTK+ and GNOME
Name:		glade3
Version:	3.6.7
Release:	2.1%{?dist}
License:	GPLv2+
Group:		Development/Tools
URL:		http://glade.gnome.org/
Source0:	http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/%{name}-%{version}.tar.bz2

Patch0:		%{name}-3.6.5-pkgconfig.patch

BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

Requires:	hicolor-icon-theme
Requires:	%{name}-libgladeui = %{version}-%{release}
Requires(post):	scrollkeeper
Requires(postun): scrollkeeper
BuildRequires:	desktop-file-utils
BuildRequires:	gettext
BuildRequires:	gnome-doc-utils
BuildRequires:	gtk2-devel >= 2.14.0
BuildRequires:	intltool
BuildRequires:	libgnomeui-devel
BuildRequires:	libtool
BuildRequires:	pygtk2-devel
BuildRequires:	scrollkeeper

%description
Glade is a RAD tool to enable quick and easy development of user interfaces for
the GTK+ toolkit and the GNOME desktop environment.

The user interfaces designed in Glade are saved as XML, which can be used in
numerous programming languages including C, C++, Java, Perl, Python, C#, Pike,
Ruby, Haskell, Objective Caml and Scheme. Adding support for other languages
is easy too.

%package libgladeui
Summary:	Widget library for Glade UI designer
# The libgladegtk.so modules is under (GPLv2+ and LGPLv2+), the icons are
# under under LGPLv2, and the rest is GPLv2+.
# For a breakdown of the licensing, see COPYING.
License:	GPLv2+ and (GPLv2+ and LGPLv2+) and LGPLv2
Group:		Development/Libraries

Requires:	devhelp

%description libgladeui
Libgladeui consists of the widgets that compose the Glade GUI as a separate
library to ease the integration of Glade into other applications.

%package libgladeui-devel
Summary:	Development files for %{name}-libgladeui
# The glade-parser.h header is under LGPLv2+, and the rest is GPLv2+.
License:	GPLv2+ and LGPLv2+
Group:		Development/Libraries

Requires:	gtk-doc
Requires:	%{name}-libgladeui = %{version}-%{release}

%description libgladeui-devel
This package contains development files for %{name}-libgladeui.

%prep
%setup -q
%patch0 -p1

# Suppress rpmlint warning.
chmod 644 ./plugins/gtk+/glade-attributes.c
chmod 644 ./plugins/gtk+/glade-attributes.h

%build
%configure --disable-static --enable-gnome --enable-gtk-doc --enable-python \
  --enable-scrollkeeper

# Remove rpaths.
rm -f ./libtool
cp %{_bindir}/libtool .

# Omit unused direct shared library dependencies.
sed --in-place --expression 's! -shared ! -Wl,--as-needed\0!g' libtool

make %{?_smp_mflags}

# Strip unneeded translations from .mo files:
# http://bugzilla.gnome.org/474987
pushd ./po
  grep --invert-match \
    ".*[.]desktop[.]in[.]in$\|.*[.]server[.]in[.]in$" \
    POTFILES.in > POTFILES.keep
  mv POTFILES.keep POTFILES.in
  intltool-update --pot
  for p in *.po; do
    msgmerge $p %{name}.pot > $p.out
    msgfmt -o `basename $p .po`.gmo $p.out
  done
popd

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d

make install INSTALL="%{__install} -p" DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -type f -name "*.la" -delete
find $RPM_BUILD_ROOT -type f -name "*.a" -delete

%find_lang %{name}

desktop-file-install %{?_remove_encoding} --vendor fedora --delete-original \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
  $RPM_BUILD_ROOT%{_datadir}/applications/glade-3.desktop

%clean
rm -rf $RPM_BUILD_ROOT

%post
scrollkeeper-update -q -o %{_datadir}/omf/glade || :

if [ -x %{_bindir}/update-desktop-database ]; then
  update-desktop-database &> /dev/null || :
fi

touch --no-create %{_datadir}/icons/hicolor || :
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%postun
scrollkeeper-update -q || :

if [ -x %{_bindir}/update-desktop-database ]; then
  update-desktop-database &> /dev/null || :
fi

touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%post libgladeui -p /sbin/ldconfig

%postun libgladeui -p /sbin/ldconfig

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS
%doc ChangeLog
%doc COPYING.GPL
%doc NEWS
%doc README
%doc TODO
%{_bindir}/glade-3
%{_datadir}/applications/fedora-glade-3.desktop
%{_datadir}/icons/hicolor/16x16/apps/glade-3.png
%{_datadir}/icons/hicolor/22x22/apps/glade-3.png
%{_datadir}/icons/hicolor/24x24/apps/glade-3.png
%{_datadir}/icons/hicolor/32x32/apps/glade-3.png
%{_datadir}/icons/hicolor/48x48/apps/glade-3.png
%{_datadir}/icons/hicolor/scalable/apps/glade-3.svg

%dir %{_datadir}/gnome/help/glade
%{_datadir}/gnome/help/glade/*

%dir %{_datadir}/omf/glade
%{_datadir}/omf/glade/*

%files libgladeui
%defattr(-,root,root,-)
%doc COPYING
%doc COPYING.GPL
%doc COPYING.LGPL
%{_libdir}/libgladeui-1.so.*

%dir %{_datadir}/%{name}
%{_datadir}/%{name}/catalogs
%{_datadir}/%{name}/pixmaps

%dir %{_libdir}/%{name}
# Contains *.so files that are not symlinked to *.so.* files.
%{_libdir}/%{name}/modules

%files libgladeui-devel
%defattr(-,root,root,-)
%doc COPYING.GPL
%{_libdir}/libgladeui-1.so
%{_libdir}/pkgconfig/gladeui-1.0.pc

%dir %{_datadir}/gtk-doc/html/gladeui
%doc %{_datadir}/gtk-doc/html/gladeui/*

%dir %{_includedir}/libgladeui-1.0
%{_includedir}/libgladeui-1.0/gladeui

%changelog
* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 3.6.7-2.1
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Release Engineering <rel-eng@fedoraproject.org> - 3.6.7-2
- Autorebuild for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jun 30 2009 Matthias Clasen <mclasen@redhat.com> - 3.6.7-1
- Version bump to 3.6.7.
  * Fixed crashes when handling GtkTextView in GtkBuilder format.
  * Fixed loading and saving of GtkIconSources.
  * GNOME Goal: removed deprecated Gtk+ symbols. (GNOME Bugzilla #572756)
  * Fixed obscure crash when loading a project. (GNOME Bugzilla #585860)
  * Introspect lowest GTK+ project dependancy when loading files with missing 
    versioning information. (GNOME Bugzilla #586046)
  * Detect correct modifiers and buttons to spawn a context menu in a platform
    independant way. (GNOME Bugzilla #587128)
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.7.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.6.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.7.changes
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.6.changes
- Drop the menu patch, since glade-3 is the version we install
  by default now, and it didn't work right anyway

* Mon Jun 15 2009 Matthias Clasen <mclasen@redhat.com> - 3.6.5-1
- Version bump to 3.6.5.
  * GtkButton only accepts real stock items and GtkImage but not icons.
  * Removed buggy query dialog from GtkNotebook creation. (GNOME Bugzilla
    #578727)
  * Removed hard coded size request to palette. (GNOME Bugzilla #579624)
  * Atk proxy objects should always have unique names. (GNOME Bugzilla
    #579565)
  * Fixed output format for GtkLabel attributes. (GNOME Bugzilla #579793)
  * Widget names should be unique withing the project. (GNOME Bugzilla
    #580745)
  * Dialogs should not disappear on pressing ESC. (GNOME Bugzilla #582559)
  * Properly load sizes of fixed/layout children. (GNOME Bugzilla #584334)
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.5.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.4.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.3.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.5.changes
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.4.changes
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.3.changes

* Mon Apr 27 2009 Matthias Clasen <mclasen@redhat.com> - 3.6.2-2
- Don't drop schemas translations from po files

* Fri Apr 17 2009 Debarshi Ray <rishi@fedoraproject.org> - 3.6.2-1
- Version bump to 3.6.2.
  * Fixed missing properties/attributes when serializing a GtkWindow. (GNOME
    Bugzilla #578211)
  * Fixed loading state of GtkCellRenderer attributes (whether to use
    attribute or property directly). (GNOME Bugzilla #566928)
  * Translation updates: es, sr and sr@latin.
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.2.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.2.changes
- Fixed gladeui-1.0.pc.in by trimming 'Requires' list.

* Tue Apr 07 2009 Debarshi Ray <rishi@fedoraproject.org> - 3.6.1-1
- Version bump to 3.6.1.
  * Fixed crash during internal widget selection.
  * Fixed Libglade regression. Libglade needs specific ordering of properties,
    ATK props, signals and accelerators.
  * Disable loading and displaying of 'data' property on GtkTreeStore. Only
    GtkListStore understands the 'data' construct.
  * Properly initialize a GValue on the stack. (GNOME Bugzilla #577822)
  * Translation updates: ar and cs.
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.1.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.6/glade3-3.6.1.changes
- Added 'Requires: devhelp' to glade3-libgladeui.
- Removed 'Requires: gtk2-devel >= 2.14.0 libxml2-devel pkgconfig' from
  glade3-libgladeui-devel. Let rpm-4.6 autogenerate them.

* Tue Mar 17 2009 Debarshi Ray <rishi@fedoraproject.org> - 3.6.0-1
- Version bump to 3.6.0.
  * Support for both GtkBuilder and Libglade, and conversion from one format
    to the other.
  * Support for GtkAction.
  * New interface to allow plugins to define editor layouts on a class level
    basis, and new customized editors for GtkButton, GtkImage and GtkEntry.
  * New Python plugin for instrospecting and loading Python class properties
    and signals, and adding them to the palette automatically.
  * Support for filtering and searching the project using the inspector.
  * Support for inline editing of widgets in a dialog.
  * Cut and pasted widgets should retain original names. (GNOME Bugzilla
    #567809)
  * The "after" property for a signal handler should be saved to the project
    file. (GNOME Bugzilla #573453)
  * Fixed crash when choosing not to save a project with errors. (GNOME
    Bugzilla #574706)
  * Translation updates: el, fr, da, ml, gl, te, lt, pt, or, cs, it, th, en_GB,
    sv, ru, fi, de, tr, lv, ko, es, sv, hu, eu, vi and pt_BR.
- Updated License to reflect recent licensing changes according to Fedora
  licensing guidelines.
- Stripped redundant translations from .mo files. (GNOME Bugzilla #474987)

* Tue Feb 24 2009 Release Engineering <rel-eng@fedoraproject.org> - 3.5.7-2
- Autorebuild for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 18 2009 Matthias Clasen <mclasen@redhat.com> - 3.5.7-1
- Version bump to 3.5.7.
  * Allow Anjuta to handle clicks on widgets in the designer. (GNOME Bugzilla
    #542337)
  * Allow custom signal editors. (GNOME Bugzilla #540691)
  * Support running from gtk2-2.14 targetting gtk2-2.16.
  * Translation updates: de, es, fi, he, ko and pt_BR.
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.5/glade3-3.5.7.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.5/glade3-3.5.7.changes

* Sat Jan 31 2009 Rakesh Pandit <rakesh@fedoraproject.org> - 3.5.6-1
- Version bump to 3.5.6.
  * Handles new GdkPixbuf properties. (GNOME Bugzilla #567454)
  * Translation updates: es, nb and pt_BR.
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.5/glade3-3.5.6.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.5/glade3-3.5.6.changes
- Fixed unowned directories in libgladeui-devel. (Red Hat Bugzilla #483311)

* Wed Jan 07 2009 Debarshi Ray <rishi@fedoraproject.org> - 3.5.5-1
- Version bump to 3.5.5.
  * Improved model data editor with sequential editing mode and better key
    navigations.
  * Translation updates: es.
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.5/glade3-3.5.5.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.5/glade3-3.5.5.changes
- Removed 'Provides: glade'.
- Addressed warnings generated by rpmlint.

* Thu Dec 18 2008 Debarshi Ray <rishi@fedoraproject.org> - 3.5.4-1
- Version bump to 3.5.4.
  * Some files in plugins/gtk+ have been relicensed from GPLv2+ to LGPLv2+.
  * Support for GtkIconFactory, GtkAccelGroup, GtkSizeGroup, GtkListStore,
    GtkTreeStore, GtkTreeViewColumn, GtkTreeView, GtkIconView, GtkComboBox and
    GtkCellRenderer derivatives.
  * GtkBuilder support for GtkMenu hierarchies.
  * Added versioning support. One can chose the target version of a project
    starting from gtk2-2.8.
  * New GtkTreeView editor for combo-boxes and icon views.
  * Beefed up editor widget with icon and class header.
  * Better resizing in editors for property names, warnings and inputs.
  * Simplified accelerator editor.
  * New Pango attributes editor for GtkLabel.
  * Widgets and their properties in .glade files are now saved in the same
    order. (GNOME Bugzilla #422823)
  * Permit working with non-GtkWindow top-level widgets. (GNOME Bugzilla
    #532636)
  * Simplified and improved stock-id properties to allow use of custom icons
    from factories.
  * Translation updates: ar, bg, da, de, en_gb, es, et, fi, fr, gl, gu, he,
    hi, hu, it, ko, ml, mr, nl, oc, pl, pt, pt_BR, ru, sr.po, sr@latin, sv,
    th, tr, vi, zh_HK and zh_TW.
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.5/glade3-3.5.3.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.5/glade3-3.5.2.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.5/glade3-3.5.1.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.5/glade3-3.5.4.changes
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.5/glade3-3.5.3.changes
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.5/glade3-3.5.2.changes
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.5/glade3-3.5.1.changes

* Tue Sep 16 2008 Debarshi Ray <rishi@fedoraproject.org> - 3.4.5-1
- Version bump to 3.4.5.
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.4/glade3-3.4.5.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.4/glade3-3.4.5.changes

* Wed Apr 19 2008 Debarshi Ray <rishi@fedoraproject.org> - 3.4.4-1
- Version bump to 3.4.4.
  * Duplicate widget names not allowed in a project.
  * Translation updates: sq, tr, bg, da, es, en_GB, ml, pt_BR and hi.
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.4/glade3-3.4.4.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.4/glade3-3.4.4.changes

* Wed Mar 12 2008 Debarshi Ray <rishi@fedoraproject.org> - 3.4.3-1
- Version bump to 3.4.3.
  * Ported to GtkTooltip. (GNOME Bugzilla #500947)
  * Translation updates: nb, ru, fr, lt, mk, it, hu, pt_BR, en_GB, gl, ca, fi,
    de, pt, th, uk, he, tr, vi, oc, sv, ar, es and ja.
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.4/glade3-3.4.3.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.4/glade3-3.4.2.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.4/glade3-3.4.3.changes
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.4/glade3-3.4.2.changes

* Sun Mar 02 2008 Debarshi Ray <rishi@fedoraproject.org> - 3.4.1-5
- Removed 'BuildRequires: gtk-doc' from all distributions, except Fedora 7.
- Added 'Requires: gtk-doc' for glade3-libgladeui-devel.

* Sun Mar 02 2008 Debarshi Ray <rishi@fedoraproject.org> - 3.4.1-4
- Replaced 'BuildRequires: chrpath' with 'BuildRequires: libtool' for removing
  rpaths.

* Sun Feb 03 2008 Debarshi Ray <rishi@fedoraproject.org> - 3.4.1-3
- Omitted unused direct shared library dependencies.

* Fri Dec 21 2007 Debarshi Ray <rishi@fedoraproject.org> - 3.4.1-2
- Removed deletion of /var/lib/scrollkeeper from all distributions, except
  Fedora 7.

* Thu Dec 20 2007 Debarshi Ray <rishi@fedoraproject.org> - 3.4.1-1
- Version bump to 3.4.1.
  * Translation updates: nb, sl, et, ar, tr, gl, ko, ja and pt_BR.
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.4/glade3-3.4.1.news
  * http://ftp.gnome.org/pub/GNOME/sources/glade3/3.4/glade3-3.4.1.changes

* Tue Nov 27 2007 Debarshi Ray <rishi@fedoraproject.org> - 3.4.0-5
- Fixed usage of _remove_encoding to prevent failure on Fedora 7.
- Added 'BuildRequires: gtk-doc' and 'BuildRequires: scrollkeeper' to prevent
  failure on Fedora 7.

* Sun Nov 25 2007 Debarshi Ray <rishi@fedoraproject.org> - 3.4.0-4
- Removed Encoding from Desktop Entry for all distributions, except Fedora 7.

* Tue Nov 13 2007 Debarshi Ray <rishi@fedoraproject.org> - 3.4.0-3
- Clarified multiple licensing issues according to Fedora licensing guidelines.
- Trimmed the 'BuildRequires' list.
- Trimmed the 'Requires' list for glade3-libgladeui-devel.
- Removed custom config files for /etc/ld.so.conf.d.

* Wed Nov 07 2007 Debarshi Ray <rishi@fedoraproject.org> - 3.4.0-2
- Added 'BuildRequires: chrpath' for removing rpaths.

* Tue Nov 06 2007 Debarshi Ray <rishi@fedoraproject.org> - 3.4.0-1
- Initial build. Imported SPEC written by Yijun Yuan and fixed by Tim
  Lauridsen.
  * Translation updates: et, es, fi, gl, sv, en_CA, ja, pt_BR, th, hu, pt, da,
    vi, bg, lt, mk, nb, uk, it, de, si, bn, fr, ar, en_GB, ru, pl and ca.
- Included custom config files for /etc/ld.so.conf.d.
- Changed Name to differentiate with Glade-2.
