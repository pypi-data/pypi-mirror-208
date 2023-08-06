from .viewm2m import MyApp as m2m
import click


@click.command(context_settings={"strict": True})
@click.option('-p', '--port', default='8083', help='设置端口号')
def main(port):
    m2m.run(port)


if __name__ == '__main__':
    main()
