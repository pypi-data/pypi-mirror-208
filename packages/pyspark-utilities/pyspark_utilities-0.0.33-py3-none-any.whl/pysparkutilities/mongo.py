from .datastorage import DataStorage
from .utils import get_dataset_property

class Mongo(DataStorage):

    def __init__(self):
        super().__init__()
        user = get_dataset_property('mongoUser')
        password = get_dataset_property('mongoPassword')
        ip = get_dataset_property('mongoUri').split(":")[0] 
        port = get_dataset_property('mongoUri').split(":")[1] 
        self.uri = "mongodb://" + user + ":" + password + "@" + ip + ":" + port + "/"


    # overriding abstract method
    def load_dataset(self, name, read_all=True, input_dest=None, header=True):

        if input_dest is None:
            input_dest = get_dataset_property("input-dataset")
   
        db = input_dest.split["."][0]
        collection = input_dest.split["."][1]

        df = self.spark.read.format("com.mongodb.spark.sql.DefaultSource")\
            .option("uri", self.uri).option("database", db).option("collection", collection)\
            .load()
        return df


    # overriding abstract method
    def save_dataset(self, name, df, output_dest=None):

        if output_dest is None:
            output_dest = get_dataset_property("output-dataset")
       
        db = output_dest.split["."][0]
        collection = output_dest.split["."][1]

        df.write.format("com.mongodb.spark.sql.DefaultSource").mode("append")\
            .option("uri", self.uri).option("database", db).option("collection", collection)\
            .save()
