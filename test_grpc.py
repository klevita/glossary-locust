import grpc
import glossary_pb2
import glossary_pb2_grpc

# Quick test of gRPC service
channel = grpc.insecure_channel('localhost:50051')
stub = glossary_pb2_grpc.GlossaryServiceStub(channel)

try:
    # Test GetAllItems
    request = glossary_pb2.GetAllGlossaryItemsRequest()
    response = stub.GetAllItems(request)
    print(f"GetAllItems: Found {len(response.items)} items")
    if response.items:
        print(f"First item: {response.items[0]}")

        # Test UpdateItem
        update_request = glossary_pb2.UpdateGlossaryItemRequest(
            id=response.items[0].id,
            name="Test Update",
            description="Test Description"
        )
        update_response = stub.UpdateItem(update_request)
        if update_response.HasField('error'):
            print(f"UpdateItem error: {update_response.error.message}")
        elif update_response.HasField('item'):
            print(f"UpdateItem success: {update_response.item}")

except grpc.RpcError as e:
    print(f"gRPC error: {e}")
finally:
    channel.close()
