from datetime import datetime

from py4j.java_gateway import JavaGateway
from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.streaming import StreamingContext

class sparkUtil:
    def writehdfs(self):
        # conf = SparkConf().setMaster("local").setAppName('sparkUtil')
        # sc = SparkContext('local', 'test', conf=conf)
        spark = SparkSession.builder.getOrCreate()
        # spark = SparkSession.builder\
        #     .master("local") \
        #     .getOrCreate()
        # spark = SparkSession(conf).getOrCreate() #SparkSession(sc)

        # parquetFile = r"hdfs://host:port/Felix_test/test_data.parquet"
        parquetFile = r"hdfs://master:9870/user/limm/sparkSql/users.parquet"
        df = spark.read.parquet(parquetFile)
        print(df.first())

    def insHdsf(self):
        pass


    def mongo2hdfs(self, tblname, fdlist, where, pathtosave):
        print("tblname:" + tblname +",fdlist:" + fdlist+",where:"+where+",pathtosave:"+pathtosave)
        mongoUri = "mongodb+srv://home.hddly.cn:57017/pythondb"
        timetosleep = 10
        my_spark = SparkSession.builder \
            .appName("mongo2hdfs") \
            .master("local[*]") \
            .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.2") \
            .config("spark.mongodb.input.uri", mongoUri) \
            .config("spark.mongodb.output.uri", mongoUri) \
            .config("spark.network.timeout", "7200s") \
            .config("spark.executor.heartbeatInterval", "1200s") \
            .getOrCreate()


        # my_spark.conf.set('spark.sql.session.timeZone', 'UTC')
        tmptblname = "tmp_" + tblname
        isucc,ifail = 0,0
        timeDF = my_spark.sql("select  current_timestamp()")
        last_timestamp = timeDF.collect()[0][0]

        last_timestamp=last_timestamp + datetime.timedelta(minutes=-1)
        # relativedelta(minutes=-1)...strftime("%Y-%m-%d %H:%M:%S")
        last_time = format(last_timestamp, '%Y-%m-%d %H:%M:%S')
        print("last_time:"+last_time)
        # my_spark.read.format("mongo").option("collection", tblname).load() \
        #     .createOrReplaceTempView(tmptblname)
        my_spark.read.format("mongo").option("collection", tblname).load() \
            .createOrReplaceTempView(tmptblname)

        while True:
            datetime.sleep(timetosleep)
            timeDF = my_spark.sql("select  current_timestamp()")
            current_timestamp = timeDF.collect()[0][0]
            current_timestamp = current_timestamp + datetime.timedelta(minutes=-1)
            current_time = format(current_timestamp, '%Y-%m-%d %H:%M:%S')

            print("current_time:"+current_time)
            sql_str = "select %s from %s " % (fdlist, tmptblname)

            sqlDF = my_spark.sql(sql_str)

            sqldfwhere = sqlDF.where(where)

            sqldfilter1=sqldfwhere.filter(sqldfwhere["coll_time"]> last_timestamp)

            # sqldfilter = sqldfwhere.filter("coll_time > '" + last_time +"'")
            if (sqldfilter1.isEmpty()):
                print(current_time + ",Fail:" + str(ifail)+ ",Succ:" + str(isucc) )
                ifail+=1
            else:
                fileid = "music_data_" + format(current_timestamp, '%Y%m%d%H%M%S') + "_" + str(isucc).zfill(3)
                sqldfilter1.repartition(1).write.mode("overwrite").format("json") \
                    .save(pathtosave + fileid)
                print(current_time + ",Succ:" + str(isucc)+ ",Fail:" + str(ifail))
                isucc+=1

            last_time = current_time
            last_timestamp=current_timestamp
            print("current_time=>last_time:" + last_time)
            my_spark.stop

    def testhdfs(self):
        collector = "张三"
        tblname = "music_data_1"
        fdlist = "song_url,song_name,collector,coll_time"
        where = "collector='" + collector + "'"
        pathtosave = "hdfs://master:9864/user/myname/spark/"
        sparku.mongo2hdfs(tblname, fdlist, where, pathtosave)

    def dealstream(self):
        sc = SparkContext("local[2]", "NetworkWordCount")
        ssc = StreamingContext(sc, 1)
        java_gateway = JavaGateway.launch_gateway(die_on_exit=True)
        java_gateway.start_callback_server()
        lines = ssc.socketTextStream("slave1", 8888)
        words = lines.flatMap(lambda line: line.split(" "))
        pairs = words.map(lambda word: (word, 1))
        wordCounts = pairs.reduceByKey(lambda x, y: x + y)

        # Print the first ten elements of each RDD generated in this DStream to the console
        wordCounts.pprint()
        ssc.start()  # Start the computation
        # ssc.awaitTermination(10)  # Wait for the computation to terminate
        ssc.awaitTerminationOrTimeout(10)
        ssc.stop()

if __name__ == '__main__':
    sparku = sparkUtil()
    # sparku.writehdfs();
    sparku.dealstream();
    # sparku.testhdfs();
