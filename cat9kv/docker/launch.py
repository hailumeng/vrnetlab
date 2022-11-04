#!/usr/bin/env python3

import datetime
import logging
import os
import re
import signal
import subprocess
import sys
import time
import random
import string

import vrnetlab

STARTUP_CONFIG_FILE = "/config/startup-config.cfg"


def handle_SIGCHLD(signal, frame):
    os.waitpid(-1, os.WNOHANG)


def handle_SIGTERM(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, handle_SIGTERM)
signal.signal(signal.SIGTERM, handle_SIGTERM)
signal.signal(signal.SIGCHLD, handle_SIGCHLD)

TRACE_LEVEL_NUM = 9
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")


def trace(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kws)


logging.Logger.trace = trace


class CAT9KV_vm(vrnetlab.VM):
    def __init__(
        self, hostname, username, password, nics, conn_mode, install_mode=False
    ):
        for e in os.listdir("/"):
            if re.search(".qcow2$", e):
                disk_image = "/" + e
            if re.search("\.license$", e):
                os.rename("/" + e, "/tftpboot/license.lic")

        self.license = False
        if os.path.isfile("/tftpboot/license.lic"):
            logger.info("License found")
            self.license = True

        super(CAT9KV_vm, self).__init__(username, password, disk_image=disk_image)

        self.install_mode = install_mode
        self.num_nics = nics
        self.hostname = hostname
        self.conn_mode = conn_mode
        self.nic_type = "e1000"
        # We DON'T mount cdrom with bootstrap config and vswitch xml file to bootstrap the VM
        # We MOUNT cdrom when booting up VM to supply the unique serial number.
        if not self.install_mode:
            logger.trace("install mode")
            self.image_name = "config.iso"
            self.create_boot_image()

            self.qemu_args.extend(["-cdrom", "/" + self.image_name])

    def create_boot_image(self):
        """Creates a iso image with a bootstrap configuration"""

        # get iosxe_config.txt file and vswitch.xml file ready for bootstrap ISO. This will give unique serial number to each instance. In addition, the license is changed to Advantage level which requires reboot.
        os.mkdir("/vswitch")
        os.mkdir("/vswitch/conf")
        cfg_file = open("/vswitch/conf/iosxe_config.txt", "w")
        switch_file = open("/vswitch/conf/vswitch.xml", "w")
        self.logger.info("Creating bootstrap iso")
        cfg_file.write("hostname cat9kv\r\n\r\n")
        cfg_file.write("platform console serial\r\n\r\n")
        cfg_file.write("license boot level network-advantage addon dna-advantage\r\n\r\n")
        cfg_file.write("license smart off\r\n\r\n")
        cfg_file.write("do wr\r\n\r\n")
        cfg_file.write("do reload\r\n\r\n\r\n")
        cfg_file.close()
        characters = string.ascii_uppercase + string.digits
        sn = ''.join(random.choice(characters) for i in range(10))
        vswitch_xml = f"""<?xml version="1.0"?>
                    <!-- Copyright (c) 2020 by Cisco Systems, Inc.-->
                    <!-- All rights reserved. -->
                    <!-- Virtual Cat9k configuration information -->
                    <switch>
                    <!-- Virtual Board ID to indicate S1 or Doppler asic simulation -->
                    <board_id>20612</board_id>
                    <!-- Unique Serial# must be provided for each running instance -->
                    <prod_serial_number>9{sn}</prod_serial_number>
                    <!-- Number of ports must appear before other port information -->
                    <port_count>8</port_count>
                    <port lpn="1">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="2">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="3">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="4">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="5">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="6">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="7">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="8">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="9">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="10">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="11">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="12">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="13">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="14">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="15">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    <port lpn="16">
                        <asic_id>0</asic_id>
                        <asic_ifg>0</asic_ifg>
                        <asic_slice>0</asic_slice>
                    </port>
                    </switch>
        """
        switch_file.write(vswitch_xml)
        switch_file.close()

        genisoimage_args = [
            "genisoimage",
            "-l",
            "-o",
            "/" + self.image_name,
            "/vswitch"
        ]


        subprocess.Popen(genisoimage_args)

    def bootstrap_spin(self):
        """This function should be called periodically to do work."""
        # increase waiting time to 1500 seconds
        if self.spins > 1500:
            # too many spins with no result ->  give up
            self.stop()
            self.start()
            return

        (ridx, match, res) = self.tn.expect([b"Press RETURN to get started!"], 1)
        if match:  # got a match!
            if ridx == 0:  # login
                # We skip this in install mode
                # if self.install_mode:
                #     self.running = True
                #     return

                self.logger.debug("matched, Press RETURN to get started.")
                self.wait_write("", wait=None)

                # run main config!
                self.bootstrap_config()
                self.startup_config()
                # skip this for cat9kv
                # self.running = True
                # close telnet connection
                self.tn.close()
                # close monitor connection            
                self.qm.close()
                # eject cdrom to avoid another bootstraping with serial number randomization during IOS-XE reload
                p = subprocess.Popen( "echo 'eject -f ide1-cd0' | socat - tcp:localhost:4000", shell=True)
                # startup time?
                startup_time = datetime.datetime.now() - self.start_time
                self.logger.info("Startup complete in: %s" % startup_time)
                # mark as running
                self.running = True
                return

        # no match, if we saw some output from the router it's probably
        # booting, so let's give it some more time
        if res != b"":
            self.logger.trace("OUTPUT: %s" % res.decode())
            # reset spins if we saw some output
            self.spins = 0

        self.spins += 1

        return

    def bootstrap_config(self):
        """Do the actual bootstrap config"""
        self.logger.info("applying bootstrap configuration")

        self.wait_write("", None)
        self.wait_write("enable", wait=">")
        self.wait_write("configure terminal", wait=">")

        self.wait_write("hostname %s" % (self.hostname))
        self.wait_write(
            "username %s privilege 15 password %s" % (self.username, self.password)
        )
        self.wait_write("ip domain name vrf Mgmt-vrf lab.local")
        self.wait_write("ip domain lookup source-interface GigabitEthernet 0/0")  
        self.wait_write("ip name-server vrf Mgmt-vrf 10.0.0.3")      
        self.wait_write("crypto key generate rsa modulus 4096")
        self.wait_write("ip ssh server algorithm mac hmac-sha2-256-etm hmac-sha2-512-etm hmac-sha2-256 hmac-sha2-512")
        self.wait_write("ip ssh client algorithm mac hmac-sha2-256-etm hmac-sha2-512-etm hmac-sha2-256 hmac-sha2-512")
        self.wait_write("ip scp server enable")
        self.wait_write("ip ssh source-interface gigabitEthernet 0/0")
        self.wait_write("cdp run")
        self.wait_write("lldp run")
        self.wait_write("interface GigabitEthernet0/0")
        self.wait_write("ip address 10.0.0.15 255.255.255.0")
        self.wait_write("no shut")
        self.wait_write("exit")
        self.wait_write("ip route vrf Mgmt-vrf 0.0.0.0 0.0.0.0 10.0.0.2")
        self.wait_write("restconf")
        self.wait_write("netconf-yang")
        self.wait_write("snmp-server community C1sco12345 RW")
        self.wait_write("line vty 0 15")
        self.wait_write("login local")
        self.wait_write("transport input ssh")
        self.wait_write("end")
        # Delete the initial bootstrap config file in flash which was mounted through config.iso in cdrom during the first bootup
        self.wait_write("delete bootflash:iosxe_config.txt")
        self.wait_write("\r\r", wait="]?")
        self.wait_write("\r\r", wait="[confirm]")
        self.wait_write("wr")
        self.wait_write("\r\r")
    def startup_config(self):
        """Load additional config provided by user."""

        if not os.path.exists(STARTUP_CONFIG_FILE):
            self.logger.trace(f"Startup config file {STARTUP_CONFIG_FILE} is not found")
            return

        self.logger.trace(f"Startup config file {STARTUP_CONFIG_FILE} exists")
        with open(STARTUP_CONFIG_FILE) as file:
            config_lines = file.readlines()
            config_lines = [line.rstrip() for line in config_lines]
            self.logger.trace(f"Parsed startup config file {STARTUP_CONFIG_FILE}")

        self.logger.info(f"Writing lines from {STARTUP_CONFIG_FILE}")

        self.wait_write("configure terminal")
        # Apply lines from file
        for line in config_lines:
            self.wait_write(line)
        # End and Save
        self.wait_write("end")
        self.wait_write("wr")
        self.wait_write("\r\r")


class CAT9KV(vrnetlab.VR):
    def __init__(self, hostname, username, password, nics, conn_mode):
        super(CAT9KV, self).__init__(username, password)
        self.vms = [CAT9KV_vm(hostname, username, password, nics, conn_mode)]


class CAT9KV_installer(CAT9KV):
    """CAT9KV installer

    Will start the CAT9KV with a mounted iso to make sure that we get
    console output on serial, not vga.
    """

    def __init__(self, hostname, username, password, nics, conn_mode):
        super(CAT9KV, self).__init__(username, password)
        self.vms = [
            CAT9KV_vm(
                hostname,
                username,
                password,
                nics,
                conn_mode,
                install_mode=True,
            )
        ]
    # We will skip the typical install process like csr since we want a clean VM to bootstrap with randomized serial number. Leave this function here as placeholder for future change.
    def install(self):
        self.logger.info("Installing CAT9KV")
        # CAT9KV = self.vms[0]
        # while not CAT9KV.running:
        #     CAT9KV.work()
        # time.sleep(30)
        # CAT9KV.stop()
        self.logger.info("Installation complete")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--trace", action="store_true", help="enable trace level logging"
    )
    parser.add_argument("--username", default="vrnetlab", help="Username")
    parser.add_argument("--password", default="VR-netlab9", help="Password")
    parser.add_argument("--install", action="store_true", help="Install CAT9KV")
    parser.add_argument("--hostname", default="CAT9KV", help="Switch Hostname")
    parser.add_argument("--nics", type=int, default=9, help="Number of NICS")
    parser.add_argument(
        "--connection-mode",
        default="vrxcon",
        help="Connection mode to use in the datapath",
    )
    args = parser.parse_args()

    LOG_FORMAT = "%(asctime)s: %(module)-10s %(levelname)-8s %(message)s"
    logging.basicConfig(format=LOG_FORMAT)
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    if args.trace:
        logger.setLevel(1)

    if args.install:
        vr = CAT9KV_installer(
            args.hostname,
            args.username,
            args.password,
            args.nics,
            args.connection_mode,
        )
        vr.install()
    else:
        vr = CAT9KV(
            args.hostname,
            args.username,
            args.password,
            args.nics,
            args.connection_mode,
        )
        vr.start()
