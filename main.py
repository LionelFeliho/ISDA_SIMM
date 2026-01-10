import logging

import pandas as pd

from src.agg_margins import SIMM


LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Run a SIMM calculation from the sample CRIF file."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    path = "CRIF/"
    LOGGER.info("Loading CRIF data from %s", path)
    crif = pd.read_csv(f"{path}crif.csv", header=0)
    portfolio1 = SIMM(crif, "USD", 1)

    # Total SIMM
    LOGGER.info("Total SIMM: %s", portfolio1.simm)
    print(portfolio1.simm)

    # SIMM Break Down
    LOGGER.info("SIMM breakdown calculated.")
    print(portfolio1.simm_break_down)


if __name__ == '__main__':
    main()
