import json
import os
import time
from logging import Logger
from typing import Dict

from mininet.clean import cleanup
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import Node

from qemu_host import QEMUHost


class RouterThroughputTester:
    def __init__(self, name: str, router_image: str, config: str, guest_image: str, run_number: int, logger: Logger):
        """
        Initialize the throughput tester for a specific router OS.

        :param name: Name of the router OS to be tested
        :param router_image: Path to the router OS disk image
        :param config: Network configuration
        :param run_number: Run number of the test
        :param logger: Logger instance
        """
        self.name = name
        self.router_image = router_image
        self.config = config
        self.guest_image = guest_image
        self.run_number = run_number
        self.logger = logger

    def configure_router(self, router: Node):
        """
        Configure router-specific network settings.

        :param router: Mininet Node representing the router
        """

        # iproute2, freebsd, redox
        if self.config == 'unix':
            router.cmd('ip link set dev eth0 up')
            router.cmd('ip link set dev eth1 up')
            router.cmd('ip addr add 10.0.2.1/24 dev router-eth1')
            router.cmd('ip route add 10.0.1.0/24 via 10.0.2.1 dev router-eth0')
            router.cmd('ip route add 10.0.2.0/24 via 10.0.1.1 dev router-eth1')
            router.cmd('sysctl -w net.ipv4.ip_forward=1')
        else:
            router.cmd(self.config)

    def run_iperf_test(self, client: Node, server: Node, duration: int) -> Dict[str, float]:
        """
        Run iPerf3 throughput test between client and server.

        :param client: Mininet Node representing the client
        :param server: Mininet Node representing the server
        :param duration: Test duration in seconds
        :return: Dictionary with throughput results
        """
        results = {}

        # Start iPerf3 server
        server.cmd(f'iperf3 --server --interval 1 --daemon')
        self.logger.debug("iPerf3 server launching...")

        # Give server time to start
        time.sleep(2)
        self.logger.debug("iPerf3 launched")

        # Run iPerf3 client test
        self.logger.debug("Starting iPerf3 test...")
        client_output = client.cmd(f'iperf3 --client {server.IP()} --udp --time {duration} --interval 1 --json')

        # Saving result
        directory_path = f'results/{self.name}'
        os.makedirs(directory_path, exist_ok=True)
        path = f'{directory_path}/{self.name}_run_{self.run_number}.json'

        with open(path, 'w') as f:
            f.write(client_output)

        self.logger.debug(f'Output wrote in file "{path}"')

        # Parse JSON output
        try:
            raw_result = json.loads(client_output)
            throughput_mbps = raw_result['end']['sum']['bits_per_second'] / 1_000_000
            results = {
                'throughput_mbps': throughput_mbps,
                'jitter_ms': raw_result['end']['streams'][0]['udp']['jitter_ms'],
                'lost_percent': raw_result['end']['streams'][0]['udp']['lost_percent']
            }
        except Exception as e:
            self.logger.error(f"Error parsing iPerf3 results: {e}\n")
        finally:
            # Cleanup server
            server.cmd('pkill iperf3')

            return results

    def create_topology(self) -> Mininet:
        """
        Create Mininet topology with client, router, and server.

        :return: Mininet
        """
        # Create network
        net = Mininet(host=QEMUHost, controller=None, waitConnected=True)

        # Add topology
        client: QEMUHost = net.addHost('client', ip='10.0.1.2/24', os_image=self.guest_image)
        router: QEMUHost = net.addHost('router', ip='10.0.1.1/24', os_image=self.router_image)
        server: QEMUHost = net.addHost('server', ip='10.0.2.2/24', os_image=self.guest_image)

        # Connect nodes
        net.addLink(client, router, intfName1='client-eth0', intfName2='router-eth0')
        net.addLink(server, router, intfName1='server-eth0', intfName2='router-eth1')
        net.start()

        # Configure router
        self.configure_router(router)

        # Configure routing
        client.cmd('ip route add default via 10.0.1.1')
        server.cmd('ip route add default via 10.0.2.1')

        return net

    def run_test(self, duration: int, access_cli: bool) -> dict:
        """
        Execute complete throughput test.

        :param access_cli:
        :param duration: iPerf3 test duration
        :return: Test results dictionary
        """
        results = {}
        net = self.create_topology()

        client: QEMUHost = net.getNodeByName('client')
        server: QEMUHost = net.getNodeByName('server')

        try:
            # Log router type and image
            self.logger.info(f"Testing Router: {self.name}")
            self.logger.info(f"Router Image: {self.router_image}")

            if access_cli:
                CLI(net)

            # Run throughput test
            results = self.run_iperf_test(client, server, duration)

        except Exception as e:
            self.logger.error(f"Test failed: {e}")

        finally:
            net.stop()
            cleanup()
            return results
