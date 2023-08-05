import asyncio
from abc import abstractmethod
from .grpc.translationContainerGRPC_pb2_grpc import TranslationContainerStub
from .grpc.translationContainerGRPC_pb2 import TrGenerateEncryptionKeysMessage, TrGenerateEncryptionKeysMessageResponse
from .grpc.translationContainerGRPC_pb2 import TrCustomMessageToMythicC2FormatMessage, \
    TrCustomMessageToMythicC2FormatMessageResponse
from .grpc.translationContainerGRPC_pb2 import TrMythicC2ToCustomMessageFormatMessage, \
    TrMythicC2ToCustomMessageFormatMessageResponse
import grpc.aio
from mythic_container.logging import logger
from .config import settings
import json


class TranslationContainer:
    """The base definition for a Translation Container Service.

    To have this hooked up to a Payload Type, you need to specify this service's name as the translation_container attribute in your Payload Type.

    This uses gRPC to connect to port 17444 on the Mythic Server.

    Attributes:
        name (str): The name of the translation container
        description (str): Description of the translation container to appear in Mythic's UI
        author (str): The author of the container

    Functions:
        to_json:
            return dictionary form of class
        generate_keys:
            A function for generating encryption/decryption keys based on provided C2 info
        translate_to_c2_format:
            A function for translating from Mythic's JSON format to a custom C2 format
        translate_from_c2_format:
            A function for translating from a custom C2 format to Mythic's JSON format

    """
    async def generate_keys(self, inputMsg: TrGenerateEncryptionKeysMessage) -> TrGenerateEncryptionKeysMessageResponse:
        response = TrGenerateEncryptionKeysMessageResponse(Success=False)
        response.Error = f"Not Implemented:\n{inputMsg}"

        return response

    async def translate_to_c2_format(self,
                                     inputMsg: TrMythicC2ToCustomMessageFormatMessage) -> TrMythicC2ToCustomMessageFormatMessageResponse:
        response = TrMythicC2ToCustomMessageFormatMessageResponse(Success=False)
        response.Error = f"Not Implemented:\n{inputMsg}"
        return response

    async def translate_from_c2_format(self,
                                       inputMsg: TrCustomMessageToMythicC2FormatMessage) -> TrCustomMessageToMythicC2FormatMessageResponse:
        response = TrCustomMessageToMythicC2FormatMessageResponse(Success=False)
        response.Error = f"Not Implemented:\n{inputMsg}"
        return response

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @property
    @abstractmethod
    def author(self):
        pass

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
        }

    def __str__(self):
        return json.dumps(self.to_json(), sort_keys=True, indent=2)


translationServices: dict[str, TranslationContainer] = {}


async def handleTranslationServices(tr_name: str):
    while True:
        try:
            logger.info(f"Attempting connection to gRPC for {tr_name}...")
            channel = grpc.aio.insecure_channel(
                f'{settings.get("mythic_server_host", "127.0.0.1")}:{settings.get("mythic_server_grpc_port", 17444)}')
            await channel.channel_ready()
            client = TranslationContainerStub(channel=channel)
            genKeys = handleGenerateKeys(tr_name, client)
            customToMythic = handleCustomToMythic(tr_name, client)
            mythicToCustom = handleMythicToCustom(tr_name, client)
            logger.info(f"[+] Successfully connected to gRPC for {tr_name}")
            await asyncio.gather(genKeys, customToMythic, mythicToCustom)
        except Exception as e:
            logger.exception(f"Translation gRPC services closed for {tr_name}: {e}")


async def handleGenerateKeys(tr_name: str, client):
    try:
        while True:
            stream = client.GenerateEncryptionKeys()
            await stream.write(TrGenerateEncryptionKeysMessageResponse(
                Success=True,
                TranslationContainerName=tr_name
            ))
            logger.info(f"Connected to gRPC for generating encryption keys for {tr_name}")
            async for request in stream:
                try:
                    result = await translationServices[tr_name].generate_keys(request)
                    result.TranslationContainerName = tr_name
                    await stream.write(result)
                except Exception as d:
                    logger.exception(f"Failed to process message:\n{d}")
                    await stream.write(TrGenerateEncryptionKeysMessageResponse(
                        Success=False,
                        TranslationContainerName=tr_name,
                        Error=f"Failed to process message:\n{d}"
                    ))
            logger.error(f"disconnected from gRPC for generating encryption keys for {tr_name}")
    except Exception as e:
        logger.exception(f"[-] exception in handleGenerateKeys for {tr_name}")


async def handleCustomToMythic(tr_name: str, client):
    try:
        while True:
            stream = client.TranslateFromCustomToMythicFormat()
            await stream.write(TrCustomMessageToMythicC2FormatMessageResponse(
                Success=True,
                TranslationContainerName=tr_name
            ))
            logger.info(f"Connected to gRPC for handling CustomC2 to MythicC2 Translations for {tr_name}")
            async for request in stream:
                try:
                    result = await translationServices[tr_name].translate_from_c2_format(request)
                    result.TranslationContainerName = tr_name
                    await stream.write(result)
                except Exception as d:
                    logger.exception(f"Failed to process message:\n{d}")
                    await stream.write(TrCustomMessageToMythicC2FormatMessageResponse(
                        Success=False,
                        TranslationContainerName=tr_name,
                        Error=f"Failed to process message:\n{d}"
                    ))
            logger.error(f"disconnected from gRPC for doing custom->mythic c2 for {tr_name}")
    except Exception as e:
        logger.exception(f"[-] exception in handleCustomToMythic for {tr_name}")


async def handleMythicToCustom(tr_name: str, client):
    try:
        while True:
            stream = client.TranslateFromMythicToCustomFormat()
            await stream.write(TrMythicC2ToCustomMessageFormatMessageResponse(
                Success=True,
                TranslationContainerName=tr_name
            ))
            logger.info(f"Connected to gRPC for handling MythicC2 to CustomC2 Translations for {tr_name}")
            async for request in stream:
                try:
                    result = await translationServices[tr_name].translate_to_c2_format(request)
                    result.TranslationContainerName = tr_name
                    await stream.write(result)
                except Exception as d:
                    logger.exception(f"Failed to process message:\n{d}")
                    await stream.write(TrMythicC2ToCustomMessageFormatMessageResponse(
                        Success=False,
                        TranslationContainerName=tr_name,
                        Error=f"Failed to process message:\n{d}"
                    ))
            logger.error(f"disconnected from gRPC for doing mythic->custom c2 for {tr_name}")
    except Exception as e:
        logger.exception(f"[-] exception in handleMythicToCustom for {tr_name}")
