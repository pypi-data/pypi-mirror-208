from .captor import MyApp as cap
from .viewm2m import MyApp as m2m
import click


@click.command(context_settings={"strict": True})
@click.option('-r', '--repeat', default=False,type=click.BOOL, help='是否允许重复')
@click.option('-p', '--port', default='8083', help='设置端口号')
def main(repeat, port):
    print(repeat+port)
    if repeat:
        cap.run(port)
    elif not repeat:
        m2m.run(port)


if __name__ == '__main__':
    main()
