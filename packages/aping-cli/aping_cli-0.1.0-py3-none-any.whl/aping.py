import argparse
import time
from dataclasses import dataclass
from typing import Dict, List, NoReturn, Optional, Union

from multiping import MultiPing
from prometheus_client import Gauge, start_http_server

DEFAULT_PING_TIMEOUT_SECONDS = 2
DEFAULT_PROMETHEUS_METRICS_SERVER_PORT = 8000

PING_LATENCY_SECONDS = Gauge("ping_latency_seconds", "Latency (gauge)", ["target"])


def ping(targets: List[str], timeout_seconds: int = 1) -> Dict[str, float]:
    mp = MultiPing(targets)
    resolved_targets = mp._dest_addrs
    target_by_resolved_target = dict(zip(resolved_targets, targets))

    mp.send()
    responses, no_responses = mp.receive(timeout_seconds)

    res = {
        target_by_resolved_target[resolved_target]: response_time_seconds
        for resolved_target, response_time_seconds in responses.items()
    }
    res.update({target_by_resolved_target[resolved_target]: None for resolved_target in no_responses})

    return res


def format_response_time(response_time: Union[float, None], timeout: int) -> str:
    if response_time is None:
        return f">{timeout}s"
    else:
        ms = round(response_time * 1000, 2)
        return f"{ms:0.2f}ms"


@dataclass(frozen=True)
class Input:
    targets: Dict[str, str]
    timeout: int
    port: int


def parse_args(cli_args: Optional[List[str]] = None) -> Input:
    p = argparse.ArgumentParser(
        description="Ping multiple targets and export results as Prometheus metrics.",
    )
    p.add_argument(
        "targets",
        nargs="+",
        metavar="target",
        help="A target to ping, in the form 'name=ip_address' (e.g., 'google-dns=8.8.8.8')",
    )
    p.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=DEFAULT_PING_TIMEOUT_SECONDS,
        help=f"Maximum ping-completion time in seconds (default: {DEFAULT_PING_TIMEOUT_SECONDS})",
    )
    p.add_argument(
        "-p",
        "--port",
        type=int,
        default=DEFAULT_PROMETHEUS_METRICS_SERVER_PORT,
        help=f"Prometheus metric server port (default: {DEFAULT_PROMETHEUS_METRICS_SERVER_PORT})",
    )
    args = p.parse_args(args=cli_args)

    targets = {}
    for s in args.targets:
        name, address = s.split("=", 1)
        targets[name.strip()] = address.strip()

    return Input(targets, args.timeout, args.port)


def main() -> NoReturn:
    args = parse_args()

    start_http_server(args.port)
    print(f"Prometheus metrics server available at http://127.0.0.1:{args.port}", flush=True)

    name_by_target = {target: name for name, target in args.targets.items()}
    targets = sorted(args.targets.values())

    while True:
        res = ping(targets, timeout_seconds=args.timeout)
        res_by_full_name = {
            f"{name_by_target[target]} ({target})": response_time for target, response_time in res.items()
        }

        for full_name, response_time in res_by_full_name.items():
            value = response_time or args.timeout
            PING_LATENCY_SECONDS.labels(full_name).set(value)

        details = [
            f"{full_name}: {format_response_time(res_by_full_name[full_name], args.timeout)}"
            for full_name in sorted(res_by_full_name.keys())
        ]
        print(", ".join(details), flush=True)

        time.sleep(1)


if __name__ == "__main__":
    main()
