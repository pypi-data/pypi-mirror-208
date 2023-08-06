# Copied and modified from https://pypi.org/project/rdflib-endpoint/

import logging
import re
import arklog
import rdflib
from typing import Any, Dict, List, Optional, Union
from urllib import parse
from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse
from rdflib import ConjunctiveGraph, Dataset, Graph, Literal, URIRef
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.evaluate import evalPart
from rdflib.plugins.sparql.evalutils import _eval
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql.sparql import QueryContext, SPARQLError

from spendpoint import service

arklog.set_config_logging()


class SparqlEndpoint(FastAPI):
    """SPARQL endpoint for services and storage of heterogeneous data."""

    @staticmethod
    def is_json_mime_type(mime: str) -> bool:
        """"""
        return mime.split(",")[0] in ("application/sparql-results+json","application/json","text/javascript","application/javascript")

    @staticmethod
    def is_csv_mime_type(mime: str) -> bool:
        """"""
        return mime.split(",")[0] in ("text/csv", "application/sparql-results+csv")

    @staticmethod
    def is_xml_mime_type(mime: str) -> bool:
        """"""
        return mime.split(",")[0] in ("application/xml", "application/sparql-results+xml")

    @staticmethod
    def is_turtle_mime_type(mime: str) -> bool:
        """"""
        return mime.split(",")[0] in ("text/turtle",)

    async def requested_result_type(self, request: Request, operation: str) -> str:
        output_mime_type = request.headers["accept"]
        # TODO Ugly hack, fix later (Fuseki sends options)
        output_mime_type = output_mime_type.split(",")[0]
        if isinstance(output_mime_type, list):
            return output_mime_type[0]
        # TODO Use match or dict for this
        if not output_mime_type:
            logging.warning("No mime type provided. Setting mimetype to 'application/xml'.")
            return "application/xml"
        if operation == "Construct Query" and (self.is_json_mime_type(output_mime_type) or self.is_csv_mime_type(output_mime_type)):
            return "text/turtle"
        if operation == "Construct Query" and output_mime_type == "application/xml":
            return "application/rdf+xml"
        return output_mime_type

    def __init__(self, *args: Any, title: str, description: str, version: str, configuration, graph: Union[Graph, ConjunctiveGraph, Dataset] = ConjunctiveGraph(), **kwargs: Any):
        """"""
        self.graph = graph
        self.title = title
        self.description = description
        self.version = version
        self.configuration = configuration
        super().__init__(*args, title=title, description=description, version=version, **kwargs)
        logging.debug(self.description)
        rdflib.plugins.sparql.CUSTOM_EVALS["evalCustomFunctions"] = self.eval_custom_functions
        api_responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = {
            200: {
                "description": "SPARQL query results",
                "content": {
                    "application/sparql-results+json": {
                        "results": {"bindings": []},
                        "head": {"vars": []},
                    },
                    "application/json": {
                        "results": {"bindings": []},
                        "head": {"vars": []},
                    },
                    "text/csv": {"example": "s,p,o"},
                    "application/sparql-results+csv": {"example": "s,p,o"},
                    "text/turtle": {"example": "service description"},
                    "application/sparql-results+xml": {"example": "<root></root>"},
                    "application/xml": {"example": "<root></root>"},
                },
            },
            400: {
                "description": "Bad Request",
            },
            403: {
                "description": "Forbidden",
            },
            422: {
                "description": "Unprocessable Entity",
            },
        }

        @self.get("/", name="SPARQL endpoint", description="", responses=api_responses)
        async def sparql_endpoint_get(request: Request, query: Optional[str] = Query(None)) -> Response:
            logging.debug("Received GET request.")
            if not query:
                logging.warning("No query provided in GET request!")
                return JSONResponse({"error": "No query provided."})

            graph_ns = {}
            for prefix, ns_uri in self.graph.namespaces():
                graph_ns[prefix] = ns_uri

            try:
                parsed_query = prepareQuery(query, initNs=graph_ns)
                query_operation = re.sub(r"(\w)([A-Z])", r"\1 \2", parsed_query.algebra.name)
            except Exception as e:
                logging.error("Error parsing the SPARQL query: " + str(e))
                return JSONResponse(
                    status_code=400,
                    content={"message": "Error parsing the SPARQL query"},
                )

            try:
                query_results = self.graph.query(query, initNs=graph_ns)
            except Exception as e:
                logging.error("Error executing the SPARQL query on the RDFLib Graph: " + str(e))
                # TODO Send better error which can be parsed as a SPARQL response or check it client side
                return JSONResponse(
                    status_code=400,
                    content={"message": "Error executing the SPARQL query on the RDFLib Graph"},
                )
            output_mime_type = await self.requested_result_type(request, query_operation)
            logging.debug(f"Returning {output_mime_type}.")
            try:
                if self.is_csv_mime_type(output_mime_type):
                    return Response(query_results.serialize(format="csv"), media_type=output_mime_type)
                elif self.is_json_mime_type(output_mime_type):
                    return Response(query_results.serialize(format="json"), media_type=output_mime_type)
                elif self.is_xml_mime_type(output_mime_type):
                    return Response(query_results.serialize(format="xml"), media_type=output_mime_type)
                elif self.is_turtle_mime_type(output_mime_type):
                    return Response(query_results.serialize(format="turtle"), media_type=output_mime_type)
                return Response(query_results.serialize(format="xml"), media_type="application/sparql-results+xml")
            except Exception as e:
                logging.exception(e)
                return JSONResponse(status_code=400, content={"message": "Error executing the SPARQL query on the RDFLib Graph"})

        @self.post("/", name="SPARQL endpoint", description="", responses=api_responses)
        async def sparql_endpoint_post(request: Request, query: Optional[str] = Query(None)) -> Response:
            logging.debug("Received POST request.")
            if not query:
                # Handle federated query services which provide the query in the body
                query_body = await request.body()
                body = query_body.decode("utf-8")
                parsed_query = parse.parse_qsl(body)
                for params in parsed_query:
                    if params[0] == "query":
                        query = parse.unquote(params[1])
            return await sparql_endpoint_get(request, query)


    def eval_custom_functions(self, ctx: QueryContext, part: CompValue) -> List[Any]:
        if part.name != "Extend":
            raise NotImplementedError()

        query_results = []
        logging.debug("Custom evaluation.")
        for eval_part in evalPart(ctx, part.p):
            # Checks if the function is a URI (custom function)
            if hasattr(part.expr, "iri"):
                for conf_service in self.configuration.services:
                    # Check if URI correspond to a registered custom function
                    if part.expr.iri == URIRef(conf_service.namespace):
                        query_results, ctx, part, eval_part = getattr(service, conf_service.call)(query_results, ctx, part, eval_part, conf_service)
            else:
                # For built-in SPARQL functions (that are not URIs)
                evaluation: List[Any] = [_eval(part.expr, eval_part.forget(ctx, _except=part._vars))]
                if isinstance(evaluation[0], SPARQLError):
                    raise evaluation[0]
                # Append results for built-in SPARQL functions
                for result in evaluation:
                    query_results.append(eval_part.merge({part.var: Literal(result)}))
        return query_results
