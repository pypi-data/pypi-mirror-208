import asyncio

from django.http import Http404
from django.utils.decorators import classonlymethod

from core_models.api_response import SuccessApiResponse, \
    ServerErrorApiResponse, FailureApiResponse
from core_models.utils import log_exception
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView


class BaseListAPIView(ListAPIView):
    def list(self, request, *args, **kwargs):
        try:
            response = super(BaseListAPIView, self).list(
                request, *args, **kwargs)
            return SuccessApiResponse(
                "success",
                response.data
            )
        except NotFound:
            return FailureApiResponse("Page not found")
        except Exception as ex:
            log_exception(type(self).__name__, ex)
        return ServerErrorApiResponse()


class BaseCreateAPIView(CreateAPIView):

    def perform_create(self, serializer):
        self.object = serializer.save()

    def build_success(self) -> SuccessApiResponse:
        return SuccessApiResponse("Operation successful", None)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return self.build_success()
        except ValidationError as ex:
            return FailureApiResponse(
                "Operation could not be completed due to validation errors",
                ex.detail
            )
        except Exception as ex:
            log_exception(type(self).__name__, ex)
            return ServerErrorApiResponse()


class BaseUpdateAPIView(UpdateAPIView):

    def perform_update(self, serializer):
        self.object = serializer.save()

    def build_success(self) -> SuccessApiResponse:
        return SuccessApiResponse("Operation successful", None)

    def get_not_found_error(self):
        return "Data not found"

    def get_object(self):
        self.object = super().get_object()
        return self.object

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return self.build_success()
        except NotFound:
            return FailureApiResponse(self.get_not_found_error())
        except Http404:
            return FailureApiResponse(self.get_not_found_error())
        except ValidationError as ex:
            return FailureApiResponse(
                "Operation could not be completed due to validation errors",
                ex.detail
            )
        except Exception as ex:
            log_exception(type(self).__name__, ex)
            return ServerErrorApiResponse()

