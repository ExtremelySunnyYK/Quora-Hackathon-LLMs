from __future__ import annotations

from typing import AsyncIterable
import logging
from fastapi_poe import PoeBot
from fastapi_poe.client import stream_request, MetaMessage
from fastapi_poe.types import (
    PartialResponse,
    QueryRequest,
    SettingsRequest,
    SettingsResponse,
)
import requests
from constants import *
import requests
import PyPDF2
from io import BytesIO

from dataclasses import dataclass
from typing import AsyncIterable

from fastapi_poe import PoeBot
from fastapi_poe.types import PartialResponse, QueryRequest
from huggingface_hub import AsyncInferenceClient
from huggingface_hub.inference._types import ConversationalOutput

logger = logging.getLogger("uvicorn.default")


class StudentOutreachBot(PoeBot):
    """This bot uses the HuggingFace Inference API.

    By default, it uses the HuggingFace public Inference API, but you can also
    use this class with a self hosted Inference Endpoint.
    For more information on how to create a self hosted endpoint, see:
    https://huggingface.co/blog/inference-endpoints

    Arguments:
        - model: either the name of the model (if you want to use the public API)
        or a link to your hosted inference endpoint.

    """

    def __init__(self) -> None:
        super().__init__()
        self.profile_details = {}
        self.target_pdf_url = ""
        self.target_pdf_text = ""

    async def get_response(
        self, request: QueryRequest
    ) -> AsyncIterable[PartialResponse]:
        previous_message = request.query[-1].content
        # Check if previous message contains "Details"
        if "Details" in previous_message:
            # Split the message by line
            split_message = previous_message.split("\n")
            # Remove the first and second line
            split_message.pop(0)
            split_message.pop(0)
            # Add the details to the profile details
            self.profile_details["name"] = split_message[0]
            self.profile_details["school"] = split_message[1]
            self.profile_details["year"] = split_message[2]
            self.profile_details["major"] = split_message[3]
            self.profile_details["description"] = split_message[4]

            yield PartialResponse(text="Thanks for your details! We will be using this to generate a personalised message for you! \n\n")

        if not self.checkDetails():
            yield PartialResponse(text=enter_details_text)
            return

        if len(request.query[-1].attachments) > 0:
            # Get the first attachment and check if attachment is type application/pdf
            if request.query[-1].attachments[-1].content_type != "application/pdf":
                yield PartialResponse(text="Please upload a new attachment in PDF format!")
                return
            self.target_pdf_url = request.query[-1].attachments[-1].url
            yield PartialResponse(text="Thanks for uploading the PDF!")

            yield PartialResponse(text="Please wait while we generate a personalised message for you!\n\n")
            yield PartialResponse(text="This might take a while!")

            self.parsePDF()
            prompt = self.generatePrompt()

            character_reply = ""
            request.query[-1].content = prompt
            request.query = [request.query[-1]]

            async for msg in stream_request(request, "GP4HelperOutreach", request.api_key):
                if isinstance(msg, MetaMessage):
                    continue
                if msg.is_suggested_reply:
                    yield self.suggested_reply_event(msg.text)
                elif msg.is_replace_response:
                    yield self.replace_response_event(msg.text)
                else:
                    character_reply += msg.text
                    # rendered_text = markdown_diff(prompt, character_reply)
                    yield self.replace_response_event(character_reply)

            return

        if self.checkDetails() and self.target_pdf_url == "":
            yield PartialResponse(text=attach_pdf_text)
            return

        else:
            async for msg in stream_request(request, "GP4HelperOutreach", request.api_key):
                yield msg.model_copy(update={"text": msg.text})

    async def get_settings(self, setting: SettingsRequest) -> SettingsResponse:
        return SettingsResponse(server_bot_dependencies={"GP4HelperOutreach": 1},
                                allow_attachments=True,
                                introduction_message=student_introduction_text
                                )

    def checkDetails(self):
        if len(self.profile_details) == 5:
            return True
        else:
            return False

    def parsePDF(self):
        """
        Parses the PDF from url into string
        """
        # Send a request to the URL
        response = requests.get(self.target_pdf_url)

        # Create a BytesIO object from the content of the response
        file = BytesIO(response.content)

        # Create a PDF file reader object
        pdf = PyPDF2.PdfReader(file)

        # Initialize a string to store all the text
        text = ''

        # Loop through each page in the PDF and extract the text
        for page_num in range(len(pdf.pages)):
            text += pdf.pages[page_num].extract_text()

        self.target_pdf_text = text
        return text

    def generatePrompt(self):
        """
        Generates the prompt for GPT-3
        """
        # Formatting the user details for better readability and personalization
        user_details_prompt = (f"Hello, I am {self.profile_details['name']}, currently in my {self.profile_details['year']} "
                               f"year at {self.profile_details['school']}, with a major in {self.profile_details['major']}. "
                               f"Here's a little about me: {self.profile_details['description']}")

        # Providing a clearer context of the target profile
        target_profile_prompt = (f"I am interested in connecting with an individual whose profile is: "
                                 f"{self.target_pdf_text}. My goal is to establish a connection and set up a meeting.")

        # Providing more specific instructions with a focus on the objectives
        instructions_prompt = """
        Based on the above data, please assist me with the following:

        1. Craft a personalized message (under 250 characters) that I can use to reach out to this individual.
        2. Develop a comprehensive strategy for successfully setting up a meeting with this person.

        Remember, the goal is to establish a meaningful connection that could potentially lead to professional opportunities.
        """

        prompt = user_details_prompt + target_profile_prompt + instructions_prompt

        return prompt
