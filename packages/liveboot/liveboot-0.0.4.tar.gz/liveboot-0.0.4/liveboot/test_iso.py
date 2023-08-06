from argparse import ArgumentParser
from pathlib import Path

from .idrac import I

# sopnode-l1 is the server
# xxx to check, maybe the drac is able to perform lookups ?
HTTP_SERVER = "138.96.245.50"
HTTP_PATH = "bootable-images"

CIDATA = "cidata-seed.iso"

def main():
    parser = ArgumentParser()
    parser.add_argument("sopnode")
    parser.add_argument("iso")
    args = parser.parse_args()

    h = args.sopnode.replace("sopnode-", "").replace("-drac", "").replace(".inria.fr", "")
    h = f"sopnode-${h}-drac.inria.fr"
    iso = Path(args.iso).name
    with Idrac("sopnode-w3-drac.inria.fr", "diana", "diana-2021") as w3:


        w3.insert_virtual_media(index=1, uripath=f"http://{HTTP_SERVER}/{HTTP_PATH}/{iso}")
        w3.insert_virtual_media(index=2, uripath=f"http://{HTTP_SERVER}/{HTTP_PATH}/{CIDATA}")
        w3.set_next_one_time_boot_virtual_media_device(index=1)

        w3.get_all_bios_attributes()
        w3.get_bios_attribute("SysProfile")
        w3.set_bios_attribute("SysProfile", "PerfPerWattOptimizedDapc")

        w3.get_power_state()
        w3.set_power_state("ForceOff")
        w3.set_power_state("GracefulShutdown")

if __name__ == "__main__":
    main()
