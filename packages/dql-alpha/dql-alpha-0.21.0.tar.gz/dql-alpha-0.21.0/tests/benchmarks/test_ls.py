def test_ls(bench_dql, tmp_dir, bucket):  # pylint: disable=unused-argument
    bench_dql("ls", bucket, "--aws-anon")
