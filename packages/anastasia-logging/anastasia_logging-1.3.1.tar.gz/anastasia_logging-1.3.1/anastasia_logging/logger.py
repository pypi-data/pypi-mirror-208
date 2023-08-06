import time

from typing import Optional
from logging import getLogger, _levelToName
from logging import Logger, Formatter, FileHandler, StreamHandler
from logging import DEBUG, INFO, WARNING, ERROR, DEBUG, CRITICAL, FATAL 

from anastasia_logging.codes import StandardCodes
from anastasia_logging.env import EnvironmentVariables

PRINT = -1


class AnastasiaLogger(Logger):

    def __init__(self, name: Optional[str] = None, tag: Optional[str] = None, level: Optional[str] = None, save_log: Optional[bool] = None, log_path: Optional[str] = None):
        """
        Class wrapper from logging.Logger implementation

        Attributes
        ----------

        name : Optional[str], default='anastasia-log'
            Name identification of logger instance

        tag : Optional[str], default='ANASTASIA-JOB'
            Tag identification for job type for StreamHandlers (console) and FileHandlers (file)

        level : Optional[str], default='INFO'
            Define severity hierarchy for log generation

        save_log : Optional[bool], default=False
            Generate .log file containing logs generated

        log_path : Optional[str], default='anastasia-log.log'
            Define a custom name for log file, if none then it will be called anastasia-logs.log and will be saved in root workdir

        """
        
        self.env_vars = EnvironmentVariables()
        self.standard_codes = StandardCodes()

        if isinstance(name, type(None)):
            name = self.env_vars.ANASTASIA_LOG_NAME
        if isinstance(tag, type(None)):
            tag = self.env_vars.ANASTASIA_LOG_TAG
        if isinstance(level, type(None)):
            level = self.env_vars.ANASTASIA_LOG_LEVEL
        if isinstance(save_log, type(None)):
            save_log = self.env_vars.ANASTASIA_LOG_SAVELOG
        if isinstance(log_path, type(None)):
            log_path = self.env_vars.ANASTASIA_LOG_PATH

        Logger.__init__(self, name, level)

        self.formatter = Formatter('%(asctime)s | ['+tag+'] %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S UTC/GMT%z')
        self.tag = tag
        self.save_log = save_log
        self.log_path = log_path

        self._initial_formatter()
        if self.save_log:
            self._initial_filehandler(self.log_path)

    def __reduce__(self):
        return getLogger, ()
    
    def _initial_formatter(self) -> None:
        """
        Set formatter type for class initialization

        """
        sh = StreamHandler()
        sh.setFormatter(self.formatter)
        self.addHandler(sh)

    def _initial_filehandler(self, log_path: str) -> None:
        """
        Set file handler for class initialization

        Attributes
        ----------

        log_path : str
            Log filename path

        """
        fh = FileHandler(log_path)
        fh.setFormatter(self.formatter)
        self.addHandler(fh)

    def _get_standard_severity(self, level: int) -> dict:
        """
        Get standar severity code description

        Attributes
        ----------

        level : int
            Severity of logger

        Returns
        -------

        standard_codes : dict
            Dict with codes and default descriptions

        """
        if level == DEBUG:
            return self.standard_codes.DEBUG
        elif level == INFO:
            return self.standard_codes.INFO
        elif level == WARNING:
            return self.standard_codes.WARNING
        elif level == ERROR:
            return self.standard_codes.ERROR
        elif level == CRITICAL or level == FATAL:
            return self.standard_codes.CRITICAL
        elif level == PRINT:
            return {}
        else:
            val = "Level detected doesn't exists or is not implemented"
            self.error(val)
            raise ValueError(val)
        
    def _initial_severity_tag_code(self, level: int) -> str:
        """
        Generate level letter assignation to append to code number

        Attributes
        ----------

        level : int
            Severity of logger

        Returns
        -------

        str : str
            Letter representing level severity

        """
        if level == DEBUG:
            return "D"
        elif level == INFO:
            return "I"
        elif level == WARNING:
            return "W"
        elif level == ERROR:
            return "E"
        elif level == CRITICAL or level == FATAL:
            return "C"
        elif level == PRINT:
            return "P"
        else:
            val = "Level detected doesn't exists or is not implemented"
            self.error(val)
            raise ValueError(val)
        
    def _check_code_msg(self, level: int, msg: Optional[str] = None, code: Optional[int] = None) -> str:
        """
        Appends code to message, if no msg has been set, then it will search for default code errors

        Attributes
        ----------

        level : int
            Severity of logger

        msg : Optional[str]
            Message to set in logger

        code : Optional[int]
            Code to set in logger

        Returns
        -------

        str : str
            Modified message

        """
        if (not msg) and (not code):
            msg = ""

        if code:
            if isinstance(code, int):
                severity_codes = self._get_standard_severity(level)
                if not msg:
                    msg = severity_codes.get(code, None)
                    if not msg:
                        code = 0
                        msg = severity_codes[code]
                msg = f"<{self._initial_severity_tag_code(level)}{code}> " + msg
            else:
                val = "Code is not a number"
                self.error(val)
                raise ValueError(val)
            
        return msg

    def debug(self, msg: Optional[str] = None, code: Optional[int] = None, save_log: bool = False, return_formatted_msg: bool = False, *args, **kwargs) -> Optional[str]:
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

        msg = self._check_code_msg(DEBUG, msg, code)

        if save_log:
            self._initial_filehandler(self.log_path)

        if self.isEnabledFor(DEBUG):
            self._log(DEBUG, msg, args, **kwargs)

        if return_formatted_msg:
            return self._getprint(msg=msg, level=DEBUG, *args, **kwargs)

    def info(self, msg: Optional[str] = None, code: Optional[int] = None, save_log: bool = False, return_formatted_msg: bool = False, *args, **kwargs) -> Optional[str]:
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

        msg = self._check_code_msg(INFO, msg, code)

        if save_log:
            self._initial_filehandler(self.log_path)

        if self.isEnabledFor(INFO):
            self._log(INFO, msg, args, **kwargs)

        if return_formatted_msg:
            return self._getprint(msg=msg, level=INFO, *args, **kwargs)

    def warning(self, msg: Optional[str] = None, code: Optional[int] = None, save_log: bool = False, return_formatted_msg: bool = False, *args, **kwargs) -> Optional[str]:
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

        msg = self._check_code_msg(WARNING, msg, code)

        if save_log:
            self._initial_filehandler(self.log_path)

        if self.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, **kwargs)

        if return_formatted_msg:
            return self._getprint(msg=msg, level=WARNING, *args, **kwargs)

    def error(self, msg: Optional[str] = None, code: Optional[int] = None, raise_type: Optional[type] = None, save_log: bool = False, return_formatted_msg: bool = False, *args, **kwargs) -> Optional[str]:
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

        msg = self._check_code_msg(ERROR, msg, code)

        if save_log:
            self._initial_filehandler(self.log_path)

        if self.isEnabledFor(ERROR):
            self._log(ERROR, msg, args, **kwargs)

        if isinstance(raise_type, type):
            raise raise_type(msg)
        
        if return_formatted_msg:
            return self._getprint(msg=msg, level=ERROR, *args, **kwargs)
        
    def critical(self, msg: Optional[str] = None, code: Optional[int] = None, raise_type: Optional[type] = None, save_log: bool = False, return_formatted_msg: bool = False, *args, **kwargs) -> Optional[str]:
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

        msg = self._check_code_msg(CRITICAL, msg, code)

        if save_log:
            self._initial_filehandler(self.log_path)

        if self.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, **kwargs)

        if isinstance(raise_type, type):
            raise raise_type(msg)
        
        if return_formatted_msg:
            return self._getprint(msg=msg, level=CRITICAL, *args, **kwargs)
    
    fatal = critical # fatal = critical in base logging implementation

    def print(self, msg: Optional[str] = None, code: Optional[int] = None, return_formatted_msg: bool = False, *args, **kwargs) -> Optional[str]:
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
        console_msg = self._getprint(msg=msg, code=code, level=PRINT, *args, **kwargs)
        print(console_msg)

        if return_formatted_msg:
            return console_msg

    def _getprint(self, level: int, msg: Optional[str] = None, code: Optional[int] = None, *args, **kwargs) -> str:
        """
        Obtain a string with an example of logger output contained from message. 

        Attributes
        ----------

        msg : Optional[str], default=None
            Name identification of logger instance

        code : Optional[int], default=None
            Code assignation to add, if msg is not declared then it will search for default error codes

        Returns
        -------

        msg : str
            Original message with logger format

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
        fmt = self.formatter._fmt
        datefmt = self.formatter.datefmt

        asctime = time.strftime(datefmt)
        fmt = fmt.replace("%(", "{").replace(")s", "}")
        msg = self._check_code_msg(level, msg, code)
        
        if level == PRINT:
            levelname = "PRINT"
        elif level in [INFO, WARNING, ERROR, DEBUG, CRITICAL, FATAL]:
            levelname = _levelToName[level]
        else:
            val = "Level detected doesn't exists or is not implemented"
            self.error(val)

        return fmt.format(asctime=asctime, levelname=levelname, message=msg)