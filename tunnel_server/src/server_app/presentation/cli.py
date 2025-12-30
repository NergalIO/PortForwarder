"""CLI argument parser."""

import argparse
from dataclasses import dataclass


@dataclass
class ServerConfig:
    """Server configuration."""
    bind: str
    control_port: int
    port_min: int
    port_max: int
    token: str


def parse_args() -> ServerConfig:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Tunnel server")
    parser.add_argument(
        '--bind',
        default='0.0.0.0',
        help='Bind address (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--control',
        type=int,
        default=7000,
        help='Control port (default: 7000)'
    )
    parser.add_argument(
        '--port-min',
        type=int,
        default=10000,
        help='Minimum public port (default: 10000)'
    )
    parser.add_argument(
        '--port-max',
        type=int,
        default=11000,
        help='Maximum public port (default: 11000)'
    )
    parser.add_argument(
        '--token',
        required=True,
        help='Authentication token'
    )
    
    args = parser.parse_args()
    
    if args.port_min > args.port_max:
        parser.error("--port-min must be <= --port-max")
    
    return ServerConfig(
        bind=args.bind,
        control_port=args.control,
        port_min=args.port_min,
        port_max=args.port_max,
        token=args.token
    )

