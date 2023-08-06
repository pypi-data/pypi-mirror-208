import argparse

parser = argparse.ArgumentParser(
    prog='Run SciCom Simulations',
    description='This script starts the server interfaces for the different ABM.',
    epilog='During the running of this script, the interfaces should be reachable at http://127.0.0.1:8521'
)

parser.add_argument('simulation', choices=["randomletters", "historicalletters"])


args = parser.parse_args()

if args.simulation == "randomletters":
    from randomletters.server import server
    server.launch()


elif args.simulation == "historicalletters":
    from historicalletters.server import server
    server.launch()
