{
  nixpkgs,
  python_version,
  src,
}: let
  deps = import ./deps {
    inherit nixpkgs python_version;
  };
  pkg_deps = {
    runtime_deps = with deps.python_pkgs; [
      deprecated
      fa-purity
      psycopg2
      types-deprecated
      types-psycopg2
    ];
    build_deps = with deps.python_pkgs; [flit-core];
    test_deps = with deps.python_pkgs; [
      arch-lint
      mypy
      pytest
    ];
  };
  publish = nixpkgs.mkShell {
    packages = [
      nixpkgs.git
      deps.python_pkgs.flit
    ];
  };
  packages = import ./generic_builder {
    inherit (deps.lib) buildEnv buildPythonPackage;
    inherit pkg_deps src;
  };
  dev_shell = import ./dev_env {
    inherit nixpkgs;
    dev_env = packages.env.dev;
  };
in
  packages // {inherit dev_shell publish;}
