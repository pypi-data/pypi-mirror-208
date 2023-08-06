
import argparse
from .service import app

parser = argparse.ArgumentParser(usage="Manager project, can create git , sync , encrypt your repo")
parser.add_argument("-p","--port",default=9292,type=int,help="set server port")
parser.add_argument("-i","--ip",default="0.0.0.0",type=str,help="set server port")


def main():
    args = parser.parse_args()
    app.run(host=args.ip, port=args.port)    

if __name__ == "__main__":
    main()
