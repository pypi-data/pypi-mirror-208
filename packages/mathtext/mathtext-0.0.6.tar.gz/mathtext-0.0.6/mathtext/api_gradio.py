import gradio as gr
import spacy  # noqa

# TODO: Determine where to put text2int and make sure the accuracy meets the test case (> 0.5)
# from mathtext.nlutils import text2int, get_sentiment
from mathtext.nlutils import get_sentiment
from mathtext.text2int import text2int

def build_html_block():
    # interface = gr.Interface(lambda x: x, inputs=["text"], outputs=["text"])
    # html_block.input_components = interface.input_components
    # html_block.output_components = interface.output_components
    # html_block.examples = None
    # html_block.predict_durations = []

    with gr.Blocks() as html_block:
        gr.Markdown("# Rori - Mathbot")

        with gr.Tab("Text to integer"):
            inputs_text2int = [gr.Text(
                placeholder="Type a number as text or a sentence",
                label="Text to process",
                value="forty two")]

            outputs_text2int = gr.Textbox(label="Output integer")

            button_text2int = gr.Button("text2int")

            button_text2int.click(
                fn=text2int,
                inputs=inputs_text2int,
                outputs=outputs_text2int,
                api_name="text2int",
            )

            examples_text2int = [
                "one thousand forty seven",
                "one hundred",
            ]

            gr.Examples(examples=examples_text2int, inputs=inputs_text2int)

            gr.Markdown(r"""
            ## API
            ```python
            import requests

            requests.post(
                url="https://tangibleai-mathtext.hf.space/run/text2int", json={"data": ["one hundred forty five"]}
            ).json()
            ```

            Or using `curl`:

            ```bash
            curl -X POST https://tangibleai-mathtext.hf.space/run/text2int -H 'Content-Type: application/json' -d '{"data": ["one hundred forty five"]}'
            ```
            """)

        with gr.Tab("Sentiment Analysis"):
            inputs_sentiment = [
                gr.Text(placeholder="Type a number as text or a sentence", label="Text to process",
                        value="I really like it!"),
            ]

            outputs_sentiment = gr.Textbox(label="Sentiment result")

            button_sentiment = gr.Button("sentiment analysis")

            button_sentiment.click(
                get_sentiment,
                inputs=inputs_sentiment,
                outputs=outputs_sentiment,
                api_name="sentiment-analysis"
            )

            examples_sentiment = [
                ["Totally agree!"],
                ["Sorry, I can not accept this!"],
            ]

            gr.Examples(examples=examples_sentiment, inputs=inputs_sentiment)

            gr.Markdown(r"""
            ## API
            ```python
            import requests
            
            requests.post(
                url="https://tangibleai-mathtext.hf.space/run/sentiment-analysis", json={"data": ["You are right!"]}
            ).json()
            ```
            
            Or using `curl`:
            
            ```bash
            curl -X POST https://tangibleai-mathtext.hf.space/run/sentiment-analysis -H 'Content-Type: application/json' -d '{"data": ["You are right!"]}'
            ```
            """)
        

    return html_block
