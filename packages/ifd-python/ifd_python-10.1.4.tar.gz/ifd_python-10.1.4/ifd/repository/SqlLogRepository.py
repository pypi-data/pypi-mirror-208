from .abstract import AbsSqlRepository

class SqlLogRepository(AbsSqlRepository):
    
    def insertOne(self, img_id, log):
        if not self.is_open:
            self._connectToDatabase()

        cur = self.connection.cursor()
        
        log.startTime = '%s.%i' % (log.startTime.strftime("%m/%d/%Y %H:%M:%S"), log.startTime.microsecond/1000)
        log.stopTime = '%s.%i' % (log.stopTime.strftime("%m/%d/%Y %H:%M:%S"), log.stopTime.microsecond/1000)
        log.message = log.message.replace("'", "''")
        
        req = f"""
            INSERT INTO T_H_HISTO_ANALYSE_HIA (IMG_ID,HIA_STEP,HIA_START,HIA_STOP,HIA_DURATION,HIA_RESULT,HIA_MESSAGE)
            VALUES (
                {img_id},
                '{log.step}',
                CAST('{log.startTime}' as datetime),
                CAST('{log.stopTime}' as datetime),
                '{log.duration}',
                '{log.result}',
                '{log.message}'
                )
            """
        print(req)
        cur.execute(req)
        cur.close()