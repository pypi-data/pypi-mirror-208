import os
import sys
import shutil
import argparse
import subprocess

from pathlib import Path
from typing import List

LIB_DAISY = Path("/home/lukas/repos/daisy-clang") / "build" / "lib" / "libDaisy.so"
DACE_RUNTIME_PATH = "-I/home/lukas/repos/dace/dace/runtime/include/"


class ClangWrapper:
    def __init__(
        self, executable: str, clang_executable: str, args, unknown: List[str]
    ) -> None:
        self._executable = executable
        self._clang_executable = clang_executable
        self._args = args

        # Special flags
        self._O = "-O2"
        self._g = False
        self._fPIE = True
        self._fopenmp = False

        D = []
        if self._args.D is not None:
            D = ["-D" + macro for macro in self._args.D]
        U = []
        if self._args.U is not None:
            U = ["-U" + macro for macro in self._args.U]
        self._macros = D + U

        # Standard flags
        self._unknown = set(unknown)
        self._options = []
        self._warnings = []
        self._foptions = []
        for option in set(unknown):
            if option == "-O1":
                self._O = option
            elif option == "-O2":
                self._O = option
            elif option == "-O3":
                self._O = option
            elif option == "-g":
                self._g = True
            elif option == "-fPIE":
                continue
            elif option == "-fopenmp":
                self._fopenmp = True
            elif option.startswith("-stdlib"):
                self._options.append(option)
            elif option.startswith("-std"):
                self._options.append(option)
            elif option == "-pedantic":
                self._options.append(option)
            elif option.startswith("-Wa"):
                continue
            elif option.startswith("-Wl"):
                continue
            elif option.startswith("-Wp"):
                continue
            elif option.startswith("-W"):
                self._warnings.append(option)
            elif option == "-w":
                self._warnings.append(option)
            else:
                continue

            self._unknown.remove(option)

    def execute(self):
        if self._unknown and not self._args.ignore_unknown:
            raise ValueError("Unknown options provided: ", self._unknown)

        retcode = 1
        if len(sys.argv) == 1:
            retcode = self._empty()
        elif self._args.version:
            retcode = self._version()
        elif self._args.v and len(sys.argv) == 2:
            retcode = self._verbose()
        else:
            inputs = [Path(input) for input in self._args.file]
            object_mode = False
            for input in inputs:
                if input.suffix == ".o":
                    object_mode = True
                    break

            if not object_mode:
                output = self._args.o
                includes = self._args.I
                if includes is None:
                    includes = []
                isystems = self._args.isystem
                if isystems is None:
                    isystems = []

                retcode = self._compile(
                    inputs=inputs, output=output, includes=includes, isystems=isystems
                )

            if object_mode or retcode > 0:
                retcode = _execute_command([self._clang_executable] + sys.argv[1:])

        return retcode

    def _empty(self):
        return _execute_command([self._clang_executable])

    def _version(self):
        cmd = [self._clang_executable, "--version"]
        return _execute_command(cmd)

    def _verbose(self):
        cmd = [self._clang_executable, "-v"]
        return _execute_command(cmd)

    def _compile(
        self, inputs: List[str], output: str, includes: List[str], isystems: List[str]
    ):
        cache_folder = Path() / ".daisycache"
        if cache_folder.is_dir():
            shutil.rmtree(cache_folder)

        cache_folder.mkdir(exist_ok=True, parents=False)

        # Preprocessor, Compile to LLVM IR
        clang_options = [
            "-S",
            "-emit-llvm",
            "-fno-vectorize",
            "-fno-slp-vectorize",
            "-fno-tree-vectorize",
            "-fno-unroll-loops",
        ]
        if self._g:
            clang_options.append("-g")
        if self._fopenmp:
            clang_options.append("-fopenmp")
        if self._args.v:
            clang_options.append("-v")
        if self._O != "-O3":
            clang_options.append(self._O)
        else:
            clang_options.append("-O2")

        dependency_files = {}
        llvm_source_files = []
        for input_file in inputs:
            llvm_file = str(cache_folder / f"{input_file.stem}.ll")

            dependencies = []
            if self._args.write_dependencies:
                dependencies.append("-MD")
                dependencies.append(
                    "-MF" + str(cache_folder / f"{input_file.name}.o.d")
                )
                dependency_files[cache_folder / f"{input_file.name}.o"] = (
                    cache_folder / f"{input_file.name}.o.d"
                )

            cmd = (
                [self._clang_executable]
                + clang_options
                + dependencies
                + self._options
                + self._warnings
                + self._macros
                + self._foptions
                + [f"-I{include}" for include in includes]
                + [f"-isystem {isystem}" for isystem in isystems]
                + ["-o", llvm_file]
                + [str(input_file)]
            )
            ret_code = _execute_command(cmd)
            if ret_code > 0:
                return ret_code

            llvm_dace_file = cache_folder / f"{input_file.stem}_dace.ll"
            cmd = [
                "opt",
                "-polly-allow-unsigned-operations",
                "-polly-allow-nonaffine-branches",
                "-polly-allow-nonaffine-loops=true",
                "-polly-allow-nonaffine",
                # "-polly-process-unprofitable=true",
                "-load-pass-plugin",
                LIB_DAISY,
                f"--daisy-transfer-tune={self._args.ftransfer_tune}",
                "--passes=Daisy",
                llvm_file,
                "-S",
                "-o",
                llvm_dace_file,
            ]
            ret_code = _execute_command(cmd)
            if ret_code > 0:
                return ret_code

            llvm_source_files.append(llvm_dace_file)

            # Preprocessor, Compile to LLVM IR
            sdfgs = [
                Path(path) for path in input_file.parent.glob("sdfg_*") if path.is_dir()
            ]
            print(sdfgs)
            for sdfg_base in sdfgs:
                sdfg_path = (
                    sdfg_base / "dacecache" / "src" / "cpu" / f"{sdfg_base.stem}.cpp"
                )
                sdfg_ll_file = cache_folder / f"{sdfg_base.stem}.ll"

                dependencies = []
                if self._args.write_dependencies:
                    dependencies.append("-MD")
                    dependencies.append(
                        "-MF" + str(cache_folder / f"{sdfg_ll_file.stem}.o.d")
                    )
                    dependency_files[sdfg_path.name] = (
                        cache_folder / f"{sdfg_ll_file.stem}.o.d"
                    )

                cmd = [
                    "clang++",
                    "-O3",
                    "-funroll-loops",
                    "-std=c++17",
                    "-stdlib=libc++",
                    "-S",
                    "-emit-llvm",
                    sdfg_path,
                    "-o",
                    sdfg_ll_file,
                    DACE_RUNTIME_PATH,
                ] + dependencies
                ret_code = _execute_command(cmd)
                if ret_code > 0:
                    return ret_code

                llvm_source_files.append(sdfg_ll_file)

        if self._args.write_dependencies:
            dest_file = cache_folder / Path(self._args.MT).name
            d_file = dependency_files[dest_file]
            shutil.copy(d_file, self._args.MF)

        # Linker
        llvm_link_options = []
        cmd = (
            ["llvm-link"]
            + llvm_link_options
            + ["-o", cache_folder / "program.ll"]
            + llvm_source_files
        )
        ret_code = _execute_command(cmd)
        if ret_code > 0:
            return ret_code

        # Compile to Object Format
        llc_options = ["-filetype=obj", self._O]
        if self._fPIE:
            llc_options.append("-relocation-model=pic")
        if self._args.compile:
            llc_options.append("-o")
            llc_options.append(output)
        else:
            llc_options.append("-o")
            llc_options.append(cache_folder / "program.o")

        cmd = ["llc"] + llc_options + [cache_folder / "program.ll"]
        ret_code = _execute_command(cmd)
        if ret_code > 0:
            return ret_code

        if self._args.compile:
            return ret_code

        # Assembler
        bin_options = [self._O]
        cmd = (
            [self._clang_executable]
            + bin_options
            + ["-o", output, cache_folder / "program.o"]
        )
        ret_code = _execute_command(cmd)
        if ret_code > 0:
            return ret_code

        return 0

    @classmethod
    def create(cls, args: List[str]):
        # Determine executable
        executable = Path(args[0]).name
        if executable == "daisy-clang":
            clang_executable = "clang"
        else:
            clang_executable = "clang++"

        parser = argparse.ArgumentParser(
            prog=f"daisy-{clang_executable}",
            description=f"Daisy wrapper for {clang_executable}",
        )
        parser.add_argument("--version", action="store_true", default=False)
        parser.add_argument("-v", action="store_true", default=False)
        parser.add_argument("-o", default="a.out")
        parser.add_argument("-I", action="append")
        parser.add_argument("-D", action="append")
        parser.add_argument("-U", action="append")
        parser.add_argument("-isystem", action="append")
        parser.add_argument("file", type=str, nargs="*")

        # Compile options
        parser.add_argument("-c", "--compile", action="store_true", default=False)

        # Dependencies
        parser.add_argument(
            "-MD", "--write-dependencies", action="store_true", default=False
        )
        parser.add_argument("-MF", required=False)
        parser.add_argument("-MT", required=False)

        # Transfer tuning flag
        parser.add_argument("--ignore-unknown", action="store_true", default=True)
        parser.add_argument("-ftransfer-tune", action="store_true", default=False)

        args, unknown = parser.parse_known_args()
        return ClangWrapper(
            executable=executable,
            clang_executable=clang_executable,
            args=args,
            unknown=unknown,
        )


def _execute_command(command: List[str]):
    print(" ".join([str(cmd) for cmd in command]))

    process = subprocess.Popen(
        command,
        shell=False,
        stdout=subprocess.PIPE,
    )
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break

        if output:
            out_str = output.__str__()
            print(out_str)

    return process.returncode


def main():
    wrapper = ClangWrapper.create(sys.argv)
    retcode = wrapper.execute()
    exit(retcode)
