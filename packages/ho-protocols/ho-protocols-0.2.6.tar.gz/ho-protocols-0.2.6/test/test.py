import ho_protocols.example_pb2 as pb
import ho_protocols.live.live_pb2 as lv

req = pb.ExampleRequest()    
req.type = pb.ExampleRequest.Two
req.param = 42

print('Request:')
print(req)
print(req.SerializeToString())

res = pb.ExampleResponse()
res.valueA = 'Lorem'
res.valueB = 3.1415

print('\nResponse:')
print(res)
print(res.SerializeToString())

msg = lv.LiveStreamItem()
msg.source = "test"
msg.actuator.broodnest.actual_temp = 56
msg.actuator.gate.status = msg.actuator.gate.Status.Closing
msg.sensor.entrance.bees_in = 50
msg.sensor.entrance.bees_out = 150

print('\nLive:')
print(msg)
print(msg.SerializeToString())