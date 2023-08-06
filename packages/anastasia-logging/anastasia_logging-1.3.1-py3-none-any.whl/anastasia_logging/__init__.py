"""
Anastasia Logging Standarization

This package holds a logging implementation wrapper for python scripts with standarized code notifications and additional features.

How to use
----------

To use, you can simply replace
```
import logging
```
with
```
import anastasia_logging as logging
```
and log away, no additional changes are required if your scripts already has logging implemented!

You can use additional containerized loggers by calling AnastasiaLogger class

```
from anastasia_logging import AnastasiaLogger
logger = AnastasiaLogger()
```

"""

from typing import Optional
from .logger import AnastasiaLogger

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

# Equivalent to RootLogger from logging but doesn't override it
anastasia_logger = AnastasiaLogger()

def basicConfig(tag: Optional[str] = None, level: Optional[int]=None, save_log: Optional[bool] = None, log_path: Optional[str]=None, **kwargs) -> None:
    """
    Do basic configuration for root Anastasia logging, similar to logging base root function.

    Attributes
    ----------

    tag : Optional[str], default='ANASTASIA-JOB'
            Tag identification for job type for StreamHandlers (console) and FileHandlers (file)

    level : Optional[str], default='INFO'
        Define severity hierarchy for log generation

    save_log : Optional[bool], default=False
        Generate .log file containing logs generated

    log_path : Optional[str], default='anastasia-log.log'
        Define a custom name for log file, if none then it will be called anastasia-logs.log and will be saved in root workdir

    """
    from logging import Formatter, FileHandler, StreamHandler

    # Catch existing parameters if not declared
    if isinstance(tag, type(None)):
        tag = anastasia_logger.tag
    if isinstance(level, type(None)):
        level = anastasia_logger.level
    if isinstance(save_log, type(None)):
        save_log = anastasia_logger.save_log
    if isinstance(log_path, type(None)):
        log_path = anastasia_logger.log_path

    # Reset all existing handlers
    while anastasia_logger.hasHandlers():
        anastasia_logger.removeHandler(anastasia_logger.handlers[0])
    
    # Set new tag to Formatter
    format_left = anastasia_logger.formatter._fmt.split("[")[0]
    format_rigth = anastasia_logger.formatter._fmt.split("]")[-1]
    format = format_left + f"[{tag}]" + format_rigth
    fmt = Formatter(format, anastasia_logger.formatter.datefmt)

    # Set level hierarchy
    anastasia_logger.setLevel(level)

    handlers = []
    # Set new FileHandler if save_log is True
    if save_log:
        fh = FileHandler(log_path)
        fh.setFormatter(fmt)
        handlers.append(fh)
    # Set new StreamHandler
    sh = StreamHandler()
    sh.setFormatter(fmt)
    handlers.append(sh)

    # Add new Handlers to root AnastasiaLogger
    for h in handlers:
        anastasia_logger.addHandler(h)

    # Warning about parameters not compatible inherited from basicConfig versioning definitions
    if kwargs:
        params = list(kwargs.keys())
        anastasia_logger.warning(f"Parameters {params} are not implement or doesn't exists in basicConfig")

def override_logging(based_on: Optional[AnastasiaLogger] = None) -> None:
    """
    Modify base root logging with Anastasia logging format

    Attributes
    ----------

    based_on : Optional[AnastasiaLogger], default=None
        Reply properties from existing AnastasiaLogger, if not declared then it will use default AnastasiaLogger properties

    """
    import logging
    filename = anastasia_logger.log_path
    save_log = anastasia_logger.save_log
    format = anastasia_logger.formatter._fmt
    datefmt = anastasia_logger.formatter.datefmt
    level = anastasia_logger.level
    if isinstance(based_on, AnastasiaLogger):
        filename = based_on.log_path
        save_log = anastasia_logger.save_log
        format = based_on.formatter.format
        datefmt = based_on.formatter.datefmt
        level = based_on.level

    if not save_log:
        filename = None

    logging.basicConfig(filename=filename, format=format, datefmt=datefmt, level=level)
    logging.info("Root logging modified with AnastasiaLogger structure")

def debug(msg: Optional[str] = None, code: Optional[int] = None, save_log: bool = False, return_formatted_msg: bool = False, *args, **kwargs) -> Optional[str]:
    """
    Inherited from logging.debug function with additional properties

    Attributes
    ----------

    msg : Optional[str], default=None
        Name identification of logger instance

    code : Optional[int], default=None
        Code assignation to add, if msg is not declared then it will search for default debug codes

    save_log : bool, default=False
        Force to save log file, predefined with log_path attribute

    return_formatted_msg : bool = False
        If True, return the formatted message for further usage as a string

    *args, **kwargs inherited from logging.debug function

    Returns
    -------

    formatted_msg : Optional[str]
        Message formatted with logger definitions

    Notes
    -----

    Base codes standards:

    -   0 = Unindentified
    - 1XX = Data related
    - 2XX = Mathematical related
    - 3XX = AI related
    - 4XX = Resources related
    - 5XX = Operative System (OS) related
    - 6XX = API related
    - 7XX = AWS related

    """

    return anastasia_logger.debug(msg=msg, code=code, save_log=save_log, return_formatted_msg=return_formatted_msg, *args, **kwargs)

def info(msg: Optional[str] = None, code: Optional[int] = None, save_log: bool = False, return_formatted_msg: bool = False, *args, **kwargs) -> Optional[str]:
    """
    Inherited from logging.info function with additional properties

    Attributes
    ----------

    msg : Optional[str], default=None
        Name identification of logger instance

    code : Optional[int], default=None
        Code assignation to add, if msg is not declared then it will search for default info codes

    save_log : bool, default=False
        Force to save log file, predefined with log_path attribute

    return_formatted_msg : bool = False
        If True, return the formatted message for further usage as a string

    *args, **kwargs inherited from logging.info function

    Returns
    -------

    formatted_msg : Optional[str]
        Message formatted with logger definitions

    Notes
    -----

    Base codes standards:

    -   0 = Unindentified
    - 1XX = Data related
    - 2XX = Mathematical related
    - 3XX = AI related
    - 4XX = Resources related
    - 5XX = Operative System (OS) related
    - 6XX = API related
    - 7XX = AWS related

    """

    return anastasia_logger.info(msg=msg, code=code, save_log=save_log, return_formatted_msg=return_formatted_msg, *args, **kwargs)

def warning(msg: Optional[str] = None, code: Optional[int] = None, save_log: bool = False, return_formatted_msg: bool = False, *args, **kwargs) -> Optional[str]:
    """
    Inherited from logging.warning function with additional properties

    Attributes
    ----------

    msg : Optional[str], default=None
        Name identification of logger instance

    code : Optional[int], default=None
        Code assignation to add, if msg is not declared then it will search for default warning codes

    save_log : bool, default=False
        Force to save log file, predefined with log_path attribute

    return_formatted_msg : bool = False
        If True, return the formatted message for further usage as a string

    *args, **kwargs inherited from logging.warning function

    Returns
    -------

    formatted_msg : str
        Message formatted with logger definitions

    Notes
    -----

    Base codes standards:

    -   0 = Unindentified
    - 1XX = Data related
    - 2XX = Mathematical related
    - 3XX = AI related
    - 4XX = Resources related
    - 5XX = Operative System (OS) related
    - 6XX = API related
    - 7XX = AWS related

    """

    return anastasia_logger.warning(msg=msg, code=code, save_log=save_log, return_formatted_msg=return_formatted_msg, *args, **kwargs)

def error(msg: Optional[str] = None, code: Optional[int] = None, raise_type: Optional[type] = None, save_log: bool = False, return_formatted_msg: bool = False, *args, **kwargs) -> Optional[str]:
    """
    Inherited from logging.error function with additional properties

    Attributes
    ----------

    msg : Optional[str], default=None
        Name identification of logger instance

    code : Optional[int], default=None
        Code assignation to add, if msg is not declared then it will search for default error codes

    raise_type : Optional[type], default=None
        Raise any type with message content as text description and terminating python script execution, if None then no python type will be raised

    save_log : bool, default=False
        Force to save log file, predefined with log_path attribute

    return_formatted_msg : bool = False
        If True, return the formatted message for further usage as a string

    *args, **kwargs inherited from logging.error function

    Returns
    -------

    formatted_msg : str
            Message formatted with logger definitions

    Notes
    -----

    Base codes standards:

    -   0 = Unindentified
    - 1XX = Data related
    - 2XX = Mathematical related
    - 3XX = AI related
    - 4XX = Resources related
    - 5XX = Operative System (OS) related
    - 6XX = API related
    - 7XX = AWS related

    """
    
    return anastasia_logger.error(msg=msg, code=code, raise_type=raise_type, save_log=save_log, return_formatted_msg=return_formatted_msg, *args, **kwargs)

def critical(msg: Optional[str] = None, code: Optional[int] = None, raise_type: Optional[type] = None, save_log: bool = False, return_formatted_msg: bool = False, *args, **kwargs) -> Optional[str]:
    """
    Inherited from logging.critical function with additional properties

    Attributes
    ----------

    msg : Optional[str], default=None
        Name identification of logger instance

    code : Optional[int], default=None
        Code assignation to add, if msg is not declared then it will search for default critical codes

    raise_type : Optional[type], default=None
        Raise any type with message content as text description and terminating python script execution, if None then no python type will be raised

    save_log : bool, default=False
        Force to save log file, predefined with log_path attribute

    return_formatted_msg : bool = False
        If True, return the formatted message for further usage as a string

    *args, **kwargs inherited from logging.critical function

    Returns
    -------

    formatted_msg : str
            Message formatted with logger definitions

    Notes
    -----

    Base codes standards:

    -   0 = Unindentified
    - 1XX = Data related
    - 2XX = Mathematical related
    - 3XX = AI related
    - 4XX = Resources related
    - 5XX = Operative System (OS) related
    - 6XX = API related
    - 7XX = AWS related

    """
    
    return anastasia_logger.critical(msg=msg, code=code, raise_type=raise_type, save_log=save_log, return_formatted_msg=return_formatted_msg, *args, **kwargs)

fatal = critical # fatal = critical in base logging implementation

def print(msg: Optional[str] = None, code: Optional[int] = None, return_formatted_msg: bool = False, *args, **kwargs) -> Optional[str]:
    """
    Show in console a required message with logger format, doesn't register in contained handlers (just for console view, like a normal python print). 

    Attributes
    ----------

    msg : Optional[str], default=None
        Name identification of logger instance

    code : Optional[int], default=None
        Code assignation to add, if msg is not declared then it will search for default error codes

    return_formatted_msg : bool = False
            If True, return the formatted message for further usage as a string

    Returns
    -------

    formatted_msg : str
        Message formatted with logger definitions

    Notes
    -----

    Base codes standards:

    -   0 = Unindentified
    - 1XX = Data related
    - 2XX = Mathematical related
    - 3XX = AI related
    - 4XX = Resources related
    - 5XX = Operative System (OS) related
    - 6XX = API related
    - 7XX = AWS related

    """
    
    return anastasia_logger.print(msg=msg, code=code, return_formatted_msg=return_formatted_msg, *args, **kwargs)