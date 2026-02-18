# FactSearch — Enhanced Fact-Checking Framework

**Images Here**

## Overview

FactSearch is an AI pipeline for verifying the factuality of LLM outputs. The pipeline consists of a four-step verification process:

1. Claim Extraction: Given an LLM-generated response, the system extracts atomic factual claims. 
2. Query Generation: For each extracted claim, the system generates search queries intended to retrieve relevant supporting or refuting evidence.
3. Evidence Retrieval: Evidence is retrieved using a locally-hosted instance of **SearXNG**, an open-source meta-search engine.
4. Claim Verification: For each claim, reteieved evidence snippets are provided to a language model for evidence-conditioned reasoning. 

The pipeline outputs binary claim verification labels (True/False), alongside explanatory reasoning for each decision. Additionally, users can access source links retrieved via SearXNG - some examples of commonly occuring sources are: Wikipedia, online newspaper articles, independent media publications, government/public-sector webpages (e.g. NHS pages for healthcare-related information), scholarly articles, and technical documentation. The nature of the sources used will vary depending on the information which the user inputs to the pipeline. 

Users can also export their results in .txt or JSON format.

## AI Safety Disclaimer

FactSearch is a research project aimed at improving AI transparency and safety for decision-making scenarios. Ultimately, even when fact-checking tools such as FactSearch are used, it is still important that a human checks and verifies all LLM-generated information before influencing any important decisions.

## How to use FactSearch

Users can interact with FactSearch either via the command line, or through the web-based GUI included in this repositary. 

### Instillation & Quick-Start

### FactSearch GUI

Upon loading the FactSearch app in a browser, users will be prompted to select an AI model which will be used for reasoning tasks within the verification pipeline. The OpenAI models that FactSearch currently supports are:

1. GPT-5 
2. GPT-5-mini
3. GPT-5.2 

To use any of these models, the user will also be required to input an OpenAI API key with sufficient tokens loaded to support FactSearch. For optimal performance, we recommend using GPT-5.2, OpenAI's flagship model as of February 2026. 

For more info on OpenAI models: https://developers.openai.com/api/docs/models

Alternatively, users can choose to use the open-source model Ollama, in which case they will not require an API key and FactSearch will be completely free to use. 

Once FactSearch is initialised, users will be prompted for two inputs:

* Prompt/Question: Enter here the prompt that you passed to the LLM.
* Response to Check: Enter here the the LLM's response to your prompt. 

![FactSearch Input Panel](https://github.com/hmackenzie21/FactSearch/blob/working/images/input_panel.png)

Once these fields have been filled, you will be able to use the button within the panel to run the fact checking pipeline and your results will be available within a few moments. 

### Interpreting Results and Reviewing Sources

FactSearch enables users to view factuality on a claim-by-claim basis, in addition to 

## SearXNG Configuration and Language Model Selection
Search engine configuration and effects of search engine blocks on the system, built in mitigation measures (XNG wrapper pausing) - maybe add this into the app?? 
OpenAI model selection + thoughts on relative model performance (mention temperature needing to be set to 1)
Additional NLP model integration (OLlama probably)


## Credits and references