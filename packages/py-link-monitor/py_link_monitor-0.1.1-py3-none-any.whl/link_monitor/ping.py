from pingparsing import PingParsing, PingTransmitter, PingStats


def ping(address: str, source: str = None, timeout: int = 2, deadline: int = 2, count: int = 1) -> PingStats:
    transmitter = PingTransmitter()
    transmitter.destination = address
    transmitter.count = count
    transmitter.timeout = f'{timeout}s'
    transmitter.deadline = f'{deadline}s'
    transmitter.interface = source

    result = transmitter.ping()
    return PingParsing().parse(result)


def is_alive(address: str, source: str = None):
    return ping(address, source=source).packet_loss_count == 0
