def test_version(bench_dql):
    bench_dql("--help", rounds=100)
