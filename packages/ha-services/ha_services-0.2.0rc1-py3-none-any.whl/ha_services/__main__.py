"""
    Allow ha_services to be executable
    through `python -m ha_services`.
"""


from ha_services.cli import cli_app


def main():
    cli_app.main()


if __name__ == '__main__':
    main()
