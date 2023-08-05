import time

from dequeai.deque_environment import AGENT_API_SERVICE_URL
#from deque.redis_services import RedisServices
import pickle
from dequeai.rest_connect import RestConnect
import json
import requests
import asyncio

class ParsingService:
    def __init__(self):
        #self._redis = RedisServices.get_redis_connection()
        self._rest = RestConnect()
        self.tracking_endpoint = AGENT_API_SERVICE_URL+"/fex/python/track/"

    def receive(self):
        while True:
            #run_ids = self._redis.smembers("run_ids:")


            #for s in run_ids:
               # s = str(s.decode("utf-8"))
                #steps = self._redis.smembers("run_id:steps:"+s)
                #print(steps)

                #for step in steps:
                    #step = str(step.decode("utf-8"))
                    #print("Step")
                    #print(step)
                    #key = "run_id:step:data:"+s+step
                    #pickled_data = self._redis.get(key)
                    #experiment_data = pickle.loads(pickled_data)
                    #print("pickled data")
                    #print(pickle.loads(pickled_data))



                    #if pickled_data is None:
                        #continue
                    #self._upload_data(pickled_data=pickled_data)
                    #self._rest.post_binary(url=self.tracking_endpoint,data=pickled_data)
                    #self._redis.delete(key)
                    #self._redis.srem("run_id:steps:"+s,step)

                    #self._get_all_values(data)
            time.sleep(1)

    def _upload_data(self, pickled_data):
        experiment_data = pickle.loads(pickled_data)
        user_name = experiment_data['user_name']

        workload_type = experiment_data['workload_type']

        project_name = experiment_data['project_name']
        run_id = experiment_data['run_id']
        step = experiment_data['step']







        data = {}

        data.update({
            'user_name': user_name, 'workload_type': workload_type, 'project_name': project_name,'run_id':run_id,'step':step,

        })


        filenames = []



        filenames.append(
                    (
                        'experiment_files[]', (
                            pickled_data,
                            ), 'application/octet',
                        ),
                    ),



        filenames.append(
            ('data', ('data', json.dumps(experiment_data), 'application/json')),
        )

        resp = requests.post(
            AGENT_API_SERVICE_URL + '/fex/python/track/',
            files=filenames,
        )






    def _get_all_values(self, nested_dictionary):
        for key, value in nested_dictionary.items():
            if type(value) is dict:
                self._get_all_values(value)
            else:
                print(key, ":", value)

    def test(self):
        ex = {"k":"v"}
        pickled_object = pickle.dumps(ex)
        self._redis.set("test_key",pickled_object)
        data_p = self._redis.get("test_key")

        print(pickle.loads(data_p))





if __name__ =="__main__":
    deque = ParsingService()
    for i in range(100):
        d = {"accuracy":99,"label":"cat","i":i}
        deque.log(d, i)









