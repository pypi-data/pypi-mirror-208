import logging

from map_apply.cli import get_args
from map_apply.main import map_apply

logger = logging.getLogger(__name__)


def main():

    args = get_args()
    logger.info(map_apply(args.input,
                          args.map,
                          args.separator))


if __name__ == "__main__":
    main()
