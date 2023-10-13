import jaydebeapi
import time
import timeit

class SqlError(Exception):
    '''
    Exception raised for sql execute errors not relating to connection
    issues.
    '''
    def __init__(self,message):
        self.message = message

class dbConn:
    '''
        Should be used for all database connections.
        Attempts to auto recover in the case of all failures related to
        database connectivy, db failures or db failover. 
        Should raise errors and not attempt to rerun bad queries
        invalid data, etc.
    '''
    def __init__(self,
                dlSqlClass,
                dlSqlConnectString,
                dlSqlUser,
                dlSqlPasswd,
                dlSqlJar,
                logger):

        if (dlSqlClass and dlSqlConnectString and dlSqlUser and
            dlSqlPasswd and dlSqlJar and logger):
        
            self.dlSqlClass = dlSqlClass
            self.dlSqlConnectString = dlSqlConnectString
            self.dlSqlUser = dlSqlUser
            self.dlSqlPasswd = dlSqlPasswd
            self.dlSqlJar = dlSqlJar
            self.logger = logger

            # local constants
            self.maxExecAttempts = 240 
            self.dbReconnectSleep = 30
            self.executeSleep = 30
        else:
            raise ValueError('required db connection values not received')

        self.cnxn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        tryConnect = True
        attemptNbr = 0
        while tryConnect:
            try:
                if self.cursor or self.cnxn:
                    self.cursor.close()
                    self.cnxn.close()
            except Exception as e:
                self.logger.debug('unable to close db cursor or connection'
                                  + ' ' + str(e))

            try:
                self.cnxn = jaydebeapi.connect(self.dlSqlClass,
                                      self.dlSqlConnectString,
                                      [self.dlSqlUser,
                                      self.dlSqlPasswd],
                                      self.dlSqlJar,)
                self.cnxn.jconn.setAutoCommit(False)
                self.cursor = self.cnxn.cursor()
                tryConnect = False
            except Exception as e:
                attemptNbr = attemptNbr + 1
                self.logger.warn('dbConn failed connecting to db '
                        + 'attempt number: ' + str(attemptNbr) 
                        + ' - ' + str(e))
                time.sleep(self.dbReconnectSleep)
                pass


    def commit(self):
        self.cnxn.commit()

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def execute(self, sql, sqlVals=None, execMany=False, infoStr=None):
        '''
            somethin
        '''
        sTimer = timeit.default_timer()

        execSql = True
        failedAttempts = 0
        r = None
        resultsSet = None
        while execSql:
            try:
                if execMany:
                    r = self.cursor.executemany(sql,sqlVals)
                else:
                    if sqlVals:
                        r = self.cursor.execute(sql,sqlVals)
                    else:
                        r = self.cursor.execute(sql)

                execSql = False
            except Exception as e:
                self.logger.exception('trying to execute ' + str(infoStr) + ' attempt: ' + str(failedAttempts)) 

                failedAttempts = failedAttempts + 1

                if (failedAttempts > self.maxExecAttempts):
                    self.logger.error('unable to execute delete after '
                                 + ' exceeding max attempts for '
                                 + str(infoStr)) 
                    execSql = False
                    raise
                else: 
                    # the first if is the stop reattempt clause in the case of
                    # non-connection related sql errors, should add other
                    # non-connection related conditions here as they are found
                    if 'Invalid column name' in str(e):
                        self.logger.error('invalid db trx, no additional '
                                + ' tries will be made for these trxs: '
                                 + str(e))
                        execSql = False
                        errorMsg = ('invalid sql: ' + str(sql) 
                                    + ' error: ' + str(e))
                        raise SqlError(errorMsg)
                    else: 
                        '''
                            assume all non-sql errors captured above are
                            connection error and hence retry
                            this includes
                            - The connection is closed
                            - Connection reset
                            - Cannot continue the execution because the session is in the kill state
                        '''
                        self.logger.warning('Lost database connection for '
                                 + str(infoStr) + ' '
                                 + 'attempting to reconnect to database')
                        time.sleep(self.executeSleep)
                        self._connect()
                        continue

        eTimer = timeit.default_timer()
        self.logger.debug("sql exec timing: " + str(infoStr) + ' in '
                 + str((eTimer - sTimer)) + '\n')
        return r, resultsSet


    def __del__(self):
        #self.logger.debug('closing cursor and/or connection')
        try:
            if self.cursor:
                self.cursor.close()
        except:
            pass

        try:
            if self.cnxn:
                self.cnxn.close()
        except:
            pass
            #self.logger.debug('unable to close db cursor or connection'
            #        + ', likely already closed: ' + str(e))

    def close(self):
        self.__del__()



        

