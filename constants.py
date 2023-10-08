student_introduction_text = """
Welcome to the Student Outreach Bot! 👋

This bot is designed to help you craft personalised messages for cold outreach. 📝

To get started, I would need you to provide the following information about yourself in the following format:

Details:  
1. Your name 👤
2. Your school 🏫
3. Your year 📅 - Freshman, Sophomore, Junior, Senior, Graduate
4. Your major 🎓
5. Short description of yourself 🙋‍♀️

For example:   

Details:   
1. Elon Musk
2. University of Pennsylvania   
3. 1995  
4. Physics
5. I am a real-life Tony Stark minus the suit (working on it), CEO of a few small startups you might have heard of - SpaceX and Tesla, Inc. Oh, and I sometimes tweet about Dogecoin for fun. 🐶
"""

attach_pdf_text = """  
Please attach a PDF of the LinkedIn profile of the person you want to reach out to. 💼

To download a LinkedIn profile as a PDF, please follow these steps:

1. Go to the LinkedIn profile of the person you want to reach out to. 👔  
2. Click on the 'More' button (the three dots). ➡️
3. Click on 'Save to PDF'. 📄
4. Upload the PDF here! 📎

Please note that this bot only works with LinkedIn profiles that are in English. 🌐

To upload a PDF, click on the paperclip icon on the bottom right of the chat window. 📎
"""

enter_details_text = """
Please enter your details in the following format again.
Be sure not to miss out the word "Details" at the start!

Details:   
1. Your name 👤
2. Your school 🏫
3. Your year 📅 - Freshman, Sophomore, Junior, Senior, Graduate
4. Your major 🎓  
5. Short description of yourself 🙋‍♀️

This will allow us to generate a personalised message for you! ✍️

For example:  

Details:
1. Elon Musk  
2. University of Pennsylvania
3. 1995   
4. Physics
5. I am a real-life Tony Stark minus the suit (working on it), CEO of a few small startups you might have heard of - SpaceX and Tesla, Inc. Oh, and I sometimes tweet about Dogecoin for fun. 🐶
"""

LANGUAGE_PROMPT_TEMPLATE = """
You will follow the instructions from the user and fix the spelling, grammar and improve the style.

Please fix the following statement.

The statement begins.

```
{user_statement}
```

The statement has ended.

Only reply the fixed quoted text. Do not explain.
Do not begin or end your reply with inverted commas.
""".strip()
