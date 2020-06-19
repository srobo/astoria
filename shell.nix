{
  pkgsSrc ? <nixpkgs>,
  pkgs ? import pkgsSrc {},
}:

with pkgs;

stdenv.mkDerivation {
  name = "astoria-dev-env";
  buildInputs = [
    gnumake
    python3
    python3Packages.poetry
  ];
}
