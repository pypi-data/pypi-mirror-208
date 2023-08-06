{
  pkgs ? import <nixpkgs> {}
}:

pkgs.python3Packages.buildPythonPackage rec {
  pname = "spendpoint";
  version = "0.2.0";
  format = "pyproject";
  src = ./.;

  nativeBuildInputs = [
    #flit-core
  ];

  buildInputs = [
    #flit-core
  ];

  propagatedBuildInputs = [
    pkgs.python3Packages.jinja2
  ];
}
