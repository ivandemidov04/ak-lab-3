import pytest
import tempfile
import os
import contextlib
import io

import translator
import simulation


@pytest.mark.golden_test("golden/*.yml")
def test_translator_and_machine(golden):
    with tempfile.TemporaryDirectory() as tmpdirname:
        source = os.path.join(tmpdirname, "source.asm")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target = os.path.join(tmpdirname, "target.txt")
        # debug_log = golden.get("debug_log", True)
        # log = os.path.join(tmpdirname, "processor.txt")
        # debug_log = golden.get("debug_log", True)

        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["input"])

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            with contextlib.redirect_stderr(io.StringIO()) as stderr:
                translator.main(source, target)
                simulation.main(target, input_stream)

        with open(target, encoding="utf-8") as file:
            code = file.read()

        assert code == golden.out["machine_code"]
        assert stdout.getvalue() == golden.out["output"]
        assert stderr.getvalue() == golden.out["log"]
        # assert log == golden.out["processor.log"]
        # assert stderr.getvalue() == golden.out["out_log"]
