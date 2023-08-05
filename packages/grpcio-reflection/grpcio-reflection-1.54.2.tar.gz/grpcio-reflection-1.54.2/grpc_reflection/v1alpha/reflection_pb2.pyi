from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ErrorResponse(_message.Message):
    __slots__ = ["error_code", "error_message"]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    error_code: int
    error_message: str
    def __init__(self, error_code: _Optional[int] = ..., error_message: _Optional[str] = ...) -> None: ...

class ExtensionNumberResponse(_message.Message):
    __slots__ = ["base_type_name", "extension_number"]
    BASE_TYPE_NAME_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    base_type_name: str
    extension_number: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, base_type_name: _Optional[str] = ..., extension_number: _Optional[_Iterable[int]] = ...) -> None: ...

class ExtensionRequest(_message.Message):
    __slots__ = ["containing_type", "extension_number"]
    CONTAINING_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    containing_type: str
    extension_number: int
    def __init__(self, containing_type: _Optional[str] = ..., extension_number: _Optional[int] = ...) -> None: ...

class FileDescriptorResponse(_message.Message):
    __slots__ = ["file_descriptor_proto"]
    FILE_DESCRIPTOR_PROTO_FIELD_NUMBER: _ClassVar[int]
    file_descriptor_proto: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, file_descriptor_proto: _Optional[_Iterable[bytes]] = ...) -> None: ...

class ListServiceResponse(_message.Message):
    __slots__ = ["service"]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    service: _containers.RepeatedCompositeFieldContainer[ServiceResponse]
    def __init__(self, service: _Optional[_Iterable[_Union[ServiceResponse, _Mapping]]] = ...) -> None: ...

class ServerReflectionRequest(_message.Message):
    __slots__ = ["all_extension_numbers_of_type", "file_by_filename", "file_containing_extension", "file_containing_symbol", "host", "list_services"]
    ALL_EXTENSION_NUMBERS_OF_TYPE_FIELD_NUMBER: _ClassVar[int]
    FILE_BY_FILENAME_FIELD_NUMBER: _ClassVar[int]
    FILE_CONTAINING_EXTENSION_FIELD_NUMBER: _ClassVar[int]
    FILE_CONTAINING_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    LIST_SERVICES_FIELD_NUMBER: _ClassVar[int]
    all_extension_numbers_of_type: str
    file_by_filename: str
    file_containing_extension: ExtensionRequest
    file_containing_symbol: str
    host: str
    list_services: str
    def __init__(self, host: _Optional[str] = ..., file_by_filename: _Optional[str] = ..., file_containing_symbol: _Optional[str] = ..., file_containing_extension: _Optional[_Union[ExtensionRequest, _Mapping]] = ..., all_extension_numbers_of_type: _Optional[str] = ..., list_services: _Optional[str] = ...) -> None: ...

class ServerReflectionResponse(_message.Message):
    __slots__ = ["all_extension_numbers_response", "error_response", "file_descriptor_response", "list_services_response", "original_request", "valid_host"]
    ALL_EXTENSION_NUMBERS_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ERROR_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    FILE_DESCRIPTOR_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    LIST_SERVICES_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_REQUEST_FIELD_NUMBER: _ClassVar[int]
    VALID_HOST_FIELD_NUMBER: _ClassVar[int]
    all_extension_numbers_response: ExtensionNumberResponse
    error_response: ErrorResponse
    file_descriptor_response: FileDescriptorResponse
    list_services_response: ListServiceResponse
    original_request: ServerReflectionRequest
    valid_host: str
    def __init__(self, valid_host: _Optional[str] = ..., original_request: _Optional[_Union[ServerReflectionRequest, _Mapping]] = ..., file_descriptor_response: _Optional[_Union[FileDescriptorResponse, _Mapping]] = ..., all_extension_numbers_response: _Optional[_Union[ExtensionNumberResponse, _Mapping]] = ..., list_services_response: _Optional[_Union[ListServiceResponse, _Mapping]] = ..., error_response: _Optional[_Union[ErrorResponse, _Mapping]] = ...) -> None: ...

class ServiceResponse(_message.Message):
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...
