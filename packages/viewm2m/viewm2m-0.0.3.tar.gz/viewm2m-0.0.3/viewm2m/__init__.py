from .captor import MyApp as cap
from .viewm2m import MyApp as m2m
import click


@click.command()
@click.option('-r', '--repeat', default=False, help='是否允许重复')
@click.option('-p', '--port', default='8083', help='设置端口号')
def main(repeat, port):
    if repeat:
        cap.run()
    else:
        m2m.run()


if __name__ == '__main__':
    main()