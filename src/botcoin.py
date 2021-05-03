#!/usr/bin/env python
'''Interface between user and the trader bot.'''
import argparse
import sys
from types import SimpleNamespace
from pathlib import Path
from colorama import init, Fore

from reader import read
from manager import Manager


def parse_args(args):
    '''This is required to test arguments.'''
    parser = argparse.ArgumentParser(description='Automate crypto trades.')
    parser.add_argument(
        '--init',
        default=None,
        help='YAML file that stores all configuration, if this file is presented, following arguments are ignored.'
    )

    parser.add_argument(
        '--id',
        default=None,
        help='session id, specify last if you want to use the lattest id used.'
    )

    parser.add_argument(
        '--strat',
        default='MACD',
        help='strategy used for trading (Default = MACD). Available: MACD.'
    )

    parser.add_argument(
        '--name',
        default=None,
        help='define strat name so it can use previous data.'
    )

    parser.add_argument(
        '--interval',
        default=1,
        type=int,
        help='define interval of strategy data in minutues (Default = 1). Min: 1.'
    )

    parser.add_argument(
        '--pair',
        default='XRPUSDT',
        help='pair of cryptos used for trading. Example: XRPUSDT, BTCUSDT...'
    )

    parser.add_argument(
        '--tokens',
        default=None,
        help='binance REST API key and secret. Format: api_key#api_secret'
    )

    return parser.parse_args(args)


def from_args_to_config(args):
    '''Prepare arguments to fit config namespace'''
    config = SimpleNamespace()
    config.id = args.id

    strat = {
        'strat': args.strat,
        'tokens': {
            'binance_api_key': args.tokens.split('#')[0],
            'binance_api_secret': args.tokens.split('#')[1]
        },
        'name': args.name,
        'interval': args.interval,
        'pair': args.pair
    }
    config.strategies = []
    config.strategies.append(strat)

    return config


def main():
    '''Initialize bot based on user arguments.'''
    init(autoreset=True)
    args = parse_args(sys.argv[1:])

    config = None
    if args.init:
        # There is a config file
        config = read(args.init)
        if config.error:
            print(f'{Fore.RED}Found errors during init file processing, error: {config.error}. Exiting...')
            sys.exit()
    elif not args.tokens:
        # There is no config file and missing tokens
        print(f'{Fore.RED}Tokens required!')
        sys.exit()
    else:
        # No config file + required tokens
        config = from_args_to_config(args)

    # pylint: disable=W0612
    manager = Manager(STORAGE_DIR, config)


STORAGE_DIR = Path('../storage')

if __name__ == '__main__':
    main()
