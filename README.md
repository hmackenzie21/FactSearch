# FactSearch — Enhanced Fact-Checking Framework

**Images Here**

## Overview

FactSearch is an AI pipeline for verifying the factuality of LLM outputs. The pipeline comprises a four-step verification process:

1. Claim Extraction: Given an LLM-generated response, the system extracts atomic factual claims. 
2. Query Generation: For each extracted claim, the system generates search queries intended to retrieve relevant supporting or refuting evidence.
3. Evidence Retrieval: Evidence is retrieved using a locally-hosted instance of **SearXNG**, an open-source meta-search engine.
4. Claim Verification: For each claim, reteieved evidence snippets are provided to a language model for evidence-conditioned reasoning. The model outputs a factuality label along with explanatory reasoning. 


## How to use FactSearch

Users can interact with FactSearch either via the command line, or through the web-based GUI included in this repositary. 

### FactSearch GUI

