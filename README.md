# FactSearch — Enhanced Fact-Checking Framework

**Images Here**

## Overview

FactSearch is an AI pipeline for verifying the factuality of LLM outputs. The pipeline consists of a four-step verification process:

1. Claim Extraction: Given an LLM-generated response, the system extracts atomic factual claims. 
2. Query Generation: For each extracted claim, the system generates search queries intended to retrieve relevant supporting or refuting evidence.
3. Evidence Retrieval: Evidence is retrieved using a locally-hosted instance of **SearXNG**, an open-source meta-search engine.
4. Claim Verification: For each claim, reteieved evidence snippets are provided to a language model for evidence-conditioned reasoning. The model outputs a factuality label along with explanatory reasoning. 


## How to use FactSearch

Users can interact with FactSearch either via the command line, or through the web-based GUI included in this repositary. 

### FactSearch GUI

Upon loading the FactSearch app in a browser, users will be prompted to select an AI model which will be used for reasoning tasks within the verification pipeline. The OpenAI models that FactSearch currently supports are:

1. GPT-5 
2. GPT-5-mini
3. GPT-5.2 

To use any of these models, the user will also be required to input an OpenAI API key with sufficient tokens loaded to support FactSearch. As of February 2026, OpenAI considers GPT-5.2 it's flagship model, describing it as: 'The best model for coding and agentic tasks across industries'. 

For more info on OpenAI models: https://developers.openai.com/api/docs/models

Alternatively, users can choose to use the open-source model Ollama, in which case they will not require an API key and FactSearch will be completely free to use. 

Once FactSearch is initialised, users will be prompted for two inputs:

* Prompt/Question: Enter here the prompt that you passed to the LLM.
* Response to Check: Enter here the the LLM's response to your prompt. 

Once these two fields are filled, you can run the fact checking pipeline and your results will be ready to view within a moment. 

![FactSearch Input Panel](https://github.com/hmackenzie21/FactSearch/blob/working/images/input_panel.png)
