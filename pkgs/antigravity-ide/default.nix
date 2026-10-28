{
  lib,
  stdenv,
  fetchurl,
  buildFHSEnv,
  autoPatchelfHook,
  makeWrapper,
  addDriverRunpath,
  desktop-file-utils,
  # Desktop & Graphical Libraries
  alsa-lib,
  at-spi2-atk,
  at-spi2-core,
  cairo,
  cups,
  curl,
  dbus,
  expat,
  fontconfig,
  freetype,
  gdk-pixbuf,
  glib,
  gtk3,
  libdrm,
  libgbm,
  libglvnd,
  libnotify,
  libpulseaudio,
  libsecret,
  libsoup_3,
  libxkbcommon,
  mesa,
  nspr,
  nss,
  openssl,
  pango,
  systemd,
  udev,
  webkitgtk_4_1,
  libX11,
  libXcomposite,
  libXdamage,
  libXext,
  libXfixes,
  libXrandr,
  libxcb,
  libxkbfile,
  zlib,
  # Darwin support
  undmg ? null,
}:

let
  sources = builtins.fromJSON (builtins.readFile ./sources.json);
  inherit (stdenv.hostPlatform) system;

  platformInfo = sources.platforms.${system} or (throw "Unsupported platform: ${system}");
  version = sources.version;

  archiveName =
    if stdenv.hostPlatform.isDarwin then
      "Antigravity-IDE-${version}.dmg"
    else
      "Antigravity-IDE-${version}.tar.gz";

  src = fetchurl {
    name = archiveName;
    url = platformInfo.url;
    hash = platformInfo.hash;
  };

  meta = with lib; {
    description = "Google's agent-first development environment built on VS Code";
    homepage = "https://antigravity.google";
    downloadPage = "https://antigravity.google/download";
    license = licenses.unfree;
    maintainers = [ ];
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
      "aarch64-darwin"
    ];
    mainProgram = "antigravity-ide";
    priority = 10;
  };

  darwinPkg = stdenv.mkDerivation {
    pname = "antigravity-ide";
    inherit version src meta;

    nativeBuildInputs = [ undmg ];

    sourceRoot = ".";

    installPhase = ''
      runHook preInstall
      mkdir -p "$out/Applications/Antigravity IDE.app" "$out/bin"
      cp -R "Antigravity IDE.app/." "$out/Applications/Antigravity IDE.app/"
      ln -s "$out/Applications/Antigravity IDE.app/Contents/Resources/app/bin/antigravity-ide" "$out/bin/antigravity-ide"
      ln -s "$out/bin/antigravity-ide" "$out/bin/antigravity"
      runHook postInstall
    '';
  };

  linuxUnwrapped = stdenv.mkDerivation {
    pname = "antigravity-ide-unwrapped";
    inherit version src;

    # Handle whitespace in archive folder name
    sourceRoot = "Antigravity IDE";

    nativeBuildInputs = [
      autoPatchelfHook
      makeWrapper
      addDriverRunpath
      desktop-file-utils
    ];

    buildInputs = [
      alsa-lib
      at-spi2-atk
      at-spi2-core
      cairo
      cups
      curl
      dbus
      expat
      fontconfig
      freetype
      gdk-pixbuf
      glib
      gtk3
      libdrm
      libgbm
      libglvnd
      libnotify
      libpulseaudio
      libsecret
      libsoup_3
      libxkbcommon
      mesa
      nspr
      nss
      openssl
      pango
      systemd
      udev
      webkitgtk_4_1
      libX11
      libXcomposite
      libXdamage
      libXext
      libXfixes
      libXrandr
      libxcb
      libxkbfile
      zlib
    ];

    runtimeDependencies = [
      (lib.getLib systemd)
      libsecret
      libnotify
      libpulseaudio
      libglvnd
      webkitgtk_4_1
      libsoup_3
    ];

    autoPatchelfIgnoreMissingDeps = [
      "libc.musl-x86_64.so.1"
      "libc.musl-aarch64.so.1"
      "libwebkit2gtk-4.1.so.0"
    ];

    appendRunpaths = [
      "${webkitgtk_4_1}/lib"
      "${addDriverRunpath.driverLink}/lib"
    ];

    installPhase = ''
      runHook preInstall

      mkdir -p $out/lib/antigravity-ide $out/bin $out/share/applications $out/share/pixmaps $out/share/icons/hicolor/1024x1024/apps $out/share/icons/hicolor/scalable/apps

      cp -r ./* $out/lib/antigravity-ide/

      # Install main binary and CLI launcher symlinks
      ln -s $out/lib/antigravity-ide/antigravity-ide $out/bin/antigravity-ide
      ln -s $out/bin/antigravity-ide $out/bin/antigravity

      # Install desktop file
      install -Dm644 ${../../assets/antigravity.desktop} $out/share/applications/antigravity.desktop
      desktop-file-edit --set-key=Exec --set-value="antigravity-ide %F" $out/share/applications/antigravity.desktop

      # Install icons
      install -Dm644 ${../../assets/antigravity.png} $out/share/pixmaps/antigravity.png
      install -Dm644 ${../../assets/antigravity.png} $out/share/icons/hicolor/1024x1024/apps/antigravity.png
      install -Dm644 ${../../assets/antigravity.svg} $out/share/icons/hicolor/scalable/apps/antigravity.svg

      # Register mime associations
      mkdir -p $out/share/mime/packages
      cat > $out/share/mime/packages/antigravity-ide.xml <<EOF
      <?xml version="1.0" encoding="UTF-8"?>
      <mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
        <mime-type type="x-scheme-handler/antigravity">
          <comment>Antigravity Protocol Handler</comment>
        </mime-type>
        <mime-type type="x-scheme-handler/antigravity-ide">
          <comment>Antigravity IDE Protocol Handler</comment>
        </mime-type>
      </mime-info>
      EOF

      runHook postInstall
    '';

    postFixup = ''
      addDriverRunpath $out/lib/antigravity-ide/antigravity-ide
    '';
  };

  linuxFHS = buildFHSEnv {
    name = "antigravity-ide";
    pname = "antigravity-ide";
    inherit version meta;

    targetPkgs = pkgs: [
      linuxUnwrapped
      # System base tools for terminal & extensions
      pkgs.coreutils
      pkgs.bash
      pkgs.zlib
      pkgs.glibc
      pkgs.curl
      pkgs.git
      pkgs.openssh
      pkgs.gnupg
      pkgs.which
      pkgs.python3
      # Graphical / GUI runtime dependencies
      pkgs.alsa-lib
      pkgs.at-spi2-atk
      pkgs.at-spi2-core
      pkgs.cairo
      pkgs.cups
      pkgs.dbus
      pkgs.expat
      pkgs.fontconfig
      pkgs.freetype
      pkgs.gdk-pixbuf
      pkgs.glib
      pkgs.gtk3
      pkgs.libdrm
      pkgs.libgbm
      pkgs.libglvnd
      pkgs.libnotify
      pkgs.libpulseaudio
      pkgs.libsecret
      pkgs.libsoup_3
      pkgs.libxkbcommon
      pkgs.mesa
      pkgs.nspr
      pkgs.nss
      pkgs.openssl
      pkgs.pango
      pkgs.systemd
      pkgs.udev
      pkgs.webkitgtk_4_1
      pkgs.libX11
      pkgs.libXcomposite
      pkgs.libXdamage
      pkgs.libXext
      pkgs.libXfixes
      pkgs.libXrandr
      pkgs.libxcb
      pkgs.libxkbfile
    ];

    extraBwrapArgs = [
      "--bind-try /etc/nixos/ /etc/nixos/"
      "--ro-bind-try /etc/xdg/ /etc/xdg/"
    ];

    extraInstallCommands = ''
      mkdir -p $out/share/applications $out/share/pixmaps $out/share/icons $out/share/mime
      ln -s ${linuxUnwrapped}/share/applications/* $out/share/applications/
      ln -s ${linuxUnwrapped}/share/pixmaps/* $out/share/pixmaps/
      ln -s ${linuxUnwrapped}/share/icons/* $out/share/icons/
      ln -s ${linuxUnwrapped}/share/mime/* $out/share/mime/
      ln -s $out/bin/antigravity-ide $out/bin/antigravity
    '';

    runScript = "antigravity-ide";

    passthru = {
      unwrapped = linuxUnwrapped;
      inherit sources;
    };
  };

in
if stdenv.hostPlatform.isDarwin then darwinPkg else linuxFHS
