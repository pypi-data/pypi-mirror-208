import click

from .loader import create_device


def serv(device, port=5000, host="localhost"):
    from flask import Flask, request
    app = Flask(__name__)

    @app.route("/<key>", methods=["GET", "POST"])
    def get_set(key):
        if request.method == "GET":
            return device.get(key)
        else:
            device.set(key, request.get_json())
            return ""

    @app.route("/reopen", methods=["POST"])
    def reopen():
        device.close()
        device.open()
        device.reset()
        return ""

    app.run(host=host, port=port)


@click.command()
@click.argument("driver_name")
@click.argument("address")
@click.option("--host", default="localhost")
@click.option("--port", default=5000)
def cli(driver_name: str, address: str, host: str, port: int):
    dev = create_device(driver_name, address)
    serv(dev, port, host)


if __name__ == "__main__":
    cli()
