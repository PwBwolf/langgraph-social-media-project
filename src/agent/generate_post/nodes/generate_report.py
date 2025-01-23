from typing import Any, Dict
import re
from langchain_core.runnables import RunnableConfig

from src.agent.generate_post.configuration import Configuration
from src.agent.generate_post.generate_post_state import GeneratePostState
from src.shared.utils import load_chat_model

STRUCTURE_GUIDELINES = '''<part key="1">
This is the introduction and summary of the content. This must include key details such as:
- the name of the content/product/service.
- what the content/product/service does, and/or the problems it solves.
- unique selling points or interesting facts about the content.
- a high level summary of the content/product/service.
</part>

<part key="2">
This section should focus on how the content implements any of the business context outlined above. It should include:
- the product(s) or service(s) used in the content.
- how these products are used in the content.
- why these products are important to the application.
</part>

<part key="3">
This section should cover any additional details about the content that the first two parts missed. It should include:
- a detailed technical overview of the content.
- interesting facts about the content.
- any other relevant information that may be engaging to readers.
</part>'''

REPORT_RULES = '''- Focus on the subject of the content, and how it uses or relates to the business context outlined above.
- The final Tweet/LinkedIn post will be developer focused, so ensure the report is VERY technical and detailed.
- You should include ALL relevant details in the report, because doing this will help the final post be more informed, relevant and engaging.
- Include any relevant links found in the content in the report. These will be useful for readers to learn more about the content.
- Include details about what the product does, what problem it solves, and how it works. If the content is not about a product, you should focus on what the content is about instead of making it product focused.
- Use proper markdown styling when formatting the marketing report.
- Generate the report in English, even if the content submitted is not in English.'''

SYSTEM_PROMPT = f'''You are a highly regarded marketing employee.
You have been tasked with writing a marketing report on content submitted to you from a third party which uses your products.
This marketing report will then be used to craft Tweets and LinkedIn posts promoting the content and your products.

{{business_context}}

The marketing report should follow the following structure guidelines. It will be made up of three main sections outlined below:
<structure-guidelines>
{STRUCTURE_GUIDELINES}
</structure-guidelines>

Follow these rules and guidelines when generating the report:
<rules>
{REPORT_RULES}
</rules>

Lastly, you should use the following process when writing the report:
<writing-process>
- First, read over the content VERY thoroughly.
- Take notes, and write down your thoughts about the content after reading it carefully. These should be interesting insights or facts which you think you'll need later on when writing the final report. This should be the first text you write. ALWAYS perform this step first, and wrap the notes and thoughts inside opening and closing "<thinking>" tags.
- Finally, write the report. Use the notes and thoughts you wrote down in the previous step to help you write the report. This should be the last text you write. Wrap your report inside "<report>" tags. Ensure you ALWAYS WRAP your report inside the "<report>" tags, with an opening and closing tag.
</writing-process>

Do not include any personal opinions or biases in the report. Stick to the facts and technical details.
Your response should ONLY include the marketing report, and no other text.
Remember, the more detailed and engaging the report, the better!!
Finally, remember to have fun!

Given these instructions, examine the users input closely, and generate a detailed and thoughtful marketing report on it.'''

def parse_generation(generation: str) -> str:
    """Parse the LLM generation to extract the report from inside the <report> tag."""
    report_match = re.search(r'<report>([\s\S]*?)</report>', generation)
    if not report_match:
        print("Warning: Could not parse report from generation:\nSTART OF GENERATION\n\n",
              generation,
              "\n\nEND OF GENERATION")
        return generation
    return report_match.group(1).strip()

def format_report_prompt(page_contents: list[str]) -> str:
    """Format the page contents with indices for the prompt."""
    content_blocks = [
        f"<Content index={i + 1}>\n{content}\n</Content>"
        for i, content in enumerate(page_contents)
    ]
    return ("The following text contains summaries, or entire pages from the content I submitted to you. "
            "Please review the content and generate a report on it.\n"
            + "\n\n".join(content_blocks))

async def generate_content_report(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]:
    """Generate a report for the relevant content."""
    configuration = Configuration.from_runnable_config(config)
    
    business_context = configuration.business_context
    system_prompt = SYSTEM_PROMPT.format(business_context=business_context)
    
    chat_model = load_chat_model(configuration.report_model)
    
    prompt = format_report_prompt(state.page_contents)
    
    result = await chat_model.ainvoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])
    
    return {
        "report": parse_generation(result.content)
    } 