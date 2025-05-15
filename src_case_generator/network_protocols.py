def single_router_network(os_name: str, resources_config: dict, nic: str) -> (str, dict):
    return 'Single', {
        'nodes': {
            'Client 1': {
                'type': 'guest',
                'vcpu': 1,
                'ram': 1024,
                'ip': '10.0.1.2'
            },
            'Server 1': {
                'type': 'guest',
                'vcpu': 1,
                'ram': 1024,
                'ip': '10.0.2.2'
            },
            'Router 1': {
                'type': 'router',
                **resources_config,
                'os': os_name,
                'nic': nic,
                'adapters': 6,
                'ips': [
                    {'adapter': 3, 'ip': '10.0.1.1/24'},
                    {'adapter': 4, 'ip': '10.0.2.1/24'}
                ],
                'routes': {
                    'static': [],
                    'RIP': [],
                    'OSPF': [],
                    'BGP': [],
                    'MPLS': []
                }
            }
        },
        'links': [
            {'node_a': 'Client 1', 'adapter_a': 0, 'node_b': 'Router 1', 'adapter_b': 3},
            {'node_a': 'Server 1', 'adapter_a': 0, 'node_b': 'Router 1', 'adapter_b': 4}
        ]
    }

def dual_router_network(
        os_name: str,
        resources_config: dict,
        nic: str,
        static_routes: list[list[dict]] = [],
        rip_routes: list[dict[str, list[str]]] = [],
        ospf_routes: list[list[dict]] = [],
        bgp_routes: list[list[dict]] = [],
        mpls_routes: list[list[dict]] = []
    ) -> (str, dict):

    return 'Dual', {
        'nodes': {
            'Client 1': {
                'type': 'guest',
                'vcpu': 1,
                'ram': 1024,
                'ip': '10.0.1.2'
            },
            'Server 1': {
                'type': 'guest',
                'vcpu': 1,
                'ram': 1024,
                'ip': '10.0.3.2'
            },
            'Router 1': {
                'type': 'router',
                **resources_config,
                'os': os_name,
                'nic': nic,
                'adapters': 6,
                'ips': [
                    {'adapter': 3, 'ip': '10.0.1.1/24'},
                    {'adapter': 4, 'ip': '10.0.2.1/24'}
                ],
                'routes': {
                    'static': static_routes[0] if len(static_routes) > 0 else static_routes,
                    'RIP': rip_routes[0] if len(rip_routes) > 0 else rip_routes,
                    'OSPF': ospf_routes[0] if len(ospf_routes) > 0 else ospf_routes,
                    'BGP': bgp_routes[0] if len(bgp_routes) > 0 else bgp_routes,
                    'MPLS': mpls_routes[0] if len(mpls_routes) > 0 else mpls_routes,
                }
            },
            'Router 2': {
                'type': 'router',
                **resources_config,
                'os': os_name,
                'nic': nic,
                'adapters': 6,
                'ips': [
                    {'adapter': 4, 'ip': '10.0.2.2/24'},
                    {'adapter': 3, 'ip': '10.0.3.1/24'}
                ],
                'routes': {
                    'static': static_routes[1] if len(static_routes) > 1 else static_routes,
                    'RIP': rip_routes[1] if len(rip_routes) > 1 else rip_routes,
                    'OSPF': ospf_routes[1] if len(ospf_routes) > 1 else ospf_routes,
                    'BGP': bgp_routes[1] if len(bgp_routes) > 1 else bgp_routes,
                    'MPLS': mpls_routes[1] if len(mpls_routes) > 1 else mpls_routes,
                }
            }
        },
        'links': [
            {'node_a': 'Client 1', 'adapter_a': 0, 'node_b': 'Router 1', 'adapter_b': 3},
            {'node_a': 'Router 1', 'adapter_a': 4, 'node_b': 'Router 2', 'adapter_b': 4},
            {'node_a': 'Server 1', 'adapter_a': 0, 'node_b': 'Router 2', 'adapter_b': 3},
        ]
    }

def static_routes(os_name: str, resources_config: dict, nic: str) -> (str, dict):
    return dual_router_network(
        os_name=os_name,
        resources_config=resources_config,
        nic=nic,
        static_routes=[
            [
                { 'distant_network': '10.0.3.0/24', 'via': '10.0.2.2' }
            ],
            [
                { 'distant_network': '10.0.1.0/24', 'via': '10.0.2.1' }
            ]
        ]
    )

def rip_routes(os_name: str, resources_config: dict, nic: str) -> (str, dict):
    return dual_router_network(
        os_name=os_name,
        resources_config=resources_config,
        nic=nic,
        rip_routes=[
            {
                'enable_interfaces': [3, 4],
                'add_networks': ['10.0.1.0/24', '10.0.2.0/24'],
            },
            {
                'enable_interfaces': [3, 4],
                'add_networks': ['10.0.3.0/24', '10.0.2.0/24']
            }
        ]
    )

def ospf_routes(os_name: str, resources_config: dict, nic: str) -> (str, dict):
    return dual_router_network(
        os_name=os_name,
        resources_config=resources_config,
        nic=nic,
        ospf_routes=[]
    )

def bgp_routes(os_name: str, resources_config: dict, nic: str) -> (str, dict):
    return dual_router_network(
        os_name=os_name,
        resources_config=resources_config,
        nic=nic,
        bgp_routes=[]
    )

def mpls_routes(os_name: str, resources_config: dict, nic: str) -> (str, dict):
    return dual_router_network(
        os_name=os_name,
        resources_config=resources_config,
        nic=nic,
        mpls_routes=[]
    )

protocols = {
    'static-single': [single_router_network],
    'static-dual': [static_routes],
    'RIP': [rip_routes],
    'OSPF': [ospf_routes],
    'BGP': [bgp_routes],
    'MPLS': [mpls_routes]
}