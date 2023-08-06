import os
from subprocess import check_output

import pytest
from dulwich.porcelain import clone
from packaging import version
from pytest_virtualenv import VirtualEnv


@pytest.fixture
def bucket():
    return "s3://noaa-bathymetry-pds/"


def pytest_generate_tests(metafunc):
    str_revs = metafunc.config.getoption("--dql-revs")
    revs = str_revs.split(",") if str_revs else [None]
    if "dql_rev" in metafunc.fixturenames:
        metafunc.parametrize("dql_rev", revs, scope="session")


@pytest.fixture(scope="session", name="make_dql_venv")
def fixture_make_dql_venv(tmp_path_factory):
    def _make_dql_venv(name):
        venv_dir = tmp_path_factory.mktemp(f"dql-venv-{name}")
        return VirtualEnv(workspace=venv_dir)

    return _make_dql_venv


@pytest.fixture(scope="session", name="dql_venvs")
def fixture_dql_venvs():
    return {}


@pytest.fixture(scope="session", name="dql_git_repo")
def fixture_dql_git_repo(tmp_path_factory, test_config):
    url = test_config.dql_git_repo

    if os.path.isdir(url):
        return url

    tmp_path = os.fspath(tmp_path_factory.mktemp("dql-git-repo"))
    clone(url, tmp_path)

    return tmp_path


@pytest.fixture(scope="session", name="dql_bin")
def fixture_dql_bin(
    dql_rev,
    dql_venvs,
    make_dql_venv,
    dql_git_repo,
    test_config,
):
    if dql_rev:
        venv = dql_venvs.get(dql_rev)
        if not venv:
            venv = make_dql_venv(dql_rev)
            venv.run("pip install -U pip")
            venv.run(f"pip install git+file://{dql_git_repo}@{dql_rev}")
            dql_venvs[dql_rev] = venv
        dql_bin = venv.virtualenv / "bin" / "dql"
    else:
        dql_bin = test_config.dql_bin

    def _dql_bin(*args):
        return check_output([dql_bin, *args], text=True)

    actual = version.parse(_dql_bin("--version"))
    _dql_bin.version = (actual.major, actual.minor, actual.micro)

    return _dql_bin


@pytest.fixture(scope="function", name="make_bench")
def fixture_make_bench(request):
    def _make_bench(name):
        import pytest_benchmark.plugin

        # hack from https://github.com/ionelmc/pytest-benchmark/issues/166
        bench = pytest_benchmark.plugin.benchmark.__pytest_wrapped__.obj(request)

        suffix = f"-{name}"

        def add_suffix(_name):
            start, sep, end = _name.partition("[")
            return start + suffix + sep + end

        bench.name = add_suffix(bench.name)
        bench.fullname = add_suffix(bench.fullname)

        return bench

    return _make_bench


@pytest.fixture(
    scope="function", params=[pytest.param(None, marks=pytest.mark.benchmark)]
)
def bench_dql(dql_bin, make_bench):
    def _bench_dql(*args, **kwargs):
        name = kwargs.pop("name", None)
        name = f"-{name}" if name else ""
        bench = make_bench(args[0] + name)
        return bench.pedantic(dql_bin, args=args, **kwargs)

    return _bench_dql
