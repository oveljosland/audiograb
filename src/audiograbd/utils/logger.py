import logging
from pathlib import Path

LOG = Path("/tmp/audiograb.log")
LVL = "INFO"
FMT = "%(asctime)s %(name)s %(levelname)s %(message)s"


def parse_level(level):
	if isinstance(level, int):
		return level
	if not isinstance(level, str):
		return logging.INFO

	numeric_level = getattr(logging, level.upper(), None)
	if isinstance(numeric_level, int):
		return numeric_level

	logging.warning(
		"Invalid logger level '%s'; falling back to INFO",
		level,
	)
	return logging.INFO


def configure_logging(config=None, file: Path | str | None = None):
	"""Configure root logging handlers and format from config.
	If no config is provided, a default console/file logger is used.
	"""
	logger_config = {}
	if isinstance(config, dict):
		logger_config = config.get("logger", {}) or {}

	level = parse_level(logger_config.get("level", LVL))
	fmt = logger_config.get("format", FMT)
	root_logger = logging.getLogger()
	root_logger.setLevel(level)
	formatter = logging.Formatter(fmt)

	# replace existing handlers so reconfiguration doesn't duplicate output
	for handler in list(root_logger.handlers):
		root_logger.removeHandler(handler)

	console_handler = logging.StreamHandler()
	console_handler.setLevel(level)
	console_handler.setFormatter(formatter)

	file_handler = logging.FileHandler(str(file or LOG), mode="a")
	file_handler.setLevel(level)
	file_handler.setFormatter(formatter)

	root_logger.addHandler(console_handler)
	root_logger.addHandler(file_handler)
	root_logger.debug("Logging configured: level=%s format=%s", level, fmt)
