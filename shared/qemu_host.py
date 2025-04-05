import os

from mininet.node import Host
from mininet.util import quietRun


class QEMUHost(Host):
    """
    Custom QEMU-based host
    """

    def __init__(self, name, os_image, **kwargs):
        """
        Initialize QEMU-based virtual host

        Args:
            name (str): Hostname
            os_image (str): Path to QEMU disk image
            **kwargs: Additional host configuration
        """
        self.os_image = os_image
        self.qemu_pid = None
        super().__init__(name, **kwargs)

    def start(self):
        """
        Start QEMU instance for the host
        """
        # Network interface configurations
        tap_intf = f'{self.name}-eth0'

        # Create TAP interface
        quietRun(f'ip tun del {tap_intf}')
        quietRun(f'ip tuntap add {tap_intf} mode tap')
        quietRun(f'ip link set {tap_intf} up')

        # Start QEMU instance
        qemu_cmd = f"""qemu-system-x86_64 \
            -m 2G \
            -drive file={self.os_image},format=raw,id=d0,if=none,bus=0,unit=0 \
            -device ide-hd,drive=d0,bus=ide.0 \
            -net nic \
            -net tap,ifname={tap_intf},script=no,downscript=no \
            -display none \
            -daemonize \
            -enable-kvm
        """
        # ,if=virtio

        self.qemu_pid = int(quietRun(qemu_cmd + ' -pidfile /tmp/qemu.pid').strip())

    def stop(self, **kwargs):
        """
        Stop QEMU instance
        """
        if self.qemu_pid:
            # SIGTERM
            os.kill(self.qemu_pid, 15)
        quietRun(f'ip link del {self.name}-eth0')


"""
def create_multi_os_network():
    net = Mininet(host=QEMUHost, switch=OVSSwitch)

    # Create nodes with different OS disk images
    client = net.addHost('client', disk_image='/path/to/debian-client.qcow2')

    router = net.addHost('router', disk_image='/path/to/ubuntu-router.qcow2')

    server = net.addHost('server', disk_image='/path/to/alpine-server.qcow2')

    # Add switches and links
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    # Connect nodes
    net.addLink(client, s1)
    net.addLink(router, s1)
    net.addLink(router, s2)
    net.addLink(server, s2)

    # Start network
    net.start()

    # Perform any additional network configuration
    # (Actual configuration would depend on your specific disk images)

    return net


def main():
    net = create_multi_os_network()
    net.interact()
    net.stop()
"""