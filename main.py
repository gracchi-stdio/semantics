import json
from platform import processor

from app.core.logger import logger
from app.config.settings import settings
from app.core.entities import DocumentMetadata, DocumentChunk
from app.services.markdown.processor import MarkdownProcessor


logger.info("This application settings are: %s", settings.model_dump_json())

def main():
    md_content = """
    # Chapter 1
    ## Section 1.1
    lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    # Chapter 2
    ## Section 2.1
    Hello, my name is Ewala. I come from the planet Alawe, in the galaxy Ewala, in the universe Alawe.
    But the point is I tried. If you think you need to go to the bakery, please do so now, because I do not want to be interrupted while I tell you my story. ...but anyway, I have been thinking about my happiness lately and have come to the conclusion that I am happy. This is annoying. If you saw a chicken as happy as me, I'll replace it, and give you a full refund... no questions asked!
    But that's not the point. The point is I am battery operated.
    Well, actually I am not.
    But that's not the point. What is the point?
    "The point is everyone should have my game and timetable! screamed someone who I subsequently smacked across the face and decapitated before sending him home in a cardboard box.
    Before I introduce myself, let me share with you a story. A story about me, and how great I am. But first, I think it would be appropriate to introduce myself. I am going to do this soon. So, it all started, in a smelly house, north of Wellington, south of Arizona and east of where you are sitting right now. It was a dark night, with no birds nor chickens, and it was raining a silent rain. There were too many stars to count, and not enough clouds to cover them. I like chickens. But anyway, what was I doing in this smelly house?
    "I was laughing at the boxes of dog food with you, remember!?" said Stevens grandma, but she was wrong. What was I doing? That's right, I was writing this story. Now back to the story.
    I needed to find something, so looked for it, and the most amazing thing happened!
    """
    _processor = MarkdownProcessor(

        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )

    metadata = DocumentMetadata(
        zotero_id="123456789",
        title="A Random Short Story",
        authors="Knth, kevin",
        tags="cs, algorhy",
    )

    chunks = _processor.process(md_content, metadata.model_dump())
    print("Chunks: ", chunks)


if __name__ == "__main__":
    main()

