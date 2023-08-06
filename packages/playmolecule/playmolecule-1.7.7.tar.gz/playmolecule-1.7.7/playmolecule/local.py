import os
import shutil
import subprocess
import logging
from protocolinterface import ProtocolInterface, val

logger = logging.getLogger(__name__)


def find_executable(exe_name):
    exe = shutil.which(exe_name, mode=os.X_OK)
    if not exe:
        return None
    if os.path.islink(exe):
        if os.path.isabs(os.readlink(exe)):
            exe = os.readlink(exe)
        else:
            exe = os.path.join(os.path.dirname(exe), os.readlink(exe))
    return exe


class LocalSession:
    def __init__(self, imagepath, license_ip, license_port, singularity=None) -> None:
        self.imagepath = imagepath
        self.license_server = f"{license_port}@{license_ip}"
        self.singularity = singularity

        if self.singularity is None:
            self.singularity = find_executable("singularity")

    def start_app(self, appname, suffix="_v1"):
        from glob import glob
        import tempfile
        import json

        appfiles = glob(os.path.join(self.imagepath, f"*{suffix}"))
        apps = {
            os.path.basename(appf).replace(suffix, "").lower(): os.path.abspath(appf)
            for appf in appfiles
        }

        decrypter = os.path.join(self.imagepath, "pm-decrypter")
        if not os.path.exists(decrypter):
            raise RuntimeError(
                f"Could not find executable pm-decrypter at {self.imagepath}"
            )

        if appname.lower() not in apps:
            raise RuntimeError(
                f"Could not find application {appname}. Available apps include {list(apps.keys())}"
            )

        appfile = apps[appname.lower()]
        with tempfile.TemporaryDirectory() as tmpdir:
            apppkl = os.path.join(tmpdir, f"{appname}.parser.pkl")
            runenv = os.environ.copy()
            runenv["ACELLERA_LICENCE_SERVER"] = self.license_server
            subprocess.run(
                [
                    decrypter,
                    "-appimage",
                    appfile,
                    "-singularity",
                    self.singularity,
                    "run",
                    appfile,
                    "--dump-argparser",
                    apppkl,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=runenv,
            )
            with open(apppkl, "r") as f:
                job_json = json.load(f)

        return LocalJob(
            job_json, decrypter, appfile, self.singularity, self.license_server
        )


class LocalJob(ProtocolInterface):
    def __init__(
        self, app_config_json, decrypter, appfile, singularity, license_server
    ) -> None:
        super().__init__()
        # self._arg("inputpath", "string", "input path", "/tmp", val.String())
        # self._arg("output", "string", "Output path", ".", val.String())

        self._app_config_json = app_config_json
        self._decrypter = decrypter
        self._appfile = appfile
        self._singularity = singularity
        self._license_server = license_server
        self._create_app_properties(app_config_json)

    def describe(self):
        from playmolecule.session import _describe_app

        tmp = self._app_config_json.copy()
        tmp["periodicities"] = []
        _describe_app(tmp)

    def _create_app_properties(self, app_config_json):
        for param in app_config_json["params"]:
            validator = self._get_validator(param["type"])
            value = self._get_value(param["type"], param["value"], param["name"])
            self._arg(
                param["name"],
                param["type"],
                param["description"],
                value,
                validator,
                required=param["mandatory"],
            )

    def _get_validator(self, type):
        if type == "bool":
            return val.Boolean()
        elif type == "int":
            return val.Number(int, "ANY")
        elif type == "string":
            return val.String()
        elif type == "file":
            return val.String()
        elif type == "float":
            return val.Number(float, "ANY")
        elif type == "fileORstring":
            return val.String()

    def _get_value(self, type, value, name):
        if value is None:
            return None

        if type == "bool":
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            raise ValueError(f'Invalid bool value "{value}" for argument {name}')
        elif type == "int":
            if value == "":
                return None
            try:
                converted_value = int(value)
                return converted_value
            except ValueError:
                raise ValueError(f'Invalid int value "{value}" for argument {name}')
        elif type == "float":
            if value == "":
                return None
            try:
                converted_value = float(value)
                return converted_value
            except ValueError:
                raise ValueError(f'Invalid float value "{value}" for argument {name}')
        elif type == "string" or type == "fileORstring" or type == "file":
            return value

    def submit(self):
        args = []
        for cmd in self._commands:
            val = getattr(self, cmd)
            if val is None or (isinstance(val, str) and len(val) == 0):
                continue
            if self._commands[cmd]["datatype"] == "bool":
                if (isinstance(val, bool) and val) or (
                    isinstance(val, str) and val.lower() == "true"
                ):
                    args.append(f"--{cmd}")
            else:
                args.append(f"--{cmd}")
                args.append(str(val))

        print("ARGS", args)

        runenv = os.environ.copy()
        runenv["ACELLERA_LICENCE_SERVER"] = self._license_server
        subprocess.run(
            [
                self._decrypter,
                "-appimage",
                self._appfile,
                "-singularity",
                self._singularity,
                "run",
                "--nv",
                "--cleanenv",
                "--no-home",
                self._appfile,
            ]
            + args,
            check=True,
            env=runenv,
        )
