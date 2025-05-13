from typing import Optional

def preformat_custom_command(
        command: str,
        ip_address: Optional[str] = None,
        distant_network: Optional[str] = None,
        gateway: Optional[str] = None,
        interface_prefix: Optional[str] = None,
        interface: Optional[int] = None,
        router_id: Optional[str] = None,
        instance_name: Optional[str] = None,
        area_name: Optional[str] = None,
    ) -> str:
    return (command
        .replace('{IP_ADDRESS}', ip_address if ip_address is not None else '')
        .replace('{DISTANT_NETWORK}', distant_network if distant_network is not None else '')
        .replace('{GATEWAY}', gateway if gateway is not None else '')
        .replace('{INTERFACE_PREFIX}', interface_prefix if interface_prefix is not None else '')
        .replace('{INTERFACE}', str(interface)  if interface is not None else '')
        .replace('{ROUTER_ID}', router_id  if router_id is not None else '')
        .replace('{INSTANCE_NAME}', instance_name  if instance_name is not None else '')
        .replace('{AREA_NAME}', area_name if area_name is not None else '')
    ) + '\r'