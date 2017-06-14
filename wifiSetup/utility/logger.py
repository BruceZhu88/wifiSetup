'''
Created on 2014-07-02

@author: Ivan.Cai
'''

import os
import time
import logging

class Logger(object):
    '''
    '''


    def __init__(self):
        '''
        Constructor
        '''
        #self.cfg=getTestConfig('testconfig.ini')



    @classmethod
    def init_logger(cls,project_code, root_dir = None):
        #cfg=getTestConfig('testconfig.ini')
        #project_code=cfg['testconfig']['project_code']
        cls.log_conf = cls.make_root_dir(project_code, root_dir)

        logfile = cls.get_logfile("log_" + project_code+ "_" + cls.get_logger_timestr())

        logfile_fullname = os.path.join(cls.log_conf['runlog_dir'], logfile)

        logformat = cls.get_log_format()
        logging.basicConfig(level = logging.DEBUG,
                            format = logformat,
                            filename = logfile_fullname,
                            filemode = 'a')

        # send log to stdout as well
        cls._add_console_handler()

        cls.log_conf['logfile'] = logfile
        return cls.log_conf


    @classmethod
    def close_logger(cls, next_logfile = ''):
        for handler in logging.getLogger(None).handlers:
            if isinstance(handler, logging.FileHandler):
                logging.info('Close logging file %s' % handler.baseFilename)
                if next_logfile:
                    logging.info('Rollover to logging file %s' % next_logfile)

                handler.close()
                logging.getLogger(None).removeHandler(handler)

        for handler in logging.getLogger('').handlers:
            handler.close()
            logging.getLogger('').removeHandler(handler)


    @classmethod
    def next_logger(cls, build_ver, tcid_str_00):
        tcid_str = tcid_str_00.replace(':', '_').replace(' ', '')

        # new logfile
        logfile = cls.get_logfile(tcid_str)

        runlog_dir = os.path.realpath(os.path.join(cls.log_conf['runlog_dir'], build_ver))
        if not os.path.exists(runlog_dir):
            os.makedirs(runlog_dir)

        logfile_fullname = os.path.join(runlog_dir, logfile)

        # close file logger and remove it before adding new handler/logfile
        cls.close_logger(logfile_fullname)

        # new logfile handler
        cls._add_logfile_handler(logfile_fullname)

        # send log to stdout as well
        cls._add_console_handler()

        cls.log_conf['logfile'] = logfile

        return cls.log_conf


    @classmethod
    def make_root_dir(cls, project_code, root_dir = None):
        cls.log_conf = dict(root_run = os.getcwd())
        """

        if not root_dir:
            if os.environ.has_key('AT_LOGGER_DIR'):
                root_dir = os.environ['AT_LOGGER_DIR']

            else:
                root_dir = os.path.realpath(os.path.join(os.getcwd(), "..", 'log'))

        """
        root_dir = os.path.realpath(os.path.join(os.getcwd(), "..", 'log'))
        runlog_dir = os.path.realpath(os.path.join(root_dir, project_code))
        #print(runlog_dir)
        if not os.path.exists(runlog_dir):
            os.makedirs(runlog_dir)

        cls.log_conf['runlog_dir'] = runlog_dir

        return cls.log_conf


    @classmethod
    def get_logger_timestr(cls):
        return time.strftime("%Y%m%d%H%M")


    @classmethod
    def get_log_format(cls):
        logformat = '%(asctime)s %(levelname)-8s %(message)s'

        return logformat


    @classmethod
    def get_logfile(cls, filename_id):
        logfile = "%s.txt" % (filename_id)

        return logfile


    @classmethod
    def get_log_filename_linux(cls, logfile_fullname):
        return logfile_fullname.replace("\\", "/")


    @classmethod
    def _add_logfile_handler(cls, logfile_fullname):
        '''
        '''
        fileHandler = logging.FileHandler(logfile_fullname)
        fileHandler.setLevel(logging.DEBUG)
        #fileHandler.setLevel(logging.INFO)
        logformat = logging.Formatter(cls.get_log_format())
        fileHandler.setFormatter(logformat)
        logging.getLogger(None).addHandler(fileHandler)


    @classmethod
    def _add_console_handler(cls):
        '''
        '''
        console = logging.StreamHandler()
        #console.setLevel(logging.DEBUG)
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(cls.get_log_format())
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)


if __name__ == "__main__":

    '''
    '''

    log_conf = Logger.init_logger('project.log')
    logging.log(logging.DEBUG, 'Debug message')
    logging.log(logging.INFO, 'info message')
    Logger.next_logger('1.0', '1.0')
    logging.log(logging.DEBUG, 'Debug message?')
    logging.log(logging.INFO, 'Debug message for another TC')
    logging.log(logging.DEBUG, 'Logger will now close...')
    Logger.close_logger()
    Logger.next_logger('2.0', '2.0')
    logging.log(logging.DEBUG, 'What happened?')
    logging.log(logging.INFO, 'New log for another TC')
    logging.log(logging.DEBUG, 'Logger will now close...')

