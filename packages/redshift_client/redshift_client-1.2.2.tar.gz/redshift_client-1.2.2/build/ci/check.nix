{self_pkg}: let
  build_check = check:
    self_pkg.overridePythonAttrs (
      old: {
        installCheckPhase = [old."${check}"];
      }
    );
in {
  tests = build_check "type_check";
  types = build_check "test_check";
  arch = build_check "arch_check";
}
