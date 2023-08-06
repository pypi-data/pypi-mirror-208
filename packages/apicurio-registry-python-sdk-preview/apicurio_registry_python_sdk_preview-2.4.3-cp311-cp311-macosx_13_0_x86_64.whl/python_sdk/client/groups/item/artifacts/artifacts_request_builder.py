from __future__ import annotations
from dataclasses import dataclass
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.response_handler import ResponseHandler
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ....models import artifact_content, artifact_meta_data, artifact_search_results, error

class ArtifactsRequestBuilder():
    """
    Manage the collection of artifacts within a single group in the registry.
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Optional[Union[Dict[str, Any], str]] = None) -> None:
        """
        Instantiates a new ArtifactsRequestBuilder and sets the default values.
        Args:
            pathParameters: The raw url or the Url template parameters for the request.
            requestAdapter: The request adapter to use to execute the requests.
        """
        if path_parameters is None:
            raise Exception("path_parameters cannot be undefined")
        if request_adapter is None:
            raise Exception("request_adapter cannot be undefined")
        # Url template to use to build the URL for the current request builder
        self.url_template: str = "{+baseurl}/groups/{groupId}/artifacts{?limit*,offset*,order*,orderby*,ifExists*,canonical*}"

        url_tpl_params = get_path_parameters(path_parameters)
        self.path_parameters = url_tpl_params
        self.request_adapter = request_adapter
    
    async def delete(self,request_configuration: Optional[ArtifactsRequestBuilderDeleteRequestConfiguration] = None) -> None:
        """
        Deletes all of the artifacts that exist in a given group.
        Args:
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from ....models import error

        error_mapping: Dict[str, ParsableFactory] = {
            "500": error.Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[ArtifactsRequestBuilderGetRequestConfiguration] = None) -> Optional[artifact_search_results.ArtifactSearchResults]:
        """
        Returns a list of all artifacts in the group.  This list is paged.
        Args:
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[artifact_search_results.ArtifactSearchResults]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ....models import error

        error_mapping: Dict[str, ParsableFactory] = {
            "500": error.Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models import artifact_search_results

        return await self.request_adapter.send_async(request_info, artifact_search_results.ArtifactSearchResults, error_mapping)
    
    async def post(self,body: Optional[artifact_content.ArtifactContent] = None, request_configuration: Optional[ArtifactsRequestBuilderPostRequestConfiguration] = None) -> Optional[artifact_meta_data.ArtifactMetaData]:
        """
        Creates a new artifact by posting the artifact content.  The body of the request shouldbe the raw content of the artifact.  This is typically in JSON format for *most* of the supported types, but may be in another format for a few (for example, `PROTOBUF`).The registry attempts to figure out what kind of artifact is being added from thefollowing supported list:* Avro (`AVRO`)* Protobuf (`PROTOBUF`)* JSON Schema (`JSON`)* Kafka Connect (`KCONNECT`)* OpenAPI (`OPENAPI`)* AsyncAPI (`ASYNCAPI`)* GraphQL (`GRAPHQL`)* Web Services Description Language (`WSDL`)* XML Schema (`XSD`)Alternatively, you can specify the artifact type using the `X-Registry-ArtifactType` HTTP request header, or include a hint in the request's `Content-Type`.  For example:```Content-Type: application/json; artifactType=AVRO```An artifact is created using the content provided in the body of the request.  Thiscontent is created under a unique artifact ID that can be provided in the requestusing the `X-Registry-ArtifactId` request header.  If not provided in the request,the server generates a unique ID for the artifact.  It is typically recommendedthat callers provide the ID, because this is typically a meaningful identifier, and for most use cases should be supplied by the caller.If an artifact with the provided artifact ID already exists, the default behavioris for the server to reject the content with a 409 error.  However, the caller cansupply the `ifExists` query parameter to alter this default behavior. The `ifExists`query parameter can have one of the following values:* `FAIL` (*default*) - server rejects the content with a 409 error* `UPDATE` - server updates the existing artifact and returns the new metadata* `RETURN` - server does not create or add content to the server, but instead returns the metadata for the existing artifact* `RETURN_OR_UPDATE` - server returns an existing **version** that matches the provided content if such a version exists, otherwise a new version is createdThis operation may fail for one of the following reasons:* An invalid `ArtifactType` was indicated (HTTP error `400`)* No `ArtifactType` was indicated and the server could not determine one from the content (HTTP error `400`)* Provided content (request body) was empty (HTTP error `400`)* An artifact with the provided ID already exists (HTTP error `409`)* The content violates one of the configured global rules (HTTP error `409`)* A server error occurred (HTTP error `500`)
        Args:
            body: The request body
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[artifact_meta_data.ArtifactMetaData]
        """
        if body is None:
            raise Exception("body cannot be undefined")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ....models import error

        error_mapping: Dict[str, ParsableFactory] = {
            "400": error.Error,
            "409": error.Error,
            "500": error.Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models import artifact_meta_data

        return await self.request_adapter.send_async(request_info, artifact_meta_data.ArtifactMetaData, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[ArtifactsRequestBuilderDeleteRequestConfiguration] = None) -> RequestInformation:
        """
        Deletes all of the artifacts that exist in a given group.
        Args:
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation()
        request_info.url_template = self.url_template
        request_info.path_parameters = self.path_parameters
        request_info.http_method = Method.DELETE
        if request_configuration:
            request_info.add_request_headers(request_configuration.headers)
            request_info.add_request_options(request_configuration.options)
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[ArtifactsRequestBuilderGetRequestConfiguration] = None) -> RequestInformation:
        """
        Returns a list of all artifacts in the group.  This list is paged.
        Args:
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation()
        request_info.url_template = self.url_template
        request_info.path_parameters = self.path_parameters
        request_info.http_method = Method.GET
        request_info.headers["Accept"] = ["application/json"]
        if request_configuration:
            request_info.add_request_headers(request_configuration.headers)
            request_info.set_query_string_parameters_from_raw_object(request_configuration.query_parameters)
            request_info.add_request_options(request_configuration.options)
        return request_info
    
    def to_post_request_information(self,body: Optional[artifact_content.ArtifactContent] = None, request_configuration: Optional[ArtifactsRequestBuilderPostRequestConfiguration] = None) -> RequestInformation:
        """
        Creates a new artifact by posting the artifact content.  The body of the request shouldbe the raw content of the artifact.  This is typically in JSON format for *most* of the supported types, but may be in another format for a few (for example, `PROTOBUF`).The registry attempts to figure out what kind of artifact is being added from thefollowing supported list:* Avro (`AVRO`)* Protobuf (`PROTOBUF`)* JSON Schema (`JSON`)* Kafka Connect (`KCONNECT`)* OpenAPI (`OPENAPI`)* AsyncAPI (`ASYNCAPI`)* GraphQL (`GRAPHQL`)* Web Services Description Language (`WSDL`)* XML Schema (`XSD`)Alternatively, you can specify the artifact type using the `X-Registry-ArtifactType` HTTP request header, or include a hint in the request's `Content-Type`.  For example:```Content-Type: application/json; artifactType=AVRO```An artifact is created using the content provided in the body of the request.  Thiscontent is created under a unique artifact ID that can be provided in the requestusing the `X-Registry-ArtifactId` request header.  If not provided in the request,the server generates a unique ID for the artifact.  It is typically recommendedthat callers provide the ID, because this is typically a meaningful identifier, and for most use cases should be supplied by the caller.If an artifact with the provided artifact ID already exists, the default behavioris for the server to reject the content with a 409 error.  However, the caller cansupply the `ifExists` query parameter to alter this default behavior. The `ifExists`query parameter can have one of the following values:* `FAIL` (*default*) - server rejects the content with a 409 error* `UPDATE` - server updates the existing artifact and returns the new metadata* `RETURN` - server does not create or add content to the server, but instead returns the metadata for the existing artifact* `RETURN_OR_UPDATE` - server returns an existing **version** that matches the provided content if such a version exists, otherwise a new version is createdThis operation may fail for one of the following reasons:* An invalid `ArtifactType` was indicated (HTTP error `400`)* No `ArtifactType` was indicated and the server could not determine one from the content (HTTP error `400`)* Provided content (request body) was empty (HTTP error `400`)* An artifact with the provided ID already exists (HTTP error `409`)* The content violates one of the configured global rules (HTTP error `409`)* A server error occurred (HTTP error `500`)
        Args:
            body: The request body
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise Exception("body cannot be undefined")
        request_info = RequestInformation()
        request_info.url_template = self.url_template
        request_info.path_parameters = self.path_parameters
        request_info.http_method = Method.POST
        request_info.headers["Accept"] = ["application/json"]
        if request_configuration:
            request_info.add_request_headers(request_configuration.headers)
            request_info.set_query_string_parameters_from_raw_object(request_configuration.query_parameters)
            request_info.add_request_options(request_configuration.options)
        request_info.set_content_from_parsable(self.request_adapter, "application/create.extended+json", body)
        return request_info
    
    @dataclass
    class ArtifactsRequestBuilderDeleteRequestConfiguration():
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        # Request headers
        headers: Optional[Dict[str, Union[str, List[str]]]] = None

        # Request options
        options: Optional[List[RequestOption]] = None

    
    @dataclass
    class ArtifactsRequestBuilderGetQueryParameters():
        """
        Returns a list of all artifacts in the group.  This list is paged.
        """
        # The number of artifacts to return.  Defaults to 20.
        limit: Optional[int] = None

        # The number of artifacts to skip before starting the result set.  Defaults to 0.
        offset: Optional[int] = None

        # Sort order, ascending (`asc`) or descending (`desc`).
        order: Optional[str] = None

        # The field to sort by.  Can be one of:* `name`* `createdOn`
        orderby: Optional[str] = None

    
    @dataclass
    class ArtifactsRequestBuilderGetRequestConfiguration():
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        # Request headers
        headers: Optional[Dict[str, Union[str, List[str]]]] = None

        # Request options
        options: Optional[List[RequestOption]] = None

        # Request query parameters
        query_parameters: Optional[ArtifactsRequestBuilder.ArtifactsRequestBuilderGetQueryParameters] = None

    
    @dataclass
    class ArtifactsRequestBuilderPostQueryParameters():
        """
        Creates a new artifact by posting the artifact content.  The body of the request shouldbe the raw content of the artifact.  This is typically in JSON format for *most* of the supported types, but may be in another format for a few (for example, `PROTOBUF`).The registry attempts to figure out what kind of artifact is being added from thefollowing supported list:* Avro (`AVRO`)* Protobuf (`PROTOBUF`)* JSON Schema (`JSON`)* Kafka Connect (`KCONNECT`)* OpenAPI (`OPENAPI`)* AsyncAPI (`ASYNCAPI`)* GraphQL (`GRAPHQL`)* Web Services Description Language (`WSDL`)* XML Schema (`XSD`)Alternatively, you can specify the artifact type using the `X-Registry-ArtifactType` HTTP request header, or include a hint in the request's `Content-Type`.  For example:```Content-Type: application/json; artifactType=AVRO```An artifact is created using the content provided in the body of the request.  Thiscontent is created under a unique artifact ID that can be provided in the requestusing the `X-Registry-ArtifactId` request header.  If not provided in the request,the server generates a unique ID for the artifact.  It is typically recommendedthat callers provide the ID, because this is typically a meaningful identifier, and for most use cases should be supplied by the caller.If an artifact with the provided artifact ID already exists, the default behavioris for the server to reject the content with a 409 error.  However, the caller cansupply the `ifExists` query parameter to alter this default behavior. The `ifExists`query parameter can have one of the following values:* `FAIL` (*default*) - server rejects the content with a 409 error* `UPDATE` - server updates the existing artifact and returns the new metadata* `RETURN` - server does not create or add content to the server, but instead returns the metadata for the existing artifact* `RETURN_OR_UPDATE` - server returns an existing **version** that matches the provided content if such a version exists, otherwise a new version is createdThis operation may fail for one of the following reasons:* An invalid `ArtifactType` was indicated (HTTP error `400`)* No `ArtifactType` was indicated and the server could not determine one from the content (HTTP error `400`)* Provided content (request body) was empty (HTTP error `400`)* An artifact with the provided ID already exists (HTTP error `409`)* The content violates one of the configured global rules (HTTP error `409`)* A server error occurred (HTTP error `500`)
        """
        # Used only when the `ifExists` query parameter is set to `RETURN_OR_UPDATE`, this parameter can be set to `true` to indicate that the server should "canonicalize" the content when searching for a matching version.  The canonicalization algorithm is unique to each artifact type, but typically involves removing extra whitespace and formatting the content in a consistent manner.
        canonical: Optional[bool] = None

        # Set this option to instruct the server on what to do if the artifact already exists.
        if_exists: Optional[str] = None

    
    @dataclass
    class ArtifactsRequestBuilderPostRequestConfiguration():
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        # Request headers
        headers: Optional[Dict[str, Union[str, List[str]]]] = None

        # Request options
        options: Optional[List[RequestOption]] = None

        # Request query parameters
        query_parameters: Optional[ArtifactsRequestBuilder.ArtifactsRequestBuilderPostQueryParameters] = None

    

