from .captor import MyApp as cap
import click


@click.command(context_settings={"strict": True})
@click.option('-p', '--port', default='8083', help='设置端口号')
def main(port):
    cap.run(port)


if __name__ == '__main__':
    main()
