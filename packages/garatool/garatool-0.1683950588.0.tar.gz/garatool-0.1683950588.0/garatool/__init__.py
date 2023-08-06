import garatool
import sys
import argparse
import binascii
import msgpack
import shutil
import esptool
import serial
import subprocess
import requests
import uuid
import platform
import tempfile


import dacite
import os


from dataclasses import dataclass, asdict, field
from enum import Enum
from termcolor import colored
import colorama

colorama.init()


def flag(str):
    return colored(str, "yellow")


def step(str):
    return colored(":::::::" + str + ":::::::", "magenta", "on_yellow")


def cmd(str):
    print("Run: ", colored(repr(str), "cyan"))
    return str


PYTHON = sys.executable
ESPTOOL = f'"{PYTHON}" "{esptool.__file__}" '


class Board(Enum):
    CreatorPlus: str = "plus"
    CreatorIoT: str = "iot"

    def __str__(self):
        return self.name


print(step("Checking system path"))
print("python", flag(PYTHON))
print("esptool", flag(esptool.__file__))


parser = argparse.ArgumentParser()
parser.add_argument(
    "-b", "--board", type=Board, choices=list(Board), help="Select board type"
)
parser.add_argument("-p", "--port", help="Select the COM port")
parser.add_argument("-t", "--tag", type=str, help="Select firmware tag", default="dev")
parser.add_argument("-i", "--imei", type=str, help="IMEI code", default="")
parser.add_argument("-n", "--name", help="Device name", default="Creator Device")
parser.add_argument("-s", "--serial", action="store_true", help="Enable Serial debug")
parser.add_argument(
    "-u", "--upload", help="(Admin) Publish firmware tag", action="store_true"
)
parser.add_argument("-k", "--key", help="(Admin) With secret key", default="")
parser.add_argument("-r", "--root", help="(Admin) Location of firmware", default="")
parser.add_argument(
    "-d", "--download", help="(Admin) Download tagged firmware", action="store_true"
)


def get_mac(port: str, nostub: bool) -> str:
    output = subprocess.getoutput(
        cmd(" ".join([ESPTOOL, "-p", port, "--no-stub" if nostub else " ", "read_mac"]))
    )
    for line in output.splitlines():
        if line.startswith("MAC"):
            mac = line.split(" ")[-1]
            break
    else:
        raise Exception("Can't read the MAC Address of the device")

    mac = mac.split(":")
    mac = bytes([int(f"0x{ids}", 16) for ids in mac])
    mac = binascii.b2a_base64(mac).strip().decode("utf8")
    print("get_mac", flag(mac))
    return mac


parsed = parser.parse_args()
for key, value in vars(parsed).items():
    print("[]", key, flag(value), sep="\t")

######### ######### ######### ######### ######### ######### ######### #########


@dataclass
class BuildRequest:
    chipset: str = ""
    nostub: bool = False
    mac: str = ""
    imei: str = ""
    name: str = "Creator Device"
    tag: str = ""
    key: str = ""
    event: str = "build_firmware"
    uuid: str = ""
    files: dict = field(default_factory=dict)

    root: str = ""
    upload: bool = False
    key: str = ""
    # Segments from server response
    partitions: list = field(default_factory=list)
    status: str = ""
    event: str = ""


def request_firmware_build(br: BuildRequest):
    req = requests.post(
        url="https://api.garastem.com/api/v1/toolchain/garatool",
        data=msgpack.dumps(asdict(br)),
    )
    print(req, flag(req.status_code))
    if req.status_code != 200:
        raise Exception("Problem: " + req.text)
    response = dacite.from_dict(BuildRequest, msgpack.loads(req.content, raw=False))
    # print('Response', flag(response))
    return response


def program_device(br: BuildRequest):
    # for parti in br.partitions:
    for i in range(len(br.partitions)):
        parti = br.partitions[i]
        # parti['file'] = tempfile.mkstemp()[1]
        print(parti["file"], parti["offset"], len(parti["data"]))
        with open(parti["file"], "wb") as f:
            f.write(parti["data"])

    partition_params = " ".join([f'{p["offset"]} "{p["file"]}"' for p in br.partitions])

    subprocess.getoutput(
        cmd(
            " ".join(
                [
                    ESPTOOL,
                    "--port",
                    parsed.port,
                    "--baud",
                    "460800",
                    "--no-stub" if br.nostub else " " "--before=default_reset",
                    "--after=hard_reset",
                    "--chip",
                    "auto",
                    "write_flash",
                    "--flash_mode=dio",
                    "--flash_size=keep",
                    partition_params,
                ]
            )
        )
    )

    for parti in br.partitions:
        try:
            os.remove(parti["file"])
        except OSError:
            pass


def download_tag(tag: str, key: str):
    req = requests.post(
        url="https://api.garastem.com/api/v1/toolchain/garatool",
    )


def start():
    br = BuildRequest()
    br.event = "build_firmware"
    br.name = parsed.name
    br.imei = parsed.imei
    br.tag = parsed.tag
    br.key = parsed.key
    br.upload = parsed.upload
    br.key = parsed.key
    br.uuid = str(uuid.uuid4())

    if len(parsed.imei) != 0:
        if len(parsed.imei) != 13:
            raise Exception("Invalid IMEI Length")

        reverse = input("Please type IMEI in reverse: ")
        reverse = reverse[::-1]
        if reverse != parsed.imei:
            raise Exception("IMEI doesn't match")

    if parsed.board == Board.CreatorPlus:
        br.chipset = "GENERIC_C3_USB"
        br.nostub = True
    elif parsed.board == Board.CreatorIoT:
        br.chipset = "GENERIC_SPIRAM"
        br.nostub = False

    if parsed.port:
        print("Port: Connecting to serial ", flag(parsed.port))
        # if port is available then get the mac
        br.mac = get_mac(parsed.port, br.nostub)

    if parsed.upload:
        # gather list of flat files
        fws = dict()
        print("Gathering file from root", flag(parsed.root))
        for file in os.listdir(parsed.root):
            if not (file.endswith(".py") or file.endswith(".pym")):
                continue
            if file.startswith("__"):
                continue
            print(file)
            content = open(os.path.join(parsed.root, file), "rb").read()
            fws[file] = content
        br.files = fws

    print(step("Downloading firmware ..."))
    br = request_firmware_build(br)
    # Start burning firmware
    print(step("Programming device ..."))
    program_device(br)

    if parsed.serial:
        print(platform.system())
        if platform.system().lower() == "darwin":
            os.system("say start")
            os.system(f"screen {parsed.port} 115200")
