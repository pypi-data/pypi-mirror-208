def read_input_validation(self):
    # table validation
    assert "path" in self.keys(), "Couldn`t find `path` in inputs"
    assert (
        "bucket_name" in self["path"].keys()
    ), "Couldn`t find `bucket_name` in path input"
    assert (
        "object_path" in self["path"].keys()
    ), "Couldn`t find `object_path` in path input"
    assert "partition" in self["path"].keys(), "Couldn`t find `partition` in path input"
    assert "file_type" in self["path"].keys(), "Couldn`t find `file_type` in path input"
    # schema validation
    assert "schema" in self.keys(), "Couldn`t find `schema` in inputs"
    assert (
        "bucket_name" in self["schema"].keys()
    ), "Couldn`t find `file_type` in schema input"
    assert (
        "object_path" in self["schema"].keys()
    ), "Couldn`t find `object_path` in schema input"
    return


def write_input_validation(self):
    # table validation
    assert "write" in self.keys(), "Couldn`t find `write` in inputs"
    assert (
        "bucket_name" in self["write"].keys()
    ), "Couldn`t find `bucket_name` in write input"
    assert (
        "object_path" in self["write"].keys()
    ), "Couldn`t find `object_path` in write input"
    assert (
        "file_type" in self["write"].keys()
    ), "Couldn`t find `file_type` in write input"
    assert (
        "partition" in self["write"].keys()
    ), "Couldn`t find `partition` in write input"
    return
