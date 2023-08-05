from signal import signal, SIGINT
from sys import exit, \
                version_info as py_version_info
import argparse
from traceroute.traceroute import trace_udp, trace_icmp


def main() -> int:
    import logging
    logging.getLogger("scapy").setLevel(logging.WARNING)

    epilog = """See also RFC2151 section 3.4 for a quick
                read-up on traceroute."""
    parser = argparse.ArgumentParser(
                    prog='traceroute',
                    description="""Provides a mostly *NIX-traceroute-
                    like -- but very basic -- tracert/traceroute IPv4
                    alternative built on scapy.""",
                    epilog=epilog)
    parser.add_argument('remote_host', metavar='host', \
        help="""IP address or host name of the remote host
                which is the destination of the route.""")
    parser.add_argument('packet_length', metavar='packet_length', \
        nargs='?', default=2, \
        help="""size of the UDP packet to be sent.
                Note that this option has no effect in ICMP
                mode.""")
    parser.add_argument('-m', '--maxttl', '--max-hops', \
                        default=30, \
        help="""maximum allowable TTL value, measured as
                the number of hops allowed before the
                program terminates.
                (default = 30)""")
    parser.add_argument('-f', '--minttl', '--first', \
                        default=1, \
        help="""minimum TTL value, measured as the number
                of hops at which to start.
                (default = 1)""")
    parser.add_argument('-q', '--fleetsize', \
                        default=3, \
        help="""number of packets that will be sent
                with each time-to-live setting ("fleet size").
                (default = 3)""")
    parser.add_argument('-w', '--timeout', \
                        default=5, \
        help="""amount of time, in seconds, to wait for
                an answer from a particular router before
                giving up.
                (default = 5)""")
    parser.add_argument('-p', '-P', '--port', \
                        default=33434, \
        help="""destination port (invalid) at the remote
                host.
                Note that this option will have no effect in
                ICMP mode.
                (default = 33434)""")
    parser.add_argument('-s', '--source', \
                        default=None, \
        help="""source address of outgoing packets.
                (default is address of adapter used)""")
    parser.add_argument('-M', '--module', \
                        default='UDP', choices=['UDP', 'ICMP'], \
        help="""module (or method) for traceroute
                operations.
                (default = UDP)""")
    parser.add_argument('-j', '--udp-junk', default='42', \
                        choices=['42', 'zeros', '00', 'loremipsum', 'asc'],
        help="""contents of the to-be-sent UDP segments in UDP mode.
                It has no further purpose than adding weight to the 
                segments, but there are several available.""")
    parser.add_argument('-i', '--no-ip-id-variation', \
                        action='store_const', \
                        const=True, default=False, \
        help="""do *not* vary the IP segment 
                'Identification' field.""")
    parser.add_argument('--no-legacy-python-notice', \
                        dest='show_legacy_py_notice', \
                        action='store_const', \
                        const=False, default=True, \
        help="""disables the legacy python version notice.""")
    args = parser.parse_args()
    
    # TODO: make id vary by default and add switch to turn it off
    
    if args.show_legacy_py_notice and py_version_info <= (3, 9):
        print()
        print()
        print("NOTE: This software runs best under Python 3.9 and later.")
        print("      It is currently running on Python " + \
            str(py_version_info.major) + "." + str(py_version_info.minor) + ".")
        print("      The program can still be executed, but it might show some" \
            "\n      strange behaviour.")
        input("  Press any key to continue.")
        print("--- CONTINUING")
        print()

    try:
        # this once was a match statement, but not any more 
        # since the language downgrade
        if args.module == 'UDP':
            print()
            trace_udp(args.remote_host,
                    udp_length=int(args.packet_length),
                    min_ttl=int(args.minttl),
                    max_ttl=int(args.maxttl),
                    num_per_fleet=int(args.fleetsize),
                    timeout=int(args.timeout),
                    port=int(args.port),
                    udp_content=args.udp_junk,
                    source=args.source,
                    ip_id_variation=(not args.no_ip_id_variation))
        elif args.module == 'ICMP':
            print("Note: ICMP mode is experimental.")
            print()
            trace_icmp(args.remote_host,
                    min_ttl=int(args.minttl),
                    max_ttl=int(args.maxttl),
                    num_per_fleet=int(args.fleetsize),
                    timeout=int(args.timeout),
                    source=args.source,
                    ip_id_variation=(not args.no_ip_id_variation))
        else:
            print('Module ' + args.module + ' is not supported.')
        return 0
    except PermissionError:
        print("Error: Please run this program with higher privileges.")
        exit(1)

def term_handler(signal_received, frame) -> None:
    print()
    print("-- Cancelled by signal " + str(signal_received) + ".")
    exit(-1)

try:
    # this sometimes makes problems on windows
    signal(SIGINT, term_handler)
    #signal(SIGKILL, term_handler)
    #signal(SIGABRT, term_handler)
    #signal(SIGTERM, term_handler)
except ImportError:
    pass

if __name__ == '__main__':
    main()
