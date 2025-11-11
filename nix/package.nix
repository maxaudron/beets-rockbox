{
  lib,
  buildPythonPackage,

  # build-system
  hatchling,

  # nativeBuildInputs
  beets-minimal,
  enlighten,

  # tests
  pytestCheckHook,
  pytest-cov-stub,
  typeguard,
  writableTmpDirAsHomeHook,
}:

buildPythonPackage rec {
  pname = "beets-rockbox";
  version = "1.0.0";
  pyproject = true;

  src = ../.;

  build-system = [
    hatchling
  ];

  nativeBuildInputs = [
    beets-minimal
  ];

  propagatedBuildInputs = [
    enlighten
  ];

  nativeCheckInputs = [
    pytestCheckHook
    pytest-cov-stub
    typeguard
    writableTmpDirAsHomeHook
  ];

  pytestDisabledFiles = [
    "cli_test.py"
    "database_test.py"
  ];

  meta = {
    description = "Beets plugin to build a rockbox database from your library";
    homepage = "https://github.com/maxaudron/beets-rockbox";
    changelog = "https://github.com/maxaudron/beets-rockbox/blob/v${version}/CHANGELOG.md";
    maintainers = with lib.maintainers; [
      maxaudron
    ];
    license = lib.licenses.mit;
  };
}
