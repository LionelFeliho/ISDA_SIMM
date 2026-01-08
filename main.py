import logging
from pathlib import Path

import pandas as pd

from src.agg_margins import SIMM
from src.config import load_config


def configure_logging() -> None:
    """Configure root logging for the CLI entrypoint."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def main() -> None:
    """Run a SIMM calculation using the configured defaults."""
    configure_logging()
    logger = logging.getLogger(__name__)

    config = load_config()
    defaults = config["defaults"]
    crif_path = Path(defaults["crif_path"])

    logger.info("Loading CRIF file from %s", crif_path)
    crif = pd.read_csv(crif_path, header=0)

    portfolio = SIMM(
        crif,
        defaults["calculation_currency"],
        float(defaults["exchange_rate"]),
    )

    logger.info("SIMM total: %s", portfolio.simm)
    logger.info("SIMM breakdown:\n%s", portfolio.simm_break_down)

    print(portfolio.simm)
    print(portfolio.simm_break_down)


if __name__ == "__main__":
    main()
