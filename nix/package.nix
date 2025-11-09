{
  lib,
  buildPythonPackage,

  # build-system
  poetry-core,

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
    poetry-core
  ];

  nativeBuildInputs = [
    beets-minimal
    enlighten
  ];

  nativeCheckInputs = [
    pytestCheckHook
    pytest-cov-stub
    typeguard
    writableTmpDirAsHomeHook
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
