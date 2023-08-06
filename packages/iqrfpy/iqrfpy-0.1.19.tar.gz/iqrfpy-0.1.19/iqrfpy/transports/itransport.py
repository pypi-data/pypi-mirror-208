"""
Transport abstract class.

Serves as an abstract for communication channels.

Classes
-------
ITransport
"""
from abc import ABC, abstractmethod
from typing import Callable, Optional
from iqrfpy.irequest import IRequest
from iqrfpy.iresponse import IResponse
from iqrfpy.confirmation import Confirmation


class ITransport(ABC):
    """Abstract class providing interface for communication channels."""

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize transport and create a connection if applicable.

        Returns
        -------
        None
        """
        raise NotImplementedError("Abstract method not implemented.")

    @abstractmethod
    def terminate(self, force: bool = False) -> None:
        """
        Terminates transport.

        Parameters
        ----------
        force: Force terminate transport
        """
        raise NotImplementedError("Abstract method not implemented.")

    @abstractmethod
    def send(self, request: IRequest) -> None:
        """
        Serialize passed request to format acceptable by the communication channel and send request.

        Parameters
        ----------
        request: IRequest
            Request to send

        Returns
        -------
        None
        """
        raise NotImplementedError("Abstract method not implemented.")

    @abstractmethod
    def send_and_receive(self, request: IRequest, timeout: Optional[float] = None) -> IResponse:
        """
        Serialize request to format acceptable by the communication channel, send request and receive response synchronously.

        Parameters
        ----------
        request: IRequest
            Request to send
        timeout: Optional[float]
            Response receive timeout

        Returns
        -------
        response
            Received response
        """
        raise NotImplementedError("Abstract method not implemented.")

    @abstractmethod
    def receive(self, timeout: Optional[float] = None) -> IResponse:
        """
        Receive and return response synchronously.

        Parameters
        ----------
        timeout: Optional[float]
            Response receive timeout

        Returns
        -------
        response
            Received response
        """
        raise NotImplementedError("Abstract method not implemented.")

    @abstractmethod
    def confirmation(self) -> Confirmation:
        """
        Receive and return confirmation synchronously.

        Returns
        -------
        confirmation: Confirmation
            Confirmation object
        """
        raise NotImplementedError("Abstract method not implemented.")

    @abstractmethod
    def set_receive_callback(self, callback: Callable[[IResponse], None]) -> None:
        """
        Set callback to handle asynchronously received messages.

        Parameters
        ----------
        callback: Callable[[IResponse], None
            Function to call once a message has been received and successfully deserialized

        Returns
        -------
        None
        """
        raise NotImplementedError("Abstract method not implemented.")
